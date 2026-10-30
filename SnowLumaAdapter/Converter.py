"""
SnowLuma 事件转换器

将 OneBot11 协议事件（SnowLuma 后端）转换为 ErisPulse 统一的事件格式（兼容 OneBot12 结构）。

SnowLuma 使用 OneBot v11 协议，因此本转换器复用 OB11 的事件/消息段映射逻辑，
仅将平台标识从 "onebot11" 改为 "snowluma"。

{!--< tips >!--}
1. 转换后的事件保留原始数据在 snowluma_raw 字段中
2. CQ 码和数组格式消息均支持解析
3. 未识别的 CQ 码类型会以 onebot11_ 前缀透传（协议级前缀）
4. 平台特有事件（poke/honor 等）使用 snowluma_ 前缀
{!--< /tips >!--}
"""

import time
import uuid
from typing import Dict, Optional, List, Any

from ErisPulse.Core.Bases import BaseConverter


class SnowLumaConverter(BaseConverter):
    """
    SnowLuma (OB11 协议) → ErisPulse 事件转换器

    继承 BaseConverter，公共字段（id/time/platform/self/{platform}_raw）由
    build_base_event 构建后按 OB11 字段名（echo/time/self_id）覆盖。

    {!--< tips >!--}
    1. 消息事件会解析 CQ 码并转换为 OB12 消息段格式
    2. 通知事件会映射到统一的 detail_type 命名
    3. 复用 OB11 协议映射，平台标识为 snowluma
    {!--< /tips >!--}
    """

    def __init__(self, platform: str = "snowluma"):
        super().__init__(platform=platform)
        self._setup_event_mapping()

    def _setup_event_mapping(self):
        self.event_map = {
            "message": "message",
            "notice": "notice",
            "request": "request",
            "meta_event": "meta_event",
        }

        self.notice_subtypes = {
            "group_upload": "group_file_upload",
            "group_admin": "group_admin_change",
            "group_decrease": "group_member_decrease",
            "group_increase": "group_member_increase",
            "group_ban": "group_ban",
            "friend_add": "friend_increase",
            "friend_delete": "friend_decrease",
            "group_recall": "message_recall",
            "friend_recall": "message_recall",
            "notify": "notify",
        }

    def convert(self, raw_event: Dict) -> Optional[Dict]:
        if not isinstance(raw_event, dict):
            raise ValueError("事件数据必须是字典类型")

        post_type = raw_event.get("post_type")
        if post_type not in self.event_map:
            return None

        # 基础事件结构（BaseConverter 提供骨架，按 OB11 字段名覆盖）
        onebot_event = self.build_base_event(raw_event, post_type)
        onebot_event["id"] = str(raw_event.get("echo", str(uuid.uuid4())))
        onebot_event["time"] = self._convert_timestamp(raw_event.get("time", int(time.time())))
        onebot_event["self"]["user_id"] = str(raw_event.get("self_id", ""))

        handler = getattr(self, f"_handle_{post_type}", None)
        if handler:
            return handler(raw_event, onebot_event)

        return None

    def _convert_timestamp(self, ts) -> int:
        if isinstance(ts, str):
            if len(ts) == 13:
                return int(ts) // 1000
            return int(ts)
        elif isinstance(ts, (int, float)):
            if ts > 9999999999:
                return int(ts // 1000)
            return int(ts)
        return int(time.time())

    def _handle_message(self, raw_event: Dict, base_event: Dict) -> Dict:
        message_type = raw_event["message_type"]
        detail_type = "private" if message_type == "private" else "group"

        message_segments = self._parse_cq_code(raw_event["message"])
        alt_message = self._generate_alt_message(message_segments)

        # message_id 为非零有符号 32 位整数，负值有效：
        # 引用、查询与撤回时应原样保留，任何环节不得取绝对值
        base_event.update(
            {
                "type": "message",
                "detail_type": detail_type,
                "message_id": str(raw_event.get("message_id", "")),
                "message": message_segments,
                "alt_message": alt_message,
                "user_id": str(
                    raw_event.get("sender", {}).get(
                        "user_id", raw_event.get("user_id", "")
                    )
                ),
            }
        )

        sender = raw_event.get("sender", {})
        if "nickname" in sender:
            base_event["user_nickname"] = sender["nickname"]
        if "card" in sender and sender["card"]:
            base_event["user_nickname"] = sender["card"]

        if detail_type == "group":
            base_event["group_id"] = str(raw_event.get("group_id", ""))
            if "group_name" in raw_event:
                base_event["group_name"] = raw_event["group_name"]

        if raw_event.get("sub_type"):
            base_event["sub_type"] = raw_event["sub_type"]

        return base_event

    @staticmethod
    def _unescape_cq(value: str) -> str:
        """
        还原 CQ 码转义字符（对齐官方 SDK fromCQString 语义）

        ``&#91;`` → ``[``、``&#93;`` → ``]``、``&#44;`` → ``,``、``&amp;`` → ``&``；
        ``&amp;`` 必须最后处理，避免把其他实体的 ``&`` 前缀二次还原。

        {!--< internal-use >!--}
        """
        value = value.replace("&#91;", "[").replace("&#93;", "]").replace("&#44;", ",")
        return value.replace("&amp;", "&")

    def _parse_cq_code(self, message: Any) -> List[Dict]:
        if isinstance(message, str):
            if "[CQ:" not in message:
                return [{"type": "text", "data": {"text": self._unescape_cq(message)}}]

            segments = []
            last_pos = 0

            while True:
                cq_start = message.find("[CQ:", last_pos)
                if cq_start == -1:
                    if last_pos < len(message):
                        text = message[last_pos:]
                        if text:
                            segments.append({"type": "text", "data": {"text": self._unescape_cq(text)}})
                    break

                if cq_start > last_pos:
                    text = message[last_pos:cq_start]
                    if text:
                        segments.append({"type": "text", "data": {"text": self._unescape_cq(text)}})

                cq_end = message.find("]", cq_start)
                if cq_end == -1:
                    segments.append(
                        {"type": "text", "data": {"text": self._unescape_cq(message[cq_start:])}}
                    )
                    break

                cq_content = message[cq_start + 4 : cq_end]
                parts = cq_content.split(",", 1)
                cq_type = parts[0]
                cq_data = {}

                if len(parts) > 1:
                    data_str = parts[1]
                    data_parts = data_str.split(",")
                    for part in data_parts:
                        if "=" in part:
                            key, value = part.split("=", 1)
                            cq_data[key] = self._unescape_cq(value)

                segment = self._convert_cq_segment(cq_type, cq_data)
                segments.append(segment)
                last_pos = cq_end + 1

            return segments

        elif isinstance(message, list):
            segments = []
            for item in message:
                if isinstance(item, str):
                    segments.append({"type": "text", "data": {"text": item}})
                elif isinstance(item, dict):
                    cq_type = item.get("type", "")
                    cq_data = item.get("data", {})
                    segment = self._convert_cq_segment(cq_type, cq_data)
                    segments.append(segment)
            return segments

        return [{"type": "text", "data": {"text": str(message)}}]

    def _convert_cq_segment(self, cq_type: str, cq_data: Dict) -> Dict:
        """将单个 CQ 码段转换为 OB12 消息段"""
        if cq_type == "text":
            return {"type": "text", "data": {"text": cq_data.get("text", "")}}
        elif cq_type == "image":
            return {
                "type": "image",
                "data": {
                    "file": cq_data.get("file"),
                    "url": cq_data.get("url"),
                    "cache": cq_data.get("cache", "1"),
                },
            }
        elif cq_type == "record":
            return {
                "type": "audio",
                "data": {
                    "file": cq_data.get("file"),
                    "url": cq_data.get("url"),
                    "magic": cq_data.get("magic", "0"),
                },
            }
        elif cq_type == "at":
            return {
                "type": "mention",
                "data": {
                    "user_id": cq_data.get("qq"),
                    "user_name": cq_data.get("name", ""),
                },
            }
        elif cq_type == "face":
            return {"type": "face", "data": {"id": cq_data.get("id")}}
        elif cq_type == "reply":
            return {
                "type": "reply",
                "data": {
                    "message_id": cq_data.get("id"),
                    "user_id": cq_data.get("qq", ""),
                },
            }
        else:
            return {"type": f"onebot11_{cq_type}", "data": cq_data}

    def _generate_alt_message(self, segments: List[Dict]) -> str:
        parts = []
        for seg in segments:
            if seg["type"] == "text":
                parts.append(seg["data"]["text"])
            elif seg["type"] == "image":
                parts.append("[图片]")
            elif seg["type"] == "audio":
                parts.append("[语音]")
            elif seg["type"] == "mention":
                data = seg.get("data") or {}
                user_id = str(data.get("user_id") or "").strip()
                user_name = str(data.get("user_name") or "").strip()
                # 昵称缺失回退 user_id；@全体成员固定文案；两者皆缺省略该段，
                # 不输出空 "@"（mention 段构造时 user_name 默认存 ""，不能用
                # get('user_name', fallback)——键存在时 fallback 永不生效）
                if user_id == "all":
                    parts.append("@全体成员")
                elif user_name:
                    parts.append(f"@{user_name}")
                elif user_id:
                    parts.append(f"@{user_id}")
            elif seg["type"] == "face":
                parts.append(f"[表情:{seg['data'].get('id', '')}]")
            elif seg["type"] == "reply":
                parts.append("[回复]")
            elif seg["type"].startswith("onebot11_"):
                parts.append(f"[{seg['type'][9:]}]")
        return "".join(parts)

    def _handle_notice(self, raw_event: Dict, base_event: Dict) -> Dict:
        notice_type = raw_event["notice_type"]
        sub_type = raw_event.get("sub_type", "")

        if notice_type == "bot_status":
            # SnowLuma 账号上下线通知（sub_type: online/offline/bot_offline）转换为
            # OB12 标准元事件 connect/disconnect——这是协议标准形态，不是平台拓展
            base_event.update(
                {
                    "type": "meta_event",
                    "detail_type": "connect" if sub_type == "online" else "disconnect",
                    "sub_type": sub_type,
                    "user_id": str(raw_event.get("user_id", "")),
                    f"{self.platform}_meta": raw_event,
                }
            )
            return base_event

        detail_type = self.notice_subtypes.get(notice_type, notice_type)

        base_event.update(
            {"type": "notice", "detail_type": detail_type, f"{self.platform}_notice": raw_event}
        )

        if notice_type == "group_upload":
            base_event.update(
                {
                    "group_id": str(raw_event.get("group_id")),
                    "user_id": str(raw_event.get("user_id")),
                    f"{self.platform}_file": raw_event.get("file"),
                }
            )
        elif notice_type == "group_admin":
            base_event.update(
                {
                    "group_id": str(raw_event.get("group_id")),
                    "user_id": str(raw_event.get("user_id")),
                    "sub_type": "set" if sub_type == "set" else "unset",
                }
            )
        elif notice_type in ["group_increase", "group_decrease"]:
            base_event.update(
                {
                    "group_id": str(raw_event.get("group_id")),
                    "user_id": str(raw_event.get("user_id")),
                    "operator_id": str(raw_event.get("operator_id", "")),
                    "sub_type": sub_type,
                }
            )
        elif notice_type == "group_ban":
            base_event.update(
                {
                    "group_id": str(raw_event.get("group_id")),
                    "operator_id": str(raw_event.get("operator_id")),
                    "user_id": str(raw_event.get("user_id")),
                    "duration": raw_event.get("duration", 0),
                }
            )
        elif notice_type in ["friend_add", "friend_delete"]:
            base_event.update({"user_id": str(raw_event.get("user_id"))})
        elif notice_type in ["group_recall", "friend_recall"]:
            base_event.update(
                {
                    "message_id": str(raw_event.get("message_id")),
                    "user_id": str(raw_event.get("user_id")),
                    "group_id": str(raw_event.get("group_id", ""))
                    if notice_type == "group_recall"
                    else None,
                }
            )
        elif notice_type == "notify":
            if sub_type == "honor":
                base_event["detail_type"] = f"{self.platform}_honor"
                base_event.update(
                    {
                        "group_id": str(raw_event.get("group_id")),
                        "user_id": str(raw_event.get("user_id")),
                        "honor_type": raw_event.get("honor_type"),
                    }
                )
            elif sub_type == "poke":
                base_event["detail_type"] = f"{self.platform}_poke"
                base_event.update(
                    {
                        "group_id": str(raw_event.get("group_id", "")),
                        "user_id": str(raw_event.get("user_id")),
                        "target_id": str(raw_event.get("target_id")),
                    }
                )
            elif sub_type == "lucky_king":
                base_event["detail_type"] = f"{self.platform}_lucky_king"
                base_event.update(
                    {
                        "group_id": str(raw_event.get("group_id")),
                        "user_id": str(raw_event.get("user_id")),
                        "target_id": str(raw_event.get("target_id")),
                    }
                )

        return base_event

    def _handle_request(self, raw_event: Dict, base_event: Dict) -> Dict:
        request_type = raw_event["request_type"]

        base_event.update(
            {
                "type": "request",
                "detail_type": request_type,
                f"{self.platform}_request": raw_event,
            }
        )

        if request_type == "friend":
            base_event.update(
                {
                    "user_id": str(raw_event.get("user_id")),
                    "comment": raw_event.get("comment"),
                    "flag": raw_event.get("flag"),
                    "request_id": raw_event.get("flag"),
                }
            )
        elif request_type == "group":
            base_event.update(
                {
                    "group_id": str(raw_event.get("group_id")),
                    "user_id": str(raw_event.get("user_id")),
                    "comment": raw_event.get("comment"),
                    "sub_type": raw_event.get("sub_type"),
                    "flag": raw_event.get("flag"),
                    "request_id": raw_event.get("flag"),
                }
            )

        return base_event

    def _handle_meta_event(self, raw_event: Dict, base_event: Dict) -> Dict:
        meta_type = raw_event["meta_event_type"]

        if meta_type == "heartbeat":
            detail_type = "heartbeat"
        else:
            detail_type = f"{self.platform}_{meta_type}"

        base_event.update(
            {
                "type": "meta_event",
                "detail_type": detail_type,
                f"{self.platform}_meta": raw_event,
            }
        )

        if meta_type == "lifecycle":
            base_event["sub_type"] = raw_event.get("sub_type", "")
        elif meta_type == "heartbeat":
            base_event["interval"] = raw_event.get("interval", 0)
            base_event["status"] = raw_event.get("status", {})

        return base_event
