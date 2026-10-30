"""
OneBot11 协议扩展动作（NapCat / SnowLuma / Lagrange 通用）

将这些 OB11 协议级扩展封装为类型化方法，提供 IDE 补全。
各适配器的 Api 类可通过多继承混入：

    class Api(BaseAdapter.Api, OB11ExtensionApi):
        ...

所有方法不加平台前缀，直接委托给 call_api(action_name, ...)，
确保 NapCat/SnowLuma/Lagrange 等 OB11 后端之间可移植。

{!--< tips >!--}
1. 仅收录高频/常用扩展动作，完整 109 个动作可通过 Api.call("action_name", ...) 调用
2. 方法签名基于 NapCat 文档，SnowLuma 兼容
3. 所有查询类方法返回标准响应格式（status/retcode/data）
{!--< /tips >!--}
"""

from typing import Any, Union


class OB11ExtensionApi:
    """
    OB11 协议扩展动作 Mixin

    提供 NapCat/go-cqhttp/SnowLuma 兼容的 OB11 扩展动作的类型化方法。
    通过多继承混入适配器的 Api 内部类，获得 IDE 补全支持。

    使用 ``self._adapter.call_api(action, _account_id=self._account_id, ...)`` 委托。
    """

    # ==================== 拍一戳 / 社交 ====================

    async def send_poke(
        self, *, user_id: Union[str, int], group_id: Union[str, int, None] = None
    ) -> dict[str, Any]:
        """
        发送拍一拍（自动路由群聊/私聊）

        :param user_id: 目标用户 ID
        :param group_id: 群 ID（传入则为群聊拍一拍，否则私聊）
        """
        params: dict[str, Any] = {"user_id": int(user_id)}
        if group_id is not None:
            params["group_id"] = int(group_id)
        return await self._adapter.call_api("send_poke", _account_id=self._account_id, **params)

    async def group_poke(
        self, *, group_id: Union[str, int], user_id: Union[str, int]
    ) -> dict[str, Any]:
        """群拍一拍"""
        return await self._adapter.call_api(
            "group_poke", _account_id=self._account_id,
            group_id=int(group_id), user_id=int(user_id),
        )

    async def friend_poke(self, *, user_id: Union[str, int]) -> dict[str, Any]:
        """好友拍一拍"""
        return await self._adapter.call_api(
            "friend_poke", _account_id=self._account_id, user_id=int(user_id),
        )

    async def send_like(
        self, *, user_id: Union[str, int], times: int = 1
    ) -> dict[str, Any]:
        """点赞（名片赞）"""
        return await self._adapter.call_api(
            "send_like", _account_id=self._account_id,
            user_id=int(user_id), times=times,
        )

    # ==================== 消息回应 / 精华 ====================

    async def set_msg_emoji_like(
        self, *, message_id: Union[str, int], emoji_id: Union[str, int]
    ) -> dict[str, Any]:
        """
        设置消息表情回应

        :param message_id: 消息 ID
        :param emoji_id: 表情 ID
        """
        return await self._adapter.call_api(
            "set_msg_emoji_like", _account_id=self._account_id,
            message_id=int(message_id), emoji_id=str(emoji_id),
        )

    async def get_emoji_likes(
        self, *, message_id: Union[str, int]
    ) -> dict[str, Any]:
        """获取表情回应用户列表"""
        return await self._adapter.call_api(
            "get_emoji_likes", _account_id=self._account_id, message_id=int(message_id),
        )

    async def set_essence_msg(self, *, message_id: Union[str, int]) -> dict[str, Any]:
        """设置精华消息"""
        return await self._adapter.call_api(
            "set_essence_msg", _account_id=self._account_id, message_id=int(message_id),
        )

    async def delete_essence_msg(self, *, message_id: Union[str, int]) -> dict[str, Any]:
        """移除精华消息"""
        return await self._adapter.call_api(
            "delete_essence_msg", _account_id=self._account_id, message_id=int(message_id),
        )

    async def get_essence_msg_list(self, *, group_id: Union[str, int]) -> dict[str, Any]:
        """获取精华消息列表"""
        return await self._adapter.call_api(
            "get_essence_msg_list", _account_id=self._account_id, group_id=int(group_id),
        )

    # ==================== 已读 / 状态 ====================

    async def mark_msg_as_read(
        self,
        *,
        group_id: Union[str, int, None] = None,
        user_id: Union[str, int, None] = None,
    ) -> dict[str, Any]:
        """标记消息已读（群聊/私聊自动路由）"""
        params: dict[str, Any] = {}
        if group_id is not None:
            params["group_id"] = int(group_id)
        elif user_id is not None:
            params["user_id"] = int(user_id)
        return await self._adapter.call_api(
            "mark_msg_as_read", _account_id=self._account_id, **params
        )

    async def mark_group_msg_as_read(self, *, group_id: Union[str, int]) -> dict[str, Any]:
        """标记群消息已读"""
        return await self._adapter.call_api(
            "mark_group_msg_as_read", _account_id=self._account_id, group_id=int(group_id),
        )

    async def mark_private_msg_as_read(self, *, user_id: Union[str, int]) -> dict[str, Any]:
        """标记私聊消息已读"""
        return await self._adapter.call_api(
            "mark_private_msg_as_read", _account_id=self._account_id, user_id=int(user_id),
        )

    async def mark_all_as_read(self) -> dict[str, Any]:
        """标记全部已读"""
        return await self._adapter.call_api(
            "_mark_all_as_read", _account_id=self._account_id
        )

    async def set_online_status(self, *, status: int) -> dict[str, Any]:
        """设置在线状态"""
        return await self._adapter.call_api(
            "set_online_status", _account_id=self._account_id, status=status,
        )

    async def set_input_status(
        self, *, user_id: Union[str, int], event_type: str = "1"
    ) -> dict[str, Any]:
        """设置输入状态（对方可见"正在输入..."）"""
        return await self._adapter.call_api(
            "set_input_status", _account_id=self._account_id,
            user_id=int(user_id), event_type=event_type,
        )

    # ==================== 消息历史 ====================

    async def get_group_msg_history(
        self,
        *,
        group_id: Union[str, int],
        message_seq: int = 0,
        count: int = 20,
    ) -> dict[str, Any]:
        """获取群消息历史"""
        return await self._adapter.call_api(
            "get_group_msg_history", _account_id=self._account_id,
            group_id=int(group_id), message_seq=message_seq, count=count,
        )

    async def get_friend_msg_history(
        self, *, user_id: Union[str, int], count: int = 20
    ) -> dict[str, Any]:
        """获取好友消息历史"""
        return await self._adapter.call_api(
            "get_friend_msg_history", _account_id=self._account_id,
            user_id=int(user_id), count=count,
        )

    # ==================== 群管理扩展 ====================

    async def set_group_reaction(
        self,
        *,
        group_id: Union[str, int],
        message_id: Union[str, int],
        code: Union[str, int],
        is_enable: bool = True,
    ) -> dict[str, Any]:
        """群聊表情回应"""
        return await self._adapter.call_api(
            "set_group_reaction", _account_id=self._account_id,
            group_id=int(group_id), message_id=int(message_id),
            code=str(code), is_enable=is_enable,
        )

    async def set_group_remark(
        self, *, group_id: Union[str, int], remark: str
    ) -> dict[str, Any]:
        """设置群备注"""
        return await self._adapter.call_api(
            "set_group_remark", _account_id=self._account_id,
            group_id=int(group_id), remark=remark,
        )

    async def set_group_sign(self, *, group_id: Union[str, int]) -> dict[str, Any]:
        """群签到"""
        return await self._adapter.call_api(
            "set_group_sign", _account_id=self._account_id, group_id=int(group_id),
        )

    async def set_group_todo(
        self, *, group_id: Union[str, int], content: str
    ) -> dict[str, Any]:
        """设置群待办"""
        return await self._adapter.call_api(
            "set_group_todo", _account_id=self._account_id,
            group_id=int(group_id), content=content,
        )

    async def get_group_info_ex(self, *, group_id: Union[str, int]) -> dict[str, Any]:
        """获取群信息（扩展）"""
        return await self._adapter.call_api(
            "get_group_info_ex", _account_id=self._account_id, group_id=int(group_id),
        )

    async def get_group_detail_info(self, *, group_id: Union[str, int]) -> dict[str, Any]:
        """获取群详细信息"""
        return await self._adapter.call_api(
            "get_group_detail_info", _account_id=self._account_id, group_id=int(group_id),
        )

    async def get_group_shut_list(self, *, group_id: Union[str, int]) -> dict[str, Any]:
        """获取群禁言列表"""
        return await self._adapter.call_api(
            "get_group_shut_list", _account_id=self._account_id, group_id=int(group_id),
        )

    async def get_group_at_all_remain(self, *, group_id: Union[str, int]) -> dict[str, Any]:
        """获取群 @全体成员 剩余次数"""
        return await self._adapter.call_api(
            "get_group_at_all_remain", _account_id=self._account_id, group_id=int(group_id),
        )

    async def get_group_system_msg(self, *, group_id: Union[str, int]) -> dict[str, Any]:
        """获取群系统消息"""
        return await self._adapter.call_api(
            "get_group_system_msg", _account_id=self._account_id, group_id=int(group_id),
        )

    # ==================== 好友 / 联系人 ====================

    async def set_friend_remark(
        self, *, user_id: Union[str, int], remark: str
    ) -> dict[str, Any]:
        """设置好友备注"""
        return await self._adapter.call_api(
            "set_friend_remark", _account_id=self._account_id,
            user_id=int(user_id), remark=remark,
        )

    async def get_unidirectional_friend_list(self) -> dict[str, Any]:
        """获取单向好友列表"""
        return await self._adapter.call_api(
            "get_unidirectional_friend_list", _account_id=self._account_id
        )

    async def get_friends_with_category(self) -> dict[str, Any]:
        """获取分组好友列表"""
        return await self._adapter.call_api(
            "get_friends_with_category", _account_id=self._account_id
        )

    async def get_recent_contact(self) -> dict[str, Any]:
        """获取最近会话"""
        return await self._adapter.call_api(
            "get_recent_contact", _account_id=self._account_id
        )

    # ==================== 群文件 ====================

    async def get_group_file_url(
        self, *, group_id: Union[str, int], file_id: str
    ) -> dict[str, Any]:
        """获取群文件下载链接"""
        return await self._adapter.call_api(
            "get_group_file_url", _account_id=self._account_id,
            group_id=int(group_id), file_id=file_id,
        )

    async def get_private_file_url(
        self, *, user_id: Union[str, int], file_id: str
    ) -> dict[str, Any]:
        """获取私聊文件下载链接"""
        return await self._adapter.call_api(
            "get_private_file_url", _account_id=self._account_id,
            user_id=int(user_id), file_id=file_id,
        )

    async def get_group_root_files(self, *, group_id: Union[str, int]) -> dict[str, Any]:
        """获取群根目录文件列表"""
        return await self._adapter.call_api(
            "get_group_root_files", _account_id=self._account_id, group_id=int(group_id),
        )

    async def get_group_files_by_folder(
        self, *, group_id: Union[str, int], folder_id: str
    ) -> dict[str, Any]:
        """获取群子目录文件列表"""
        return await self._adapter.call_api(
            "get_group_files_by_folder", _account_id=self._account_id,
            group_id=int(group_id), folder_id=folder_id,
        )

    async def create_group_file_folder(
        self, *, group_id: Union[str, int], name: str
    ) -> dict[str, Any]:
        """创建群文件夹"""
        return await self._adapter.call_api(
            "create_group_file_folder", _account_id=self._account_id,
            group_id=int(group_id), name=name,
        )

    async def delete_group_file(
        self, *, group_id: Union[str, int], file_id: str
    ) -> dict[str, Any]:
        """删除群文件"""
        return await self._adapter.call_api(
            "delete_group_file", _account_id=self._account_id,
            group_id=int(group_id), file_id=file_id,
        )

    # ==================== 群相册 ====================

    async def get_group_album_list(self, *, group_id: Union[str, int]) -> dict[str, Any]:
        """获取群相册列表"""
        return await self._adapter.call_api(
            "get_group_album_list", _account_id=self._account_id, group_id=int(group_id),
        )

    async def get_group_album_media_list(
        self, *, group_id: Union[str, int], album_id: str = ""
    ) -> dict[str, Any]:
        """获取群相册媒体列表"""
        return await self._adapter.call_api(
            "get_group_album_media_list", _account_id=self._account_id,
            group_id=int(group_id), album_id=album_id,
        )

    # ==================== QQ 空间 ====================

    async def send_qzone_msg(self, *, content: str) -> dict[str, Any]:
        """发表 QQ 空间说说（纯文字）"""
        return await self._adapter.call_api(
            "send_qzone_msg", _account_id=self._account_id, content=content,
        )

    async def get_qzone_msg_list(self) -> dict[str, Any]:
        """获取 QQ 空间说说列表"""
        return await self._adapter.call_api(
            "get_qzone_msg_list", _account_id=self._account_id
        )

    async def get_qzone_feeds(self, *, page_num: int = 1) -> dict[str, Any]:
        """
        获取 QQ 空间好友动态

        SnowLuma 后端校验 page_num ≥ 1（签名与后端校验同步：
        默认值取 1，非正值自动钳制为 1，避免不传参时报错）。

        :param page_num: 页码（≥1）
        """
        page_num = max(1, int(page_num))
        return await self._adapter.call_api(
            "get_qzone_feeds", _account_id=self._account_id, page_num=page_num,
        )

    async def like_qzone(self, *, tid: str) -> dict[str, Any]:
        """给 QQ 空间说说点赞"""
        return await self._adapter.call_api(
            "like_qzone", _account_id=self._account_id, tid=tid,
        )

    async def unlike_qzone(self, *, tid: str) -> dict[str, Any]:
        """取消 QQ 空间说说点赞"""
        return await self._adapter.call_api(
            "unlike_qzone", _account_id=self._account_id, tid=tid,
        )

    async def comment_qzone(self, *, tid: str, content: str) -> dict[str, Any]:
        """评论 QQ 空间说说"""
        return await self._adapter.call_api(
            "comment_qzone", _account_id=self._account_id, tid=tid, content=content,
        )

    async def delete_qzone_msg(self, *, tid: str) -> dict[str, Any]:
        """删除 QQ 空间说说"""
        return await self._adapter.call_api(
            "delete_qzone_msg", _account_id=self._account_id, tid=tid,
        )

    # ==================== 合并转发 ====================

    async def get_forward_msg(
        self,
        *,
        id: Union[str, int, None] = None,
        message_id: Union[str, int, None] = None,
    ) -> dict[str, Any]:
        """获取合并转发消息"""
        params: dict[str, Any] = {}
        if id is not None:
            params["id"] = str(id)
        if message_id is not None:
            params["message_id"] = int(message_id)
        return await self._adapter.call_api(
            "get_forward_msg", _account_id=self._account_id, **params
        )

    async def upload_forward_msg(
        self, *, messages: list[dict]
    ) -> dict[str, Any]:
        """上传合并转发消息，获取 resid"""
        return await self._adapter.call_api(
            "upload_forward_msg", _account_id=self._account_id, messages=messages,
        )

    # ==================== 媒体 / OCR ====================

    async def ocr_image(self, *, image: str) -> dict[str, Any]:
        """OCR 图片识别"""
        return await self._adapter.call_api(
            "ocr_image", _account_id=self._account_id, image=image,
        )

    async def get_image(self, *, file: str) -> dict[str, Any]:
        """获取图片信息（缓存）"""
        return await self._adapter.call_api(
            "get_image", _account_id=self._account_id, file=file,
        )

    async def get_record(
        self, *, file: str, out_format: str = "mp3"
    ) -> dict[str, Any]:
        """获取语音信息并转码"""
        return await self._adapter.call_api(
            "get_record", _account_id=self._account_id, file=file, out_format=out_format,
        )

    async def fetch_ptt_text(self, *, file: str) -> dict[str, Any]:
        """语音转文字"""
        return await self._adapter.call_api(
            "fetch_ptt_text", _account_id=self._account_id, file=file,
        )

    # ==================== 账号信息 / 凭证 ====================

    async def get_cookies(self, *, domain: str = "") -> dict[str, Any]:
        """获取 Cookies"""
        return await self._adapter.call_api(
            "get_cookies", _account_id=self._account_id, domain=domain,
        )

    async def get_csrf_token(self) -> dict[str, Any]:
        """获取 CSRF 令牌"""
        return await self._adapter.call_api(
            "get_csrf_token", _account_id=self._account_id
        )

    async def get_credentials(self, *, domain: str = "") -> dict[str, Any]:
        """获取凭证"""
        return await self._adapter.call_api(
            "get_credentials", _account_id=self._account_id, domain=domain,
        )

    async def get_clientkey(self) -> dict[str, Any]:
        """获取 clientkey"""
        return await self._adapter.call_api(
            "get_clientkey", _account_id=self._account_id
        )

    async def nc_get_user_status(self, *, user_id: Union[str, int]) -> dict[str, Any]:
        """获取用户在线/扩展状态"""
        return await self._adapter.call_api(
            "nc_get_user_status", _account_id=self._account_id, user_id=int(user_id),
        )

    # ==================== 资料设置 ====================

    async def set_qq_avatar(self, *, file: str) -> dict[str, Any]:
        """设置 QQ 头像"""
        return await self._adapter.call_api(
            "set_qq_avatar", _account_id=self._account_id, file=file,
        )

    async def set_self_longnick(self, *, nick: str) -> dict[str, Any]:
        """设置个性签名"""
        return await self._adapter.call_api(
            "set_self_longnick", _account_id=self._account_id, longNick=nick,
        )

    async def set_qq_profile(self, **profile: Any) -> dict[str, Any]:
        """设置 QQ 资料"""
        return await self._adapter.call_api(
            "set_qq_profile", _account_id=self._account_id, **profile,
        )

    # ==================== 下载 / 文件 ====================

    async def download_file(self, *, url: str, thread_cnt: int = 1) -> dict[str, Any]:
        """下载文件到服务器"""
        return await self._adapter.call_api(
            "download_file", _account_id=self._account_id, url=url, thread_cnt=thread_cnt,
        )

    async def get_rkey(self) -> dict[str, Any]:
        """获取下载 rkey"""
        return await self._adapter.call_api("get_rkey", _account_id=self._account_id)
