"""
SnowLuma 适配器核心模块

SnowLuma 是面向 NTQQ（QQ 桌面客户端）的远程协议框架，通过 hook 注入 QQ 进程，
以 OneBot v11 协议暴露 API。本适配器连接 SnowLuma 后端，提供完整的消息收发、
ApiDSL、事件转换及 SnowLuma 扩展功能（QQ空间/群相册/群文件等）。

{!--< tips >!--}
1. 基于 OneBot v11 协议，支持四种连接模式：client(正向WS) / server(反向WS) /
   http(HTTP API + 事件轮询) / webhook(HTTP API + 事件上报)
2. 支持多账户，默认端口 3001（WS）/ 3000（HTTP）
3. 自动识别 bot_id（QQ 号），event.reply() 无需手动指定账户
4. 提供 OB12 标准 ApiDSL（自动映射 OB11 动作名）+ SnowLuma 扩展便捷方法
5. OB11 协议扩展（NapCat/go-cqhttp 兼容）通过 Api.call("action_name", ...) 直接调用
{!--< /tips >!--}
"""

import asyncio
import base64 as _base64
import itertools
import json
import os
import warnings
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union

import filetype
from ErisPulse.Core import client, router
from ErisPulse.Core.Bases import BaseConfig, BotAccountConfig
from ErisPulse.Core.Bases.adapter import BaseAdapter, RequestDSL
from ErisPulse.Core.Bases.websocket import WSMessage

try:
    from ErisPulse.runtime.tasks import spawn_background
except ImportError:  # pragma: no cover
    spawn_background = None

__version__ = "0.1.0"

# 软依赖的框架最低版本（运行时检测，仅提示不强制）
MIN_FRAMEWORK_VERSION = (2, 7, 1)

from .i18n import SnowLumaI18n
from .ob11_extensions import OB11ExtensionApi


def _forward_node_text(node: Dict) -> str:
    """提取合并转发节点 content 中全部 text 段文本（段间直接连接）"""
    data = node.get("data") or {}
    return "".join(
        str(seg.get("data", {}).get("text") or "")
        for seg in (data.get("content") or [])
        if isinstance(seg, dict) and seg.get("type") == "text"
    )


def _forward_nodes_plain(nodes, separator: str = "\n") -> str:
    """合并转发节点降级纯文本：每条「昵称: 正文」"""
    lines = []
    for node in nodes if isinstance(nodes, list) else [nodes]:
        if not isinstance(node, dict):
            continue
        data = node.get("data") or {}
        nickname = str(data.get("nickname") or "").strip()
        text = _forward_node_text(node).strip()
        if nickname and text:
            lines.append(f"{nickname}: {text}")
        elif text:
            lines.append(text)
    return separator.join(lines)


def _deprecation_warning(old_method: str, new_method: str):
    """Send 查询类方法的废弃提示（软提示，不改变行为）"""
    msg = f"Send.{old_method}() 已废弃，推荐使用 {new_method} 替代"
    warnings.warn(msg, DeprecationWarning, stacklevel=3)
    try:
        from ErisPulse.Core import logger

        logger.debug(msg)
    except Exception:
        pass


@dataclass
class SnowLumaGlobalConfig(BaseConfig):
    """SnowLuma 适配器全局配置"""

    pass


@dataclass
class SnowLumaAccountConfig(BotAccountConfig):
    """
    SnowLuma 账户配置

    SnowLuma 默认服务端口：HTTP 3000、WS 3001。
    四种连接模式：client(正向WS) / server(反向WS) / http(HTTP API+事件轮询) /
    webhook(HTTP API+事件上报)，覆盖 OneBot 11 全部连接方式。
    """

    mode: str = field(
        default="client",
        metadata={
            "description": {"i18n": "SnowLuma_Adapter.mode", "default": "连接模式: server(反向WS) / client(正向WS) / http(HTTP API+轮询) / webhook(HTTP API+上报)"},
            "required": False,
            "ui": {
                "widget": "select",
                "group": "connection",
                "order": 2,
                "options": [
                    {"label": {"i18n": "SnowLuma_Adapter.mode_server", "default": "Server"}, "value": "server"},
                    {"label": {"i18n": "SnowLuma_Adapter.mode_client", "default": "Client"}, "value": "client"},
                    {"label": {"i18n": "SnowLuma_Adapter.mode_http", "default": "HTTP"}, "value": "http"},
                    {"label": {"i18n": "SnowLuma_Adapter.mode_webhook", "default": "Webhook"}, "value": "webhook"},
                ],
            },
        },
    )
    url: Optional[str] = field(
        default="ws://127.0.0.1:3001",
        metadata={
            "description": {"i18n": "SnowLuma_Adapter.url", "default": "Client模式 WebSocket 地址（SnowLuma 默认: ws://127.0.0.1:3001）"},
            "required": False,
            "ui": {
                "widget": "text",
                "group": "client",
                "order": 3,
                "show_if": {"field": "mode", "op": "eq", "value": "client"},
            },
        },
    )
    token: Optional[str] = field(
        default="",
        metadata={
            "description": {"i18n": "SnowLuma_Adapter.token", "default": "访问令牌（Bearer 认证）"},
            "required": False,
            "secret": True,
            "ui": {"widget": "password", "group": "connection", "order": 4},
        },
    )
    server_path: Optional[str] = field(
        default="/",
        metadata={
            "description": {"i18n": "SnowLuma_Adapter.server_path", "default": "Server模式 WebSocket 路径"},
            "required": False,
            "ui": {
                "widget": "text",
                "group": "server",
                "order": 5,
                "show_if": {"field": "mode", "op": "eq", "value": "server"},
            },
        },
    )
    http_url: Optional[str] = field(
        default="http://127.0.0.1:3000",
        metadata={
            "description": {"i18n": "SnowLuma_Adapter.http_url", "default": "HTTP API 地址（http/webhook 模式调用动作使用，SnowLuma 默认: http://127.0.0.1:3000）"},
            "required": False,
            "ui": {
                "widget": "text",
                "group": "http",
                "order": 6,
                "show_if": {"field": "mode", "op": "in", "value": ["http", "webhook"]},
            },
        },
    )
    poll_interval: Optional[float] = field(
        default=1.0,
        metadata={
            "description": {"i18n": "SnowLuma_Adapter.poll_interval", "default": "HTTP模式事件轮询间隔（秒），0 表示纯 API 模式不拉取事件"},
            "required": False,
            "ui": {
                "widget": "number",
                "min": 0,
                "step": 0.5,
                "group": "http",
                "order": 7,
                "show_if": {"field": "mode", "op": "in", "value": ["http", "webhook"]},
            },
        },
    )
    webhook_path: Optional[str] = field(
        default="/events",
        metadata={
            "description": {"i18n": "SnowLuma_Adapter.webhook_path", "default": "Webhook模式接收事件上报的路径（最终路由为 /snowluma_{account}{path}，支持 {account} 占位符）"},
            "required": False,
            "ui": {
                "widget": "text",
                "group": "webhook",
                "order": 8,
                "show_if": {"field": "mode", "op": "eq", "value": "webhook"},
            },
        },
    )


SnowLumaGlobalConfig._schema_meta = {
    "group_labels": {
        "connection": {"i18n": "SnowLuma_Adapter.group_connection", "default": "连接设置"},
        "server": {"i18n": "SnowLuma_Adapter.group_server", "default": "服务端模式"},
        "client": {"i18n": "SnowLuma_Adapter.group_client", "default": "客户端模式"},
        "http": {"i18n": "SnowLuma_Adapter.group_http", "default": "HTTP 模式"},
        "webhook": {"i18n": "SnowLuma_Adapter.group_webhook", "default": "Webhook 模式"},
    }
}


class SnowLumaAdapter(BaseAdapter):
    """
    SnowLuma 协议适配器

    连接 SnowLuma 后端（NTQQ hook），使用 OneBot v11 协议进行通信。
    SnowLuma 的 API 全面向 NapCat 对齐，本适配器同样可直接连接 NapCat 后端
    （client 模式指向 NapCat forward WS，或 server 模式接收 NapCat 反向 WS）。
    提供 OB12 标准 ApiDSL 动作 + SnowLuma 109 个扩展动作。

    {!--< tips >!--}
    1. 四种连接模式：client(正向WS) / server(反向WS) / http(HTTP API+事件轮询) / webhook(HTTP API+事件上报)
    2. 自动识别 bot_id（QQ 号），event.reply() 自动路由
    3. ApiDSL 自动映射 OB12 标准动作到 OB11 动作名
    4. SnowLuma/NapCat 共享扩展通过 Send 便捷方法或 Api.call("action_name") 调用（NapCat/SnowLuma 通用）
    {!--< /tips >!--}
    """

    ConfigClass = SnowLumaGlobalConfig
    AccountConfigClass = SnowLumaAccountConfig
    I18nClass = SnowLumaI18n

    class EventMixin:
        """
        SnowLuma 平台事件扩展方法
        """

        def get_raw_event(self) -> dict:
            """获取 SnowLuma 原始事件数据（snowluma_raw）"""
            return self.get("snowluma_raw", {}) or {}

        def get_raw_self_id(self) -> str:
            """获取原始 self_id（Bot 的 QQ 号）"""
            return self.get("self", {}).get("user_id", "")

        def get_sender_info(self) -> dict:
            """获取完整的发送者信息"""
            return self.get("snowluma_raw", {}).get("sender", {})

        def get_sender_role(self) -> str:
            """获取发送者在群内的角色（owner/admin/member）"""
            return self.get("snowluma_raw", {}).get("sender", {}).get("role", "")

        def get_sender_level(self) -> int:
            """获取发送者等级"""
            return self.get("snowluma_raw", {}).get("sender", {}).get("level", 0)

        def get_sender_title(self) -> str:
            """获取发送者群头衔"""
            return self.get("snowluma_raw", {}).get("sender", {}).get("title", "")

        def is_system_message(self) -> bool:
            """判断是否为系统消息"""
            return self.get("sub_type") == "system"

    class Api(BaseAdapter.Api, OB11ExtensionApi):
        """
        SnowLuma 标准 API 动作实现（ApiDSL）

        复用 OB11 动作名映射，SnowLuma 原生支持所有 OB11 标准动作。
        混入 OB11ExtensionApi 提供 NapCat/SnowLuma 兼容扩展动作的类型化方法。

        {!--< tips >!--}
        1. get_self_info → get_login_info（字段标准化）
        2. get_user_info → get_stranger_info（字段标准化）
        3. delete_message → delete_msg（动作名映射）
        4. leave_group → set_group_leave（动作名映射）
        5. upload_file 扩展了 group_id/user_id 参数
        6. OB11 协议扩展（send_poke/get_group_msg_history 等）通过 call("action_name", ...) 直接调用（NapCat/SnowLuma 通用）
        {!--< /tips >!--}
        """

        async def get_self_info(self) -> dict:
            raw = await self._adapter.call_api(
                "get_login_info", _account_id=self._account_id
            )
            if raw.get("status") != "ok":
                return raw
            data = raw.get("data", {}) or {}
            user_id = str(data.get("user_id", ""))
            user_name = data.get("nickname", "")
            return self._adapter.make_response(
                data={
                    "user_id": user_id,
                    "user_name": user_name,
                    "user_displayname": user_name,
                },
                raw=raw.get("snowluma_raw", raw),
            )

        async def get_user_info(self, user_id: str) -> dict:
            raw = await self._adapter.call_api(
                "get_stranger_info",
                _account_id=self._account_id,
                user_id=int(user_id),
            )
            if raw.get("status") != "ok":
                return raw
            data = raw.get("data", {}) or {}
            return self._adapter.make_response(
                data={
                    "user_id": str(data.get("user_id", user_id)),
                    "user_name": data.get("nickname", ""),
                    "user_displayname": data.get("nickname", ""),
                    "user_remark": "",
                },
                raw=raw.get("snowluma_raw", raw),
            )

        async def delete_message(self, message_id: str) -> dict:
            return await self._adapter.call_api(
                "delete_msg",
                _account_id=self._account_id,
                message_id=int(message_id),
            )

        async def leave_group(self, group_id: str) -> dict:
            return await self._adapter.call_api(
                "set_group_leave",
                _account_id=self._account_id,
                group_id=int(group_id),
            )

        async def upload_file(
            self,
            *,
            type: str,
            name: str,
            url: str | None = None,
            path: str | None = None,
            data: bytes | None = None,
            headers: dict[str, str] | None = None,
            sha256: str | None = None,
            group_id: str | None = None,
            user_id: str | None = None,
        ) -> dict:
            if not group_id and not user_id:
                return self._adapter.make_error(
                    retcode=10003,
                    message="SnowLuma 上传文件需指定 group_id 或 user_id",
                )

            try:
                if type == "data":
                    if data is None:
                        return self._adapter.make_error(
                            retcode=10003, message="type=data 时必须提供 data"
                        )
                    file_bytes = data
                elif type == "path":
                    if not path:
                        return self._adapter.make_error(
                            retcode=10003, message="type=path 时必须提供 path"
                        )
                    with open(path, "rb") as f:
                        file_bytes = f.read()
                elif type == "url":
                    if not url:
                        return self._adapter.make_error(
                            retcode=10003, message="type=url 时必须提供 url"
                        )
                    resp = await client.get(url, headers=headers or {}, timeout=300)
                    file_bytes = await resp.read()
                else:
                    return self._adapter.make_error(
                        retcode=10003, message=f"不支持的 type: {type}"
                    )
            except Exception as e:
                return self._adapter.make_error(
                    retcode=10003, message=f"读取文件失败: {e}"
                )

            try:
                sample = file_bytes[:1024] if file_bytes else b""
                info = filetype.guess(sample) if sample else None
                mime = info.mime if info else ""
            except Exception:
                mime = ""

            self._adapter.logger.debug(
                f"upload_file: name={name}, mime={mime}, size={len(file_bytes)}"
            )

            file_b64 = _base64.b64encode(file_bytes).decode("ascii")
            file_param = f"base64://{file_b64}"

            if group_id:
                return await self._adapter.call_api(
                    "upload_group_file",
                    _account_id=self._account_id,
                    group_id=int(group_id),
                    file=file_param,
                    name=name,
                )
            else:
                return await self._adapter.call_api(
                    "upload_private_file",
                    _account_id=self._account_id,
                    user_id=int(user_id),
                    file=file_param,
                    name=name,
                )

    class Send(BaseAdapter.Send):
        """
        SnowLuma 消息发送 DSL

        包含标准 OB11 消息发送 + SnowLuma 扩展便捷方法（QQ空间/拍一拍/群文件等）。

        {!--< tips >!--}
        1. 所有发送方法返回 asyncio.Task 对象
        2. 消息段自动经过修饰器处理和 OB12→OB11 格式转换
        3. OB11 协议扩展通过 Send 便捷方法或 Api.call("action_name") 直接调用（不加平台前缀，NapCat/SnowLuma 通用）
        {!--< /tips >!--}
        """

        def _build_ob11_message(self, message: Union[str, List[Dict]]) -> List[Dict]:
            if isinstance(message, str):
                segments = [{"type": "text", "data": {"text": message}}]
            else:
                segments = list(message)
            segments = self._apply_modifiers(segments)
            segments = self._convert_ob12_to_ob11(segments)
            self._insert_text_separators(segments)
            return segments

        def _insert_text_separators(self, message_list: List[Dict]):
            result = []
            for i, segment in enumerate(message_list):
                seg_type = segment.get("type", "")
                result.append(segment)
                if i < len(message_list) - 1:
                    next_seg = message_list[i + 1]
                    next_type = next_seg.get("type", "")
                    if seg_type == "text" and next_type == "text":
                        result.append({"type": "text", "data": {"text": " "}})
                    elif seg_type == "at" and next_type == "text":
                        next_text = next_seg.get("data", {}).get("text", "")
                        if next_text and not next_text.startswith(" "):
                            result.append({"type": "text", "data": {"text": " "}})
                    elif seg_type == "text" and next_type == "at":
                        current_text = segment.get("data", {}).get("text", "")
                        if current_text and not current_text.endswith(" "):
                            result.append({"type": "text", "data": {"text": " "}})
            message_list.clear()
            message_list.extend(result)

        def _file_to_base64(self, file: Union[str, bytes]) -> str:
            if isinstance(file, bytes):
                return "base64://" + _base64.b64encode(file).decode("ascii")
            elif isinstance(file, str) and not file.startswith("base64://"):
                with open(os.path.abspath(file), "rb") as f:
                    return "base64://" + _base64.b64encode(f.read()).decode("ascii")
            return file

        def Text(self, text: str):
            return self.Raw_ob12([{"type": "text", "data": {"text": text}}])

        def Image(self, file: Union[str, bytes], filename: str = "image.png"):
            file = self._file_to_base64(file)
            return self.Raw_ob12(
                [{"type": "image", "data": {"file": file, "file_name": filename}}]
            )

        def Voice(self, file: Union[str, bytes], filename: str = "voice.amr"):
            file = self._file_to_base64(file)
            return self.Raw_ob12(
                [{"type": "audio", "data": {"file": file, "file_name": filename}}]
            )

        def Video(self, file: Union[str, bytes], filename: str = "video.mp4"):
            file = self._file_to_base64(file)
            return self.Raw_ob12(
                [{"type": "video", "data": {"file": file, "file_name": filename}}]
            )

        def Face(self, id: Union[str, int]):
            return self.Raw_ob12([{"type": "face", "data": {"id": str(id)}}])

        def File(self, file: Union[str, bytes], filename: str = "file.dat"):
            file = self._file_to_base64(file)
            return self.Raw_ob12(
                [{"type": "file", "data": {"file": file, "file_name": filename}}]
            )

        def Raw_ob12(self, message, **kwargs):
            if isinstance(message, dict):
                message = [message]

            # node 段解析：纯 node 列表自动路由合并转发；混合列表降级为纯文本
            if message and all(
                isinstance(seg, dict) and seg.get("type") == "node" for seg in message
            ):
                return asyncio.create_task(
                    self._do_send_forward([seg for seg in message], **kwargs)
                )
            message = [
                {"type": "text", "data": {"text": _forward_nodes_plain(seg)}}
                if isinstance(seg, dict) and seg.get("type") == "node"
                else seg
                for seg in message
            ]

            ob11_message = self._build_ob11_message(message)

            async def _do_send():
                return await self._adapter.call_api(
                    endpoint="send_msg",
                    _account_id=self._account_id,
                    message_type="private" if self._target_type == "user" else "group",
                    user_id=int(self._target_id) if self._target_type == "user" else None,
                    group_id=int(self._target_id) if self._target_type == "group" else None,
                    message=ob11_message,
                    **kwargs,
                )

            return asyncio.create_task(_do_send())

        def MergeForward(self, nodes, title: str = "合并聊天记录"):
            """发送合并转发消息（SnowLuma / NapCat 后端通用）

            三级回退：① OB11 扩展专用端点（send_group/private_forward_msg，NapCat 原生，
            SnowLuma 兼容）→ ② upload_forward_msg 取 resid 再以 forward 段发送（SnowLuma
            扩展链路）→ ③ send_msg 直发 node 段；全部失败返回标准失败响应，
            调用方会自动回退纯文本，内容不丢。

            :param nodes: go-cqhttp 扩展的 OneBot v11 合并转发节点数组（或单节点 dict）
            :param title: 保留参数（原生合并转发卡片标题由节点内容决定，此处不使用）
            :return: asyncio.Task
            """
            if isinstance(nodes, dict):
                nodes = [nodes]
            return asyncio.create_task(
                self._do_send_forward([n for n in nodes if isinstance(n, dict)])
            )

        async def _do_send_forward(self, nodes, **kwargs):
            is_private = self._target_type == "user"
            endpoint = (
                "send_private_forward_msg" if is_private else "send_group_forward_msg"
            )
            target = {
                "message_type": "private" if is_private else "group",
                "user_id": int(self._target_id) if is_private else None,
                "group_id": None if is_private else int(self._target_id),
            }
            # ① 专用端点（NapCat 原生；NapCat 对 send_msg 携带 node 段会拒绝 retcode 1400）
            try:
                result = await self._adapter.call_api(
                    endpoint=endpoint,
                    _account_id=self._account_id,
                    messages=nodes,
                    **target,
                    **kwargs,
                )
                if not (
                    isinstance(result, dict)
                    and str(result.get("status") or "") == "failed"
                ):
                    return result
            except Exception:
                pass
            # ② SnowLuma 扩展链路：上传节点取 resid → forward 段发送
            try:
                upload = await self._adapter.call_api(
                    endpoint="upload_forward_msg",
                    _account_id=self._account_id,
                    messages=nodes,
                )
                resid = None
                if isinstance(upload, dict) and str(upload.get("status") or "") != "failed":
                    data = upload.get("data") or {}
                    if isinstance(data, dict):
                        resid = data.get("resid") or data.get("id")
                if resid:
                    result = await self._adapter.call_api(
                        endpoint="send_msg",
                        _account_id=self._account_id,
                        message=[{"type": "forward", "data": {"id": str(resid)}}],
                        **target,
                        **kwargs,
                    )
                    if not (
                        isinstance(result, dict)
                        and str(result.get("status") or "") == "failed"
                    ):
                        return result
            except Exception:
                pass
            # ③ 回退：send_msg 直发 node 段
            return await self._adapter.call_api(
                endpoint="send_msg",
                _account_id=self._account_id,
                message=nodes,
                **target,
                **kwargs,
            )

        def Recall(self, message_id: Union[str, int]):
            return asyncio.create_task(
                self._adapter.call_api(
                    endpoint="delete_msg",
                    _account_id=self._account_id,
                    message_id=int(message_id),
                )
            )

        def Kick(self, user_id: Union[str, int], reject_add_request: bool = False):
            return asyncio.create_task(
                self._adapter.call_api(
                    endpoint="set_group_kick",
                    _account_id=self._account_id,
                    group_id=int(self._target_id),
                    user_id=int(user_id),
                    reject_add_request=reject_add_request,
                )
            )

        def Ban(self, user_id: Union[str, int], duration: int = 1800):
            return asyncio.create_task(
                self._adapter.call_api(
                    endpoint="set_group_ban",
                    _account_id=self._account_id,
                    group_id=int(self._target_id),
                    user_id=int(user_id),
                    duration=duration,
                )
            )

        def WholeBan(self, enable: bool = True):
            return asyncio.create_task(
                self._adapter.call_api(
                    endpoint="set_group_whole_ban",
                    _account_id=self._account_id,
                    group_id=int(self._target_id),
                    enable=enable,
                )
            )

        def SetAdmin(self, user_id: Union[str, int], enable: bool = True):
            return asyncio.create_task(
                self._adapter.call_api(
                    endpoint="set_group_admin",
                    _account_id=self._account_id,
                    group_id=int(self._target_id),
                    user_id=int(user_id),
                    enable=enable,
                )
            )

        def SetCard(self, user_id: Union[str, int], card: str = ""):
            return asyncio.create_task(
                self._adapter.call_api(
                    endpoint="set_group_card",
                    _account_id=self._account_id,
                    group_id=int(self._target_id),
                    user_id=int(user_id),
                    card=card,
                )
            )

        def SetGroupName(self, name: str):
            return asyncio.create_task(
                self._adapter.call_api(
                    endpoint="set_group_name",
                    _account_id=self._account_id,
                    group_id=int(self._target_id),
                    group_name=name,
                )
            )

        def Leave(self, is_dismiss: bool = False):
            return asyncio.create_task(
                self._adapter.call_api(
                    endpoint="set_group_leave",
                    _account_id=self._account_id,
                    group_id=int(self._target_id),
                    is_dismiss=is_dismiss,
                )
            )

        def SetTitle(self, user_id: Union[str, int], title: str = ""):
            return asyncio.create_task(
                self._adapter.call_api(
                    endpoint="set_group_special_title",
                    _account_id=self._account_id,
                    group_id=int(self._target_id),
                    user_id=int(user_id),
                    special_title=title,
                )
            )

        def SetPortrait(self, file: Union[str, bytes]):
            file = self._file_to_base64(file)
            return asyncio.create_task(
                self._adapter.call_api(
                    endpoint="set_group_portrait",
                    _account_id=self._account_id,
                    group_id=int(self._target_id),
                    file=file,
                )
            )

        def Like(self, user_id: Union[str, int], times: int = 1):
            """发送好友赞（最大 10 次）"""
            return asyncio.create_task(
                self._adapter.call_api(
                    endpoint="send_like",
                    _account_id=self._account_id,
                    user_id=int(user_id),
                    times=times,
                )
            )

        # ==================== 已废弃的查询方法（推荐使用 Api DSL） ====================

        def GetMsg(self, message_id: Union[str, int]):
            """[已废弃] 获取消息内容，推荐使用 Api.call('get_msg', ...)"""
            _deprecation_warning("GetMsg", "Api.call('get_msg', ...)")
            return asyncio.create_task(
                self._adapter.call_api(
                    endpoint="get_msg",
                    _account_id=self._account_id,
                    message_id=int(message_id),
                )
            )

        def GetForwardMsg(self, id: Union[str, int]):
            """[已废弃] 获取合并转发消息，推荐使用 Api.call('get_forward_msg', ...)"""
            _deprecation_warning("GetForwardMsg", "Api.call('get_forward_msg', ...)")
            return asyncio.create_task(
                self._adapter.call_api(
                    endpoint="get_forward_msg",
                    _account_id=self._account_id,
                    id=str(id),
                )
            )

        def GetLoginInfo(self):
            """[已废弃] 获取登录号信息，推荐使用 Api.get_self_info()"""
            _deprecation_warning("GetLoginInfo", "Api.get_self_info()")
            return asyncio.create_task(
                self._adapter.call_api(
                    endpoint="get_login_info",
                    _account_id=self._account_id,
                )
            )

        def GetFriendList(self):
            """[已废弃] 获取好友列表，推荐使用 Api.get_friend_list()"""
            _deprecation_warning("GetFriendList", "Api.get_friend_list()")
            return asyncio.create_task(
                self._adapter.call_api(
                    endpoint="get_friend_list",
                    _account_id=self._account_id,
                )
            )

        def GetGroupInfo(self):
            """[已废弃] 获取群信息，推荐使用 Api.get_group_info(group_id)"""
            _deprecation_warning("GetGroupInfo", "Api.get_group_info(group_id)")
            return asyncio.create_task(
                self._adapter.call_api(
                    endpoint="get_group_info",
                    _account_id=self._account_id,
                    group_id=int(self._target_id),
                )
            )

        def GetGroupList(self):
            """[已废弃] 获取群列表，推荐使用 Api.get_group_list()"""
            _deprecation_warning("GetGroupList", "Api.get_group_list()")
            return asyncio.create_task(
                self._adapter.call_api(
                    endpoint="get_group_list",
                    _account_id=self._account_id,
                )
            )

        def GetGroupMemberInfo(self, user_id: Union[str, int]):
            """[已废弃] 获取群成员信息，推荐使用 Api.get_group_member_info(group_id, user_id)"""
            _deprecation_warning(
                "GetGroupMemberInfo", "Api.get_group_member_info(group_id, user_id)"
            )
            return asyncio.create_task(
                self._adapter.call_api(
                    endpoint="get_group_member_info",
                    _account_id=self._account_id,
                    group_id=int(self._target_id),
                    user_id=int(user_id),
                )
            )

        def GetGroupMemberList(self):
            """[已废弃] 获取群成员列表，推荐使用 Api.get_group_member_list(group_id)"""
            _deprecation_warning(
                "GetGroupMemberList", "Api.get_group_member_list(group_id)"
            )
            return asyncio.create_task(
                self._adapter.call_api(
                    endpoint="get_group_member_list",
                    _account_id=self._account_id,
                    group_id=int(self._target_id),
                )
            )

        # ==================== SnowLuma 扩展便捷方法 ====================

        def QzoneMsg(self, content: str):
            """发表 QQ 空间说说（纯文字）"""
            return asyncio.create_task(
                self._adapter.call_api(
                    endpoint="send_qzone_msg",
                    _account_id=self._account_id,
                    content=content,
                )
            )

        def QzoneLike(self, tid: str):
            """给 QQ 空间说说点赞"""
            return asyncio.create_task(
                self._adapter.call_api(
                    endpoint="like_qzone",
                    _account_id=self._account_id,
                    tid=str(tid),
                )
            )

        def QzoneUnlike(self, tid: str):
            """取消 QQ 空间说说点赞"""
            return asyncio.create_task(
                self._adapter.call_api(
                    endpoint="unlike_qzone",
                    _account_id=self._account_id,
                    tid=str(tid),
                )
            )

        def QzoneComment(self, tid: str, content: str):
            """评论 QQ 空间说说"""
            return asyncio.create_task(
                self._adapter.call_api(
                    endpoint="comment_qzone",
                    _account_id=self._account_id,
                    tid=str(tid),
                    content=content,
                )
            )

        def QzoneDelete(self, tid: str):
            """删除 QQ 空间说说"""
            return asyncio.create_task(
                self._adapter.call_api(
                    endpoint="delete_qzone_msg",
                    _account_id=self._account_id,
                    tid=str(tid),
                )
            )

        def GroupPoke(self, user_id: Union[str, int]):
            """群拍一拍（需通过 To("group", group_id) 指定群）"""
            return asyncio.create_task(
                self._adapter.call_api(
                    endpoint="group_poke",
                    _account_id=self._account_id,
                    group_id=int(self._target_id),
                    user_id=int(user_id),
                )
            )

        def FriendPoke(self, user_id: Union[str, int]):
            """好友拍一拍"""
            return asyncio.create_task(
                self._adapter.call_api(
                    endpoint="friend_poke",
                    _account_id=self._account_id,
                    user_id=int(user_id),
                )
            )

        def SendPoke(self, user_id: Union[str, int]):
            """拍一拍（自动路由群聊/私聊）"""
            return asyncio.create_task(
                self._adapter.call_api(
                    endpoint="send_poke",
                    _account_id=self._account_id,
                    user_id=int(user_id),
                    group_id=int(self._target_id) if self._target_type == "group" else None,
                )
            )

        def SetMsgEmojiLike(self, message_id: Union[str, int], emoji_id: Union[str, int]):
            """设置消息表情回应"""
            return asyncio.create_task(
                self._adapter.call_api(
                    endpoint="set_msg_emoji_like",
                    _account_id=self._account_id,
                    message_id=int(message_id),
                    emoji_id=str(emoji_id),
                )
            )

        def UploadGroupFile(self, file: Union[str, bytes], name: str):
            """上传群文件（需通过 To("group", group_id) 指定群）"""
            file = self._file_to_base64(file)
            return asyncio.create_task(
                self._adapter.call_api(
                    endpoint="upload_group_file",
                    _account_id=self._account_id,
                    group_id=int(self._target_id),
                    file=file,
                    name=name,
                )
            )

        def GetGroupFileUrl(self, file_id: str):
            """获取群文件下载链接（需通过 To("group", group_id) 指定群）"""
            return asyncio.create_task(
                self._adapter.call_api(
                    endpoint="get_group_file_url",
                    _account_id=self._account_id,
                    group_id=int(self._target_id),
                    file_id=str(file_id),
                )
            )

        def MarkMsgAsRead(self):
            """标记消息已读（群聊/私聊自动路由，需通过 To() 指定目标）"""
            return asyncio.create_task(
                self._adapter.call_api(
                    endpoint="mark_msg_as_read",
                    _account_id=self._account_id,
                    message_type="private" if self._target_type == "user" else "group",
                    user_id=int(self._target_id) if self._target_type == "user" else None,
                    group_id=int(self._target_id) if self._target_type == "group" else None,
                )
            )

        def SetOnlineStatus(self, status: int):
            """设置在线状态"""
            return asyncio.create_task(
                self._adapter.call_api(
                    endpoint="set_online_status",
                    _account_id=self._account_id,
                    status=int(status),
                )
            )

        def GetGroupMsgHistory(self, message_seq: int = 0, count: int = 20):
            """获取群消息历史（需通过 To("group", group_id) 指定群）"""
            return asyncio.create_task(
                self._adapter.call_api(
                    endpoint="get_group_msg_history",
                    _account_id=self._account_id,
                    group_id=int(self._target_id),
                    message_seq=int(message_seq),
                    count=int(count),
                )
            )

        def GetFriendMsgHistory(self, user_id: Union[str, int], count: int = 20):
            """获取好友消息历史"""
            return asyncio.create_task(
                self._adapter.call_api(
                    endpoint="get_friend_msg_history",
                    _account_id=self._account_id,
                    user_id=int(user_id),
                    count=int(count),
                )
            )

        def GroupReaction(self, message_id: Union[str, int], emoji_id: Union[str, int], enable: bool = True):
            """群聊表情回应（需通过 To("group", group_id) 指定群）"""
            return asyncio.create_task(
                self._adapter.call_api(
                    endpoint="set_group_reaction",
                    _account_id=self._account_id,
                    group_id=int(self._target_id),
                    message_id=int(message_id),
                    code=str(emoji_id),
                    is_enable=enable,
                )
            )

        def SetEssenceMsg(self, message_id: Union[str, int]):
            """设置精华消息"""
            return asyncio.create_task(
                self._adapter.call_api(
                    endpoint="set_essence_msg",
                    _account_id=self._account_id,
                    message_id=int(message_id),
                )
            )

        def DeleteEssenceMsg(self, message_id: Union[str, int]):
            """移除精华消息"""
            return asyncio.create_task(
                self._adapter.call_api(
                    endpoint="delete_essence_msg",
                    _account_id=self._account_id,
                    message_id=int(message_id),
                )
            )

        def SetFriendRemark(self, user_id: Union[str, int], remark: str):
            """设置好友备注"""
            return asyncio.create_task(
                self._adapter.call_api(
                    endpoint="set_friend_remark",
                    _account_id=self._account_id,
                    user_id=int(user_id),
                    remark=remark,
                )
            )

        def OcrImage(self, image: str):
            """OCR 图片识别"""
            return asyncio.create_task(
                self._adapter.call_api(
                    endpoint="ocr_image",
                    _account_id=self._account_id,
                    image=image,
                )
            )

        def GetImage(self, file: str):
            """获取图片信息"""
            return asyncio.create_task(
                self._adapter.call_api(
                    endpoint="get_image",
                    _account_id=self._account_id,
                    file=file,
                )
            )

        def GetRecord(self, file: str, out_format: str = "mp3"):
            """获取语音信息"""
            return asyncio.create_task(
                self._adapter.call_api(
                    endpoint="get_record",
                    _account_id=self._account_id,
                    file=file,
                    out_format=out_format,
                )
            )

        def FetchPttText(self, file: str):
            """语音转文字"""
            return asyncio.create_task(
                self._adapter.call_api(
                    endpoint="fetch_ptt_text",
                    _account_id=self._account_id,
                    file=file,
                )
            )

        def _convert_ob12_to_ob11(self, message: List[Dict]) -> List[Dict]:
            ob11_message = []
            for segment in message:
                seg_type = segment.get("type", "")
                seg_data = segment.get("data", {})
                if seg_type == "text":
                    ob11_message.append({"type": "text", "data": {"text": seg_data.get("text", "")}})
                elif seg_type == "image":
                    file = seg_data.get("file") or seg_data.get("url", "")
                    ob11_message.append({"type": "image", "data": {"file": file}})
                elif seg_type in ("audio", "record"):
                    file = seg_data.get("file") or seg_data.get("url", "")
                    ob11_message.append({"type": "record", "data": {"file": file}})
                elif seg_type == "video":
                    file = seg_data.get("file") or seg_data.get("url", "")
                    ob11_message.append({"type": "video", "data": {"file": file}})
                elif seg_type == "file":
                    file = seg_data.get("file") or seg_data.get("url", "")
                    file_name = seg_data.get("file_name", "")
                    data = {"file": file}
                    if file_name:
                        data["name"] = file_name
                    ob11_message.append({"type": "file", "data": data})
                elif seg_type == "face":
                    ob11_message.append({"type": "face", "data": {"id": seg_data.get("id", "")}})
                elif seg_type in ("mention", "at"):
                    ob11_message.append({"type": "at", "data": {"qq": str(seg_data.get("user_id", seg_data.get("qq", "")))}})
                elif seg_type == "mention_all":
                    ob11_message.append({"type": "at", "data": {"qq": "all"}})
                elif seg_type == "reply":
                    ob11_message.append({"type": "reply", "data": {"id": str(seg_data.get("message_id", seg_data.get("id", "")))}})
                elif seg_type.startswith("onebot11_"):
                    ob11_message.append({"type": seg_type[10:], "data": seg_data})
                else:
                    ob11_message.append({"type": seg_type, "data": seg_data})
            return ob11_message

    class Request(RequestDSL):
        """SnowLuma 请求处理 DSL（基于 OB11 协议）"""

        async def _do_accept(self, **kwargs) -> dict[str, Any]:
            return await self._do_action(approve=True, **kwargs)

        async def _do_reject(self, **kwargs) -> dict[str, Any]:
            return await self._do_action(approve=False, **kwargs)

        async def _do_action(self, approve: bool, **kwargs) -> dict[str, Any]:
            try:
                result = await self._adapter.call_api(
                    endpoint="set_friend_add_request"
                    if kwargs.get("_request_type") != "group"
                    else "set_group_add_request",
                    _account_id=self._account_id,
                    flag=self._request_id,
                    approve=approve,
                    **{k: v for k, v in kwargs.items() if not k.startswith("_")},
                )
                return result
            except Exception as e:
                return self._adapter.make_error(message=str(e))

    def __init__(self, sdk_ref=None):
        super().__init__(sdk_ref)
        self._self_id_map: Dict[str, str] = {}
        self._bot_ids: Dict[str, str] = {}
        self._pending_connect_meta: set = set()
        self.connections: Dict[str, Any] = {}
        self._api_response_futures: Dict[str, Dict[str, asyncio.Future]] = {}
        self.reconnect_tasks: Dict[str, asyncio.Task] = {}
        self.poll_tasks: Dict[str, asyncio.Task] = {}
        # WS 请求 echo 关联用自增序列：hash() 在并发同参数调用时会碰撞串台
        self._echo_seq = itertools.count(1)
        self._running = False
        self.default_timeout = 30
        self.default_retry_interval = 30

        from .Converter import SnowLumaConverter

        platform = self._platform or "snowluma"
        self._converter = SnowLumaConverter(platform=platform)
        self.convert = self._converter.convert

        self._check_framework_version()
        self._get_logger().info(f"SnowLumaAdapter v{__version__} 已加载")

    @staticmethod
    def _parse_version(version_str: str) -> tuple:
        """解析版本号为可比较的三元组（忽略 dev/预发布后缀，如 2.8.0-dev.3 → (2, 8, 0)）"""
        parts = []
        for piece in str(version_str).split("."):
            digits = "".join(ch for ch in piece if ch.isdigit())
            parts.append(int(digits) if digits else 0)
        while len(parts) < 3:
            parts.append(0)
        return tuple(parts[:3])

    def _check_framework_version(self):
        """软依赖检测：框架版本过低时打警告（不阻断加载）"""
        try:
            from importlib.metadata import version as _pkg_version

            raw = _pkg_version("ErisPulse")
        except Exception:
            return
        try:
            if self._parse_version(raw) < MIN_FRAMEWORK_VERSION:
                self._get_logger().warning(
                    f"当前 ErisPulse 版本 {raw} 过低：SnowLumaAdapter v{__version__} 需要 >= "
                    f"{'.'.join(map(str, MIN_FRAMEWORK_VERSION))}"
                    "（BaseConverter / Api DSL / spawn_background 等特性），"
                    "部分功能可能不可用，建议升级框架"
                )
        except Exception:
            pass

    def _get_config_key(self) -> str:
        return "SnowLuma_Adapter"

    def _get_bot_id(self, account_name: str) -> str:
        return self._bot_ids.get(account_name, "")

    def _bot_id_display(self, account_name: str) -> str:
        return self._bot_ids.get(account_name, "待确认")

    def _update_bot_id(self, account_name: str, self_id: str):
        old = self._bot_ids.get(account_name)
        if not old:
            self._bot_ids[account_name] = self_id
            self.logger.info(f"账户 {account_name} 自动识别 bot_id: {self_id}")
        elif old != self_id:
            self._bot_ids[account_name] = self_id
            self.logger.warning(f"账户 {account_name} bot_id 变更: {old} → {self_id}")

    def _wrap_api_response(self, raw_response: Dict, endpoint: str, account_name: str) -> dict:
        """
        将 OneBot 响应信封（status/retcode/data）包装为标准响应结果

        {!--< internal-use >!--}
        """
        message_id = ""
        if isinstance(raw_response.get("data"), dict):
            message_id = str(raw_response["data"].get("message_id", ""))

        retcode = raw_response.get("retcode", 0)
        status = "ok" if retcode == 0 else "failed"

        return self.make_response(
            status=status,
            retcode=retcode,
            data=raw_response.get("data"),
            message_id=message_id,
            message=raw_response.get("message", ""),
            raw=raw_response,
        )

    async def _call_http(self, endpoint: str, account_name: str, account, params: Dict) -> dict:
        """
        http/webhook 模式：POST {http_url}/{endpoint} 调用动作，同步取响应信封

        {!--< internal-use >!--}
        """
        base_url = (account.http_url or "http://127.0.0.1:3000").rstrip("/")
        url = f"{base_url}/{endpoint}"
        headers: Dict[str, str] = {"Content-Type": "application/json"}
        if account.token:
            headers["Authorization"] = f"Bearer {account.token}"

        self.logger.debug(
            f"账户 {account_name} (bot_id: {self._bot_id_display(account_name)}) HTTP 请求: POST {url} {params}"
        )
        try:
            resp = await client.post(url, json=params, headers=headers, timeout=self.default_timeout)
            raw_response = await resp.json()
        except Exception as e:
            self.logger.error(
                f"账户 {account_name} (bot_id: {self._bot_id_display(account_name)}) HTTP 调用失败: {endpoint}: {e}"
            )
            return self.make_error(
                retcode=34001, message=f"HTTP 调用失败: {e}", raw=None
            )

        if not isinstance(raw_response, dict):
            return self.make_error(
                retcode=34002,
                message=f"HTTP 响应格式异常: {str(raw_response)[:200]}",
                raw=raw_response,
            )
        return self._wrap_api_response(raw_response, endpoint, account_name)

    async def call_api(self, endpoint: str, _account_id: str = None, **params):
        """
        调用 SnowLuma OneBot11 API

        client/server 模式经 WebSocket 以 echo 关联请求响应；
        http/webhook 模式直接 HTTP POST 取同步响应。

        :param endpoint: API 端点名称（如 send_msg、get_login_info 等）
        :param _account_id: 账户标识
        :param params: API 参数
        :return: 标准响应结果
        """
        account_name, account = self._resolve_account(_account_id)
        # 吸收 ApiDSL._merge_context 传入的 account_id
        params.pop("account_id", None)
        # 剥离 None 参数——OneBot 11 约定缺省参数应省略而非传 null，
        # OneBot 实现的参数校验会拒绝 null 值（如私聊 send_msg 携带 group_id: null
        # 报 retcode 1400 "expected a positive integer"），导致消息静默未送达
        params = {key: value for key, value in params.items() if value is not None}

        if account.mode in ("http", "webhook"):
            return await self._call_http(endpoint, account_name, account, params)

        connection = self.connections.get(account_name)
        if not connection:
            raise ConnectionError(f"账户 {account_name} 尚未连接")

        if hasattr(connection, "closed") and connection.closed:
            raise ConnectionError(f"账户 {account_name} 的连接已关闭")

        if account_name not in self._api_response_futures:
            self._api_response_futures[account_name] = {}

        echo = f"snowluma-{next(self._echo_seq)}"
        future = asyncio.get_event_loop().create_future()
        self._api_response_futures[account_name][echo] = future

        payload = {"action": endpoint, "params": params, "echo": echo}

        try:
            await connection.send_text(json.dumps(payload))
        except Exception as e:
            self.logger.error(
                f"账户 {account_name} (bot_id: {self._bot_id_display(account_name)}) 发送请求失败: {str(e)}"
            )
            if echo in self._api_response_futures[account_name]:
                del self._api_response_futures[account_name][echo]
            raise

        try:
            self.logger.debug(
                f"账户 {account_name} (bot_id: {self._bot_id_display(account_name)}) 请求: {payload}"
            )
            raw_response = await asyncio.wait_for(future, timeout=self.default_timeout)
            self.logger.debug(
                f"账户 {account_name} (bot_id: {self._bot_id_display(account_name)}) 响应: {raw_response}"
            )

            return self._wrap_api_response(raw_response, endpoint, account_name)
        except asyncio.TimeoutError:
            self.logger.error(
                f"账户 {account_name} (bot_id: {self._bot_id_display(account_name)}) API调用超时: {endpoint}"
            )
            if not future.done():
                future.cancel()
            return self.make_error(
                retcode=33001,
                message=f"账户 {account_name} API调用超时: {endpoint}",
                raw=None,
            )
        finally:
            async def cleanup():
                await asyncio.sleep(0.1)
                if account_name in self._api_response_futures and echo in self._api_response_futures[account_name]:
                    del self._api_response_futures[account_name][echo]
            asyncio.create_task(cleanup())

    async def connect(self, account_name: str):
        """以 Client 模式连接 SnowLuma 服务"""
        if account_name not in self.accounts:
            raise ValueError(f"账户 {account_name} 不存在")

        account = self.accounts[account_name]
        if account.mode != "client":
            return

        headers = {}
        if account.token:
            headers["Authorization"] = f"Bearer {account.token}"

        url = account.url

        while self._running:
            try:
                self.logger.debug(
                    f"账户 {account_name} 正在连接: url={url}, token={'***' if headers.get('Authorization') else '(none)'}"
                )
                ws = await client.ws_connect(url, headers=headers)
                self.connections[account_name] = ws
                self.logger.info(
                    f"账户 {account_name} (bot_id: {self._bot_id_display(account_name)}) 连接成功"
                )
                await self.emit_meta("connect", self._get_bot_id(account_name))
                if not self._get_bot_id(account_name):
                    self._pending_connect_meta.add(account_name)
                await self._listen(account_name)
                if not self._running:
                    return
                self.logger.info(
                    f"账户 {account_name} (bot_id: {self._bot_id_display(account_name)}) "
                    f"{self.default_retry_interval}秒后重连..."
                )
                await asyncio.sleep(self.default_retry_interval)
            except Exception as e:
                if not self._running:
                    return
                self.logger.error(
                    f"账户 {account_name} (bot_id: {self._bot_id_display(account_name)}) 连接失败: {str(e)}"
                )
                await asyncio.sleep(self.default_retry_interval)

    async def _listen(self, account_name: str):
        connection = self.connections.get(account_name)
        if not connection:
            return
        account = self.accounts.get(account_name)
        try:
            while True:
                msg = await connection.receive()
                if msg.type == WSMessage.TEXT:
                    self.logger.debug(f"账户 {account_name} 收到WS文本: {str(msg.data)[:300]}")
                    asyncio.create_task(self._handle_message(msg.data, account_name))
                elif msg.type == WSMessage.BINARY:
                    self.logger.debug(f"账户 {account_name} 收到WS二进制数据")
                elif msg.type == WSMessage.CLOSE:
                    self.logger.info(f"账户 {account_name} (bot_id: {self._bot_id_display(account_name)}) 收到CLOSE帧")
                    break
                elif msg.type == WSMessage.ERROR:
                    self.logger.error(f"账户 {account_name} (bot_id: {self._bot_id_display(account_name)}) 收到ERROR帧")
                    break
                else:
                    self.logger.warning(f"账户 {account_name} 收到未知消息类型: {msg.type}")
        except Exception as e:
            self.logger.error(
                f"账户 {account_name} (bot_id: {self._bot_id_display(account_name)}) 监听异常: {str(e)}",
                exc_info=True,
            )
        finally:
            try:
                await self.emit_meta("disconnect", self._get_bot_id(account_name) if account else "")
            except Exception:
                pass
            self.connections.pop(account_name, None)

    async def _handle_message(self, raw_msg: str, account_name: str):
        try:
            data = json.loads(raw_msg)
            if not self.accounts.get(account_name):
                return

            if "echo" in data:
                future = self._api_response_futures.get(account_name, {}).get(data["echo"])
                if future and not future.done():
                    future.set_result(data)
                return

            await self._dispatch_event(data, account_name)
        except json.JSONDecodeError:
            self.logger.error(f"JSON解析失败: {raw_msg}")
        except Exception as e:
            self.logger.error(f"消息处理异常: {str(e)}")

    async def _dispatch_event(self, data: Dict, account_name: str):
        """
        将单条 OB11 原始事件转换并分发（WS / HTTP 轮询 / Webhook 共用）

        {!--< internal-use >!--}
        """
        from ErisPulse.Core import adapter as adapter_mgr

        onebot_event = self.convert(data)
        if not onebot_event:
            return
        raw_self_id = onebot_event.get("self", {}).get("user_id", "")
        if raw_self_id:
            self._update_bot_id(account_name, str(raw_self_id))
            if str(raw_self_id) not in self._self_id_map:
                self._self_id_map[str(raw_self_id)] = account_name
                self.logger.info(f"映射 self_id {raw_self_id} → 账户 {account_name}")
            if account_name in self._pending_connect_meta:
                self._pending_connect_meta.discard(account_name)
                await self.emit_meta("connect", str(raw_self_id))
        await adapter_mgr.emit(onebot_event)

    async def _poll_events(self, account_name: str):
        """
        http 模式事件轮询：周期调用 get_latest_events 拉取增量事件

        {!--< internal-use >!--}
        """
        account = self.accounts.get(account_name)
        if not account:
            return
        interval = max(0.1, float(account.poll_interval or 1.0))

        while self._running:
            try:
                result = await self._call_http(
                    "get_latest_events", account_name, account, {"limit": 64}
                )
                events = result.get("data") if isinstance(result, dict) else None
                if isinstance(events, list):
                    for item in events:
                        if isinstance(item, dict):
                            await self._dispatch_event(item, account_name)
                elif isinstance(result, dict) and str(result.get("status")) == "failed":
                    self.logger.debug(
                        f"账户 {account_name} (bot_id: {self._bot_id_display(account_name)}) "
                        f"轮询 get_latest_events 失败: {result.get('message', '')}"
                    )
            except asyncio.CancelledError:
                raise
            except Exception as e:
                self.logger.error(
                    f"账户 {account_name} (bot_id: {self._bot_id_display(account_name)}) 事件轮询异常: {str(e)}"
                )
            await asyncio.sleep(interval)

    def _make_webhook_handler(self, account_name: str):
        """
        webhook 模式事件上报处理器（token 校验兼容 Bearer 头与 ?token= 查询参数）

        {!--< internal-use >!--}
        """

        async def webhook_receiver(request):
            account = self.accounts.get(account_name)
            if not account:
                return {"status": "failed", "message": "unknown account"}, 404

            if account.token:
                provided = (
                    request.headers.get("Authorization", "").replace("Bearer ", "")
                    or request.query_params.get("token", "")
                )
                if provided != account.token:
                    self.logger.warning(
                        f"账户 {account_name} (bot_id: {self._bot_id_display(account_name)}) Webhook Token无效"
                    )
                    return {"status": "failed", "message": "unauthorized"}, 401

            try:
                body = await request.json()
            except Exception as e:
                return {"status": "failed", "message": f"invalid json body: {e}"}, 400

            events = body if isinstance(body, list) else [body]
            accepted = 0
            for item in events:
                if isinstance(item, dict):
                    try:
                        await self._dispatch_event(item, account_name)
                        accepted += 1
                    except Exception as e:
                        self.logger.error(f"Webhook 事件处理异常: {str(e)}")
            return {"status": "ok", "accepted": accepted}

        return webhook_receiver

    async def register_webhook_routes(self, account_names: List[str]):
        """注册 webhook 模式的事件上报 HTTP 路由（最终路径为 /snowluma_{account}{path}）"""
        for account_name in account_names:
            account = self.accounts[account_name]
            path = account.webhook_path or "/events"
            if "{account}" in path:
                path = path.replace("{account}", account_name)

            namespace = f"{self._platform}_{account_name}"
            router.register_http_route(
                namespace,
                path,
                self._make_webhook_handler(account_name),
                methods=["POST"],
            )
            full_path = "/" + "/".join(p for p in (namespace, path.strip("/")) if p)
            self.logger.info(
                f"已注册账户 {account_name} (bot_id: {self._bot_id_display(account_name)}) 的Webhook路由: {full_path}"
            )

    async def _ws_handler(self, websocket, account_name: str = "default"):
        account = self.accounts.get(account_name)
        if account:
            self.logger.info(f"账户 {account_name} (bot_id: {self._bot_id_display(account_name)}) 客户端已连接")
        self.connections[account_name] = websocket
        await self.emit_meta("connect", self._get_bot_id(account_name) if account else "")
        if account and not self._get_bot_id(account_name):
            self._pending_connect_meta.add(account_name)
        try:
            while True:
                data = await websocket.receive_text()
                asyncio.create_task(self._handle_message(data, account_name))
        except Exception:
            self.logger.info(f"账户 {account_name} (bot_id: {self._bot_id_display(account_name) if account else ''}) 客户端断开连接")
        finally:
            try:
                await self.emit_meta("disconnect", self._get_bot_id(account_name) if account else "")
            except Exception:
                pass
            if account_name in self.connections:
                del self.connections[account_name]

    async def _auth_handler(self, websocket, account_name: str = "default"):
        if account_name not in self.accounts:
            await websocket.close(code=1008)
            return False
        account = self.accounts[account_name]
        if account.token:
            client_token = websocket.headers.get("Authorization", "").replace("Bearer ", "")
            if not client_token:
                query = dict(websocket.query_params)
                client_token = query.get("token", "")
            if client_token != account.token:
                self.logger.warning(f"账户 {account_name} (bot_id: {self._bot_id_display(account_name)}) Token无效")
                await websocket.close(code=1008)
                return False
        return True

    async def register_websocket(self):
        for account_name, account in self.enabled_accounts.items():
            if account.mode == "server":
                path = account.server_path

                def make_ws_handler(name):
                    async def handler(ws):
                        await self._ws_handler(ws, name)
                    return handler

                def make_auth_handler(name):
                    async def handler(ws):
                        return await self._auth_handler(ws, name)
                    return handler

                router.register_websocket(
                    f"{self._platform}_{account_name}",
                    path,
                    make_ws_handler(account_name),
                    auth_handler=make_auth_handler(account_name),
                )
                self.logger.info(f"已注册账户 {account_name} (bot_id: {self._bot_id_display(account_name)}) 的Server路由: {path}")

    async def start(self):
        self._running = True
        server_accounts = [name for name, acc in self.enabled_accounts.items() if acc.mode == "server"]
        client_accounts = [name for name, acc in self.enabled_accounts.items() if acc.mode == "client"]
        http_accounts = [name for name, acc in self.enabled_accounts.items() if acc.mode == "http"]
        webhook_accounts = [name for name, acc in self.enabled_accounts.items() if acc.mode == "webhook"]

        if server_accounts:
            await self.register_websocket()
        if webhook_accounts:
            await self.register_webhook_routes(webhook_accounts)

        for account_name in client_accounts:
            self.logger.info(f"启动Client模式账户: {account_name} (bot_id: {self._bot_id_display(account_name)})")
            coro = self.connect(account_name)
            # 生命周期任务使用 spawn_background（owner 归属，shutdown 自动回收）
            self.reconnect_tasks[account_name] = (
                spawn_background(coro) if spawn_background is not None else asyncio.create_task(coro)
            )

        for account_name in http_accounts:
            account = self.accounts[account_name]
            interval = float(account.poll_interval or 0)
            if interval > 0:
                self.logger.info(
                    f"启动HTTP模式账户: {account_name} (bot_id: {self._bot_id_display(account_name)}) "
                    f"事件轮询间隔: {interval}s"
                )
                coro = self._poll_events(account_name)
                # 生命周期任务使用 spawn_background（owner 归属，shutdown 自动回收）
                self.poll_tasks[account_name] = (
                    spawn_background(coro) if spawn_background is not None else asyncio.create_task(coro)
                )
            else:
                self.logger.info(
                    f"启动HTTP模式账户: {account_name} (bot_id: {self._bot_id_display(account_name)}) "
                    f"纯API模式（poll_interval=0，不拉取事件）"
                )

        enabled_count = len(server_accounts) + len(client_accounts) + len(http_accounts) + len(webhook_accounts)
        self.logger.info(f"SnowLuma适配器启动完成，共 {enabled_count} 个账户")

    async def shutdown(self):
        self._running = False
        for task in self.reconnect_tasks.values():
            if not task.done():
                task.cancel()
        self.reconnect_tasks.clear()

        for task in self.poll_tasks.values():
            if not task.done():
                task.cancel()
        self.poll_tasks.clear()

        for account_name, connection in list(self.connections.items()):
            account = self.accounts.get(account_name)
            try:
                if hasattr(connection, "closed") and not connection.closed:
                    await connection.close()
            except Exception as e:
                self.logger.error(f"关闭账户 {account_name} 连接失败: {str(e)}")
        self.connections.clear()
        self.logger.info("SnowLuma适配器已关闭")
