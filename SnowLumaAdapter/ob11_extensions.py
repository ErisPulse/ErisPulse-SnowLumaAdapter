"""
OneBot11 协议扩展动作（NapCat / SnowLuma / Lagrange 通用）

将这些 OB11 协议级扩展封装为类型化方法，提供 IDE 补全。
各适配器的 Api 类可通过多继承混入：

    class Api(BaseAdapter.Api, OB11ExtensionApi):
        ...

所有方法不加平台前缀，直接委托给 call_api(action_name, ...)，
确保 NapCat/SnowLuma/Lagrange 等 OB11 后端之间可移植。

SnowLuma 特有动作（群相册上传/系统表情/流式接口/闪传/收藏表情等）
见 snowluma_extensions.py 的 SnowLumaExtensionApi。

{!--< tips >!--}
1. 方法签名与参数名以官方动作目录（catalog.json，200 个动作）为准，
   服务端未实现的动作也一并封装并在 docstring 注明
2. 完整动作可通过 Api.call("action_name", ...) 调用
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

    async def friend_poke(
        self, *, user_id: Union[str, int], target_id: Union[str, int, None] = None
    ) -> dict[str, Any]:
        """
        好友拍一拍

        :param target_id: 被拍对象（可选，双击自己时省略）
        """
        params: dict[str, Any] = {"user_id": int(user_id)}
        if target_id is not None:
            params["target_id"] = int(target_id)
        return await self._adapter.call_api("friend_poke", _account_id=self._account_id, **params)

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
        self,
        *,
        message_id: Union[str, int],
        emoji_id: Union[str, int],
        set: bool = True,
    ) -> dict[str, Any]:
        """
        设置消息表情回应

        :param message_id: 消息 ID
        :param emoji_id: 表情 ID
        :param set: True 添加回应，False 取消回应
        """
        return await self._adapter.call_api(
            "set_msg_emoji_like", _account_id=self._account_id,
            message_id=int(message_id), emoji_id=str(emoji_id), set=set,
        )

    async def get_emoji_likes(
        self, *, message_id: Union[str, int], emoji_id: Union[str, int]
    ) -> dict[str, Any]:
        """
        获取表情回应用户列表

        :param emoji_id: 表情 ID（服务端必填）
        """
        return await self._adapter.call_api(
            "get_emoji_likes", _account_id=self._account_id,
            message_id=int(message_id), emoji_id=str(emoji_id),
        )

    async def get_msg_emoji_likes(self, *, message_id: Union[str, int]) -> dict[str, Any]:
        """获取一条消息的全部表情回应（每个表情的编号、数量与用户列表）"""
        return await self._adapter.call_api(
            "get_msg_emoji_likes", _account_id=self._account_id, message_id=int(message_id),
        )

    async def fetch_emoji_like(
        self,
        *,
        message_id: Union[str, int],
        emoji_id: Union[str, int],
        count: int = 10,
        cookie: str = "",
    ) -> dict[str, Any]:
        """
        获取表情回应用户（NapCat 分页形状）

        :param emoji_id: 表情 ID（线上参数名为 emojiId）
        :param count: 本页数量
        :param cookie: 分页游标（上一页响应返回）
        """
        return await self._adapter.call_api(
            "fetch_emoji_like", _account_id=self._account_id,
            message_id=int(message_id), emojiId=str(emoji_id),
            count=count, cookie=cookie,
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
        message_id: Union[str, int],
        target_id: Union[str, int, None] = None,
    ) -> dict[str, Any]:
        """
        标记消息已读（服务端按消息自动路由群聊/私聊）

        :param target_id: 可选目标 ID（群号或好友 QQ 号）
        """
        params: dict[str, Any] = {"message_id": int(message_id)}
        if target_id is not None:
            params["target_id"] = int(target_id)
        return await self._adapter.call_api(
            "mark_msg_as_read", _account_id=self._account_id, **params
        )

    async def mark_group_msg_as_read(
        self,
        *,
        message_id: Union[str, int],
        group_id: Union[str, int, None] = None,
    ) -> dict[str, Any]:
        """标记群消息已读"""
        params: dict[str, Any] = {"message_id": int(message_id)}
        if group_id is not None:
            params["group_id"] = int(group_id)
        return await self._adapter.call_api(
            "mark_group_msg_as_read", _account_id=self._account_id, **params
        )

    async def mark_private_msg_as_read(
        self,
        *,
        message_id: Union[str, int],
        user_id: Union[str, int, None] = None,
    ) -> dict[str, Any]:
        """标记私聊消息已读"""
        params: dict[str, Any] = {"message_id": int(message_id)}
        if user_id is not None:
            params["user_id"] = int(user_id)
        return await self._adapter.call_api(
            "mark_private_msg_as_read", _account_id=self._account_id, **params
        )

    async def mark_all_as_read(self) -> dict[str, Any]:
        """标记全部已读"""
        return await self._adapter.call_api(
            "_mark_all_as_read", _account_id=self._account_id
        )

    async def set_online_status(
        self,
        *,
        status: int,
        ext_status: int = 0,
        battery_status: int = 100,
    ) -> dict[str, Any]:
        """
        设置在线状态

        :param ext_status: 扩展状态码
        :param battery_status: 电量状态
        """
        return await self._adapter.call_api(
            "set_online_status", _account_id=self._account_id,
            status=int(status), ext_status=int(ext_status),
            battery_status=int(battery_status),
        )

    async def set_diy_online_status(
        self, *, face_id: int, face_type: int = 1, wording: str = ""
    ) -> dict[str, Any]:
        """
        设置自定义在线状态

        :param face_id: 状态表情编号
        :param face_type: 表情类型
        :param wording: 状态文字
        """
        return await self._adapter.call_api(
            "set_diy_online_status", _account_id=self._account_id,
            face_id=int(face_id), face_type=int(face_type), wording=wording,
        )

    async def set_input_status(
        self, *, user_id: Union[str, int], event_type: int = 1
    ) -> dict[str, Any]:
        """
        设置输入状态（对方可见"正在输入..."）

        :param event_type: 状态码（1=正在输入）
        """
        return await self._adapter.call_api(
            "set_input_status", _account_id=self._account_id,
            user_id=int(user_id), event_type=int(event_type),
        )

    async def nc_get_user_status(self, *, user_id: Union[str, int]) -> dict[str, Any]:
        """获取用户在线/扩展状态"""
        return await self._adapter.call_api(
            "nc_get_user_status", _account_id=self._account_id, user_id=int(user_id),
        )

    async def get_online_clients(self, *, no_cache: bool = False) -> dict[str, Any]:
        """
        获取在线客户端

        QQ 当前仅暴露本地快照，no_cache=True 会明确失败。
        """
        return await self._adapter.call_api(
            "get_online_clients", _account_id=self._account_id, no_cache=no_cache,
        )

    # ==================== 消息历史 ====================

    async def get_group_msg_history(
        self,
        *,
        group_id: Union[str, int],
        message_id: int = 0,
        count: int = 20,
        reverse_order: bool = True,
    ) -> dict[str, Any]:
        """
        获取群消息历史

        :param message_id: 锚点消息 ID（0 表示从最新开始）
        :param reverse_order: 仅在 message_id 非 0 时生效；True 返回锚点及更旧消息
        """
        return await self._adapter.call_api(
            "get_group_msg_history", _account_id=self._account_id,
            group_id=int(group_id), message_id=int(message_id),
            count=count, reverse_order=reverse_order,
        )

    async def get_friend_msg_history(
        self,
        *,
        user_id: Union[str, int],
        message_id: int = 0,
        count: int = 20,
        reverse_order: bool = True,
    ) -> dict[str, Any]:
        """
        获取好友消息历史（无锚点时从服务器获取最新双向记录）

        :param message_id: 锚点消息 ID（0 表示从服务器拉最新）
        :param reverse_order: 仅在 message_id 非 0 时生效；True 返回锚点及更旧消息
        """
        return await self._adapter.call_api(
            "get_friend_msg_history", _account_id=self._account_id,
            user_id=int(user_id), message_id=int(message_id),
            count=count, reverse_order=reverse_order,
        )

    # ==================== 群管理扩展 ====================

    async def set_group_reaction(
        self,
        *,
        group_id: Union[str, int, None] = None,
        message_id: Union[str, int],
        code: Union[str, int],
        is_set: bool = True,
    ) -> dict[str, Any]:
        """
        群聊表情回应

        :param group_id: 群号（可选，服务端可从消息推断）
        :param code: 表情代码
        :param is_set: True 添加回应，False 取消回应（线上参数名为 is_set）
        """
        params: dict[str, Any] = {
            "message_id": int(message_id),
            "code": str(code),
            "is_set": is_set,
        }
        if group_id is not None:
            params["group_id"] = int(group_id)
        return await self._adapter.call_api(
            "set_group_reaction", _account_id=self._account_id, **params
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

    async def get_group_signed_list(self, *, group_id: Union[str, int]) -> dict[str, Any]:
        """获取群今日打卡列表"""
        return await self._adapter.call_api(
            "get_group_signed_list", _account_id=self._account_id, group_id=int(group_id),
        )

    async def set_group_todo(
        self, *, group_id: Union[str, int], message_id: Union[str, int]
    ) -> dict[str, Any]:
        """
        设置群待办

        :param message_id: 作为待办的群消息 ID（服务端以消息为待办载体）
        """
        return await self._adapter.call_api(
            "set_group_todo", _account_id=self._account_id,
            group_id=int(group_id), message_id=int(message_id),
        )

    async def cancel_group_todo(
        self, *, group_id: Union[str, int], message_id: Union[str, int]
    ) -> dict[str, Any]:
        """取消群待办"""
        return await self._adapter.call_api(
            "cancel_group_todo", _account_id=self._account_id,
            group_id=int(group_id), message_id=int(message_id),
        )

    async def complete_group_todo(
        self, *, group_id: Union[str, int], message_id: Union[str, int]
    ) -> dict[str, Any]:
        """完成群待办"""
        return await self._adapter.call_api(
            "complete_group_todo", _account_id=self._account_id,
            group_id=int(group_id), message_id=int(message_id),
        )

    async def get_group_todo_list(self, *, group_id: Union[str, int]) -> dict[str, Any]:
        """获取群待办列表"""
        return await self._adapter.call_api(
            "get_group_todo_list", _account_id=self._account_id, group_id=int(group_id),
        )

    async def get_group_info_ex(
        self, *, group_id: Union[str, int], no_cache: bool = False
    ) -> dict[str, Any]:
        """获取群信息（扩展）"""
        return await self._adapter.call_api(
            "get_group_info_ex", _account_id=self._account_id,
            group_id=int(group_id), no_cache=no_cache,
        )

    async def get_group_detail_info(
        self, *, group_id: Union[str, int], no_cache: bool = False
    ) -> dict[str, Any]:
        """获取群详细信息"""
        return await self._adapter.call_api(
            "get_group_detail_info", _account_id=self._account_id,
            group_id=int(group_id), no_cache=no_cache,
        )

    async def get_group_admin_settings(self, *, group_id: Union[str, int]) -> dict[str, Any]:
        """获取群管理设置的当前值（与设置接口字段对齐）"""
        return await self._adapter.call_api(
            "get_group_admin_settings", _account_id=self._account_id, group_id=int(group_id),
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

    async def get_group_system_msg(
        self,
        *,
        group_id: Union[str, int, None] = None,
        only_pending: bool = False,
        count: int = 50,
    ) -> dict[str, Any]:
        """
        获取群系统消息（加群/邀请等）

        :param group_id: 群号（可选，省略返回全部群）
        :param only_pending: 仅未处理记录
        :param count: 每个收件箱最多读取的记录数
        """
        params: dict[str, Any] = {"only_pending": only_pending, "count": count}
        if group_id is not None:
            params["group_id"] = int(group_id)
        return await self._adapter.call_api(
            "get_group_system_msg", _account_id=self._account_id, **params
        )

    async def set_group_add_option(
        self,
        *,
        group_id: Union[str, int],
        add_type: int = 0,
        group_question: Union[str, None] = None,
        group_answer: Union[str, None] = None,
    ) -> dict[str, Any]:
        """
        设置加群选项

        :param add_type: 加群方式（0=允许任何人，1=需要验证，2=不允许任何人，3=需要回答问题）
        :param group_question: 验证问题（add_type=3 时）
        :param group_answer: 验证答案（add_type=3 时）
        """
        params: dict[str, Any] = {"group_id": int(group_id), "add_type": int(add_type)}
        if group_question is not None:
            params["group_question"] = str(group_question)
        if group_answer is not None:
            params["group_answer"] = str(group_answer)
        return await self._adapter.call_api(
            "set_group_add_option", _account_id=self._account_id, **params
        )

    async def set_group_anonymous(
        self, *, group_id: Union[str, int], enable: bool = True
    ) -> dict[str, Any]:
        """匿名开关（SnowLuma 服务端未实现，恒返回 ok）"""
        return await self._adapter.call_api(
            "set_group_anonymous", _account_id=self._account_id,
            group_id=int(group_id), enable=enable,
        )

    async def set_group_anonymous_ban(
        self, *, group_id: Union[str, int], anonymous_flag: str, duration: int = 1800
    ) -> dict[str, Any]:
        """匿名禁言（SnowLuma 服务端未实现，恒返回 ok）"""
        return await self._adapter.call_api(
            "set_group_anonymous_ban", _account_id=self._account_id,
            group_id=int(group_id), anonymous_flag=str(anonymous_flag), duration=int(duration),
        )

    async def set_group_kick_members(
        self,
        *,
        group_id: Union[str, int],
        user_id: list[Union[str, int]],
        reject_add_request: bool = False,
    ) -> dict[str, Any]:
        """
        批量踢出群成员

        :param user_id: 要踢出的 QQ 号列表
        :param reject_add_request: 是否拒绝再次加群
        """
        return await self._adapter.call_api(
            "set_group_kick_members", _account_id=self._account_id,
            group_id=int(group_id),
            user_id=[int(u) for u in user_id],
            reject_add_request=reject_add_request,
        )

    async def set_group_member_invite_policy(
        self, *, group_id: Union[str, int], policy: str
    ) -> dict[str, Any]:
        """
        设置群成员邀请策略

        :param policy: "disabled" | "require_approval" | "no_approval" | "no_approval_under_100"
        """
        return await self._adapter.call_api(
            "set_group_member_invite_policy", _account_id=self._account_id,
            group_id=int(group_id), policy=policy,
        )

    async def set_group_member_permissions(
        self,
        *,
        group_id: Union[str, int],
        allow_member_upload_album: Union[bool, None] = None,
        allow_member_temporary_session: Union[bool, None] = None,
        allow_member_create_group: Union[bool, None] = None,
    ) -> dict[str, Any]:
        """
        设置群成员权限（仅群主可改）；传 None 的项不下发
        """
        params: dict[str, Any] = {"group_id": int(group_id)}
        if allow_member_upload_album is not None:
            params["allow_member_upload_album"] = allow_member_upload_album
        if allow_member_temporary_session is not None:
            params["allow_member_temporary_session"] = allow_member_temporary_session
        if allow_member_create_group is not None:
            params["allow_member_create_group"] = allow_member_create_group
        return await self._adapter.call_api(
            "set_group_member_permissions", _account_id=self._account_id, **params
        )

    async def set_group_new_member_history_visibility(
        self, *, group_id: Union[str, int], visible: bool
    ) -> dict[str, Any]:
        """
        设置新成员是否可查看历史消息

        :param visible: True 允许查看历史消息
        """
        return await self._adapter.call_api(
            "set_group_new_member_history_visibility", _account_id=self._account_id,
            group_id=int(group_id), visible=visible,
        )

    async def set_group_search(
        self,
        *,
        group_id: Union[str, int],
        no_finger_open: Union[int, None] = None,
        no_code_finger_open: Union[int, None] = None,
    ) -> dict[str, Any]:
        """
        设置群被搜索方式

        :param no_finger_open: 群指纹搜索开关
        :param no_code_finger_open: 群号搜索开关
        """
        params: dict[str, Any] = {"group_id": int(group_id)}
        if no_finger_open is not None:
            params["no_finger_open"] = int(no_finger_open)
        if no_code_finger_open is not None:
            params["no_code_finger_open"] = int(no_code_finger_open)
        return await self._adapter.call_api(
            "set_group_search", _account_id=self._account_id, **params
        )

    async def set_group_robot_add_option(
        self,
        *,
        group_id: Union[str, int],
        robot_member_switch: Union[int, None] = None,
        robot_member_examine: Union[int, None] = None,
    ) -> dict[str, Any]:
        """
        设置群机器人加群选项

        :param robot_member_switch: 机器人加群开关
        :param robot_member_examine: 机器人加群审核方式
        """
        params: dict[str, Any] = {"group_id": int(group_id)}
        if robot_member_switch is not None:
            params["robot_member_switch"] = int(robot_member_switch)
        if robot_member_examine is not None:
            params["robot_member_examine"] = int(robot_member_examine)
        return await self._adapter.call_api(
            "set_group_robot_add_option", _account_id=self._account_id, **params
        )

    async def add_group_tag(self, *, group_class: int, name: str) -> dict[str, Any]:
        """
        向某个群分类添加资料标签

        :param group_class: 群分类 ID
        :param name: 标签名
        """
        return await self._adapter.call_api(
            "add_group_tag", _account_id=self._account_id,
            group_class=int(group_class), name=name,
        )

    async def delete_group_tag(self, *, group_class: int, name: str) -> dict[str, Any]:
        """从某个群分类移除资料标签"""
        return await self._adapter.call_api(
            "delete_group_tag", _account_id=self._account_id,
            group_class=int(group_class), name=name,
        )

    async def get_group_tags(self, *, group_class: int) -> dict[str, Any]:
        """读取某个群分类下的资料标签"""
        return await self._adapter.call_api(
            "get_group_tags", _account_id=self._account_id, group_class=int(group_class),
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

    async def delete_friend(
        self, *, user_id: Union[str, int], block: bool = False
    ) -> dict[str, Any]:
        """
        删除好友

        :param block: 是否同时拉黑
        """
        return await self._adapter.call_api(
            "delete_friend", _account_id=self._account_id,
            user_id=int(user_id), block=block,
        )

    async def set_friends_category(
        self,
        *,
        uin: Union[str, int],
        category_id: Union[int, None] = None,
        category_name: Union[str, None] = None,
    ) -> dict[str, Any]:
        """
        移动好友到指定分组（category_id 与 category_name 二选一）

        :param uin: 要移动的好友 QQ 号（线上参数名为 uin）
        """
        params: dict[str, Any] = {"uin": int(uin)}
        if category_id is not None:
            params["categoryId"] = int(category_id)
        if category_name is not None:
            params["categoryName"] = str(category_name)
        return await self._adapter.call_api(
            "set_friends_category", _account_id=self._account_id, **params
        )

    async def get_doubt_friends_add_request(self, *, count: int = 50) -> dict[str, Any]:
        """
        获取可疑好友申请（uid 可作为处理用 flag）
        """
        return await self._adapter.call_api(
            "get_doubt_friends_add_request", _account_id=self._account_id, count=count,
        )

    async def set_doubt_friends_add_request(
        self, *, flag: str, approve: bool = True
    ) -> dict[str, Any]:
        """处理可疑好友申请"""
        return await self._adapter.call_api(
            "set_doubt_friends_add_request", _account_id=self._account_id,
            flag=str(flag), approve=approve,
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

    async def get_recent_contact(self, *, count: int = 10) -> dict[str, Any]:
        """获取最近会话（SnowLuma 为占位实现，恒返回空数组）"""
        return await self._adapter.call_api(
            "get_recent_contact", _account_id=self._account_id, count=count
        )

    async def get_group_ignore_add_request(self) -> dict[str, Any]:
        """获取被忽略的入群请求（NapCat 字段命名）"""
        return await self._adapter.call_api(
            "get_group_ignore_add_request", _account_id=self._account_id
        )

    async def get_group_ignored_notifies(self) -> dict[str, Any]:
        """获取被过滤的入群请求"""
        return await self._adapter.call_api(
            "get_group_ignored_notifies", _account_id=self._account_id
        )

    # ==================== 群文件 ====================

    async def get_group_file_url(
        self,
        *,
        group_id: Union[str, int],
        file_id: str,
        busid: Any = None,
    ) -> dict[str, Any]:
        """
        获取群文件下载链接

        :param busid: 文件 busid（可选）
        """
        params: dict[str, Any] = {"group_id": int(group_id), "file_id": str(file_id)}
        if busid is not None:
            params["busid"] = busid
        return await self._adapter.call_api(
            "get_group_file_url", _account_id=self._account_id, **params
        )

    async def get_private_file_url(
        self,
        *,
        file_id: str,
        user_id: Union[str, int, None] = None,
        file_hash: str = "",
    ) -> dict[str, Any]:
        """
        获取私聊文件下载链接

        :param user_id: 好友 QQ 号（可选）
        :param file_hash: 文件哈希（可选）
        """
        params: dict[str, Any] = {"file_id": str(file_id), "file_hash": file_hash}
        if user_id is not None:
            params["user_id"] = int(user_id)
        return await self._adapter.call_api(
            "get_private_file_url", _account_id=self._account_id, **params
        )

    async def get_group_file_system_info(self, *, group_id: Union[str, int]) -> dict[str, Any]:
        """获取群文件系统信息（文件数量与容量）"""
        return await self._adapter.call_api(
            "get_group_file_system_info", _account_id=self._account_id, group_id=int(group_id),
        )

    async def get_group_root_files(self, *, group_id: Union[str, int]) -> dict[str, Any]:
        """获取群根目录文件列表"""
        return await self._adapter.call_api(
            "get_group_root_files", _account_id=self._account_id, group_id=int(group_id),
        )

    async def get_group_files_by_folder(
        self,
        *,
        group_id: Union[str, int],
        folder_id: str = "",
    ) -> dict[str, Any]:
        """
        获取群子目录文件列表

        :param folder_id: 目录 ID（空串表示根目录）
        """
        return await self._adapter.call_api(
            "get_group_files_by_folder", _account_id=self._account_id,
            group_id=int(group_id), folder_id=folder_id,
        )

    async def create_group_file_folder(
        self, *, group_id: Union[str, int], name: str, parent_id: str = "/"
    ) -> dict[str, Any]:
        """
        创建群文件夹

        :param parent_id: 父目录 ID（默认根目录）
        """
        return await self._adapter.call_api(
            "create_group_file_folder", _account_id=self._account_id,
            group_id=int(group_id), name=name, parent_id=parent_id,
        )

    async def delete_group_file(
        self, *, group_id: Union[str, int], file_id: str
    ) -> dict[str, Any]:
        """删除群文件"""
        return await self._adapter.call_api(
            "delete_group_file", _account_id=self._account_id,
            group_id=int(group_id), file_id=str(file_id),
        )

    async def delete_group_file_folder(
        self, *, group_id: Union[str, int], folder_id: str
    ) -> dict[str, Any]:
        """删除群文件夹（服务端亦接受别名 delete_group_folder）"""
        return await self._adapter.call_api(
            "delete_group_file_folder", _account_id=self._account_id,
            group_id=int(group_id), folder_id=str(folder_id),
        )

    async def rename_group_file(
        self,
        *,
        group_id: Union[str, int],
        file_id: str,
        new_name: str,
        current_parent_directory: str = "/",
    ) -> dict[str, Any]:
        """
        重命名群文件

        :param current_parent_directory: 文件当前所在目录
        """
        return await self._adapter.call_api(
            "rename_group_file", _account_id=self._account_id,
            group_id=int(group_id), file_id=str(file_id),
            new_name=new_name, current_parent_directory=current_parent_directory,
        )

    async def rename_group_file_folder(
        self,
        *,
        group_id: Union[str, int],
        folder_id: str,
        new_folder_name: str = "",
    ) -> dict[str, Any]:
        """
        重命名群文件夹

        :param new_folder_name: 新文件夹名（也可用 name 字段，二者等价）
        """
        return await self._adapter.call_api(
            "rename_group_file_folder", _account_id=self._account_id,
            group_id=int(group_id), folder_id=str(folder_id),
            new_folder_name=new_folder_name,
        )

    async def move_group_file(
        self,
        *,
        group_id: Union[str, int],
        file_id: str,
        parent_directory: str,
        target_directory: str,
    ) -> dict[str, Any]:
        """
        移动群文件

        :param parent_directory: 文件当前所在目录
        :param target_directory: 目标目录
        """
        return await self._adapter.call_api(
            "move_group_file", _account_id=self._account_id,
            group_id=int(group_id), file_id=str(file_id),
            parent_directory=parent_directory, target_directory=target_directory,
        )

    async def trans_group_file(
        self, *, group_id: Union[str, int], file_id: str
    ) -> dict[str, Any]:
        """转存群文件到本账号"""
        return await self._adapter.call_api(
            "trans_group_file", _account_id=self._account_id,
            group_id=int(group_id), file_id=str(file_id),
        )

    # ==================== 群信息 ====================

    async def get_group_honor_info(
        self, *, group_id: Union[str, int], type: Union[str, None] = None
    ) -> dict[str, Any]:
        """
        获取群荣誉信息（龙王/群聊之焰等）

        :param type: 荣誉类型（talkative=龙王，performer=群聊之焰，
            legend=传奇，strong_newbie=活跃新星，emotion=快乐之源；省略返回全部）
        """
        params: dict[str, Any] = {"group_id": int(group_id)}
        if type is not None:
            params["type"] = str(type)
        return await self._adapter.call_api(
            "get_group_honor_info", _account_id=self._account_id, **params
        )

    async def get_group_share_link(
        self,
        *,
        group_id: Union[str, int],
        need_short_url: bool = True,
        src_id: int = 73,
        additional_param: str = "",
    ) -> dict[str, Any]:
        """
        获取群分享链接（可作为群二维码内容）

        :param need_short_url: 是否获取短链接
        :param src_id: 来源标识（兼容参数）
        :param additional_param: 附加参数
        """
        return await self._adapter.call_api(
            "get_group_share_link", _account_id=self._account_id,
            group_id=int(group_id), need_short_url=need_short_url,
            src_id=int(src_id), additional_param=additional_param,
        )

    # ==================== 群相册（列表；上传等 SnowLuma 特有动作见 SnowLumaExtensionApi） ====================

    async def get_group_album_list(self, *, group_id: Union[str, int]) -> dict[str, Any]:
        """获取群相册列表"""
        return await self._adapter.call_api(
            "get_group_album_list", _account_id=self._account_id, group_id=int(group_id),
        )

    async def get_group_album_media_list(
        self, *, group_id: Union[str, int], album_id: str, attach_info: str = ""
    ) -> dict[str, Any]:
        """
        获取群相册媒体列表

        :param album_id: 相册 ID（服务端必填）
        :param attach_info: 下一页分页游标（上一页响应返回）
        """
        return await self._adapter.call_api(
            "get_group_album_media_list", _account_id=self._account_id,
            group_id=int(group_id), album_id=str(album_id), attach_info=attach_info,
        )

    # ==================== QQ 空间 ====================

    async def send_qzone_msg(
        self,
        *,
        content: str,
        images: Union[list[str], None] = None,
        ugc_right: int = 1,
        target_uins: Union[list[Union[str, int]], None] = None,
    ) -> dict[str, Any]:
        """
        发表 QQ 空间说说（纯文字或带图；传 images 自动上传）

        :param images: 图片数组，支持 file:// http:// base64://
        :param ugc_right: 查看权限：1=所有人可见，4=好友可见，16=部分好友可见，
            64=仅自己可见，128=部分好友不可见
        :param target_uins: 权限作用 QQ 号数组（ugc_right=16 为可见名单，128 为不可见名单）
        """
        params: dict[str, Any] = {"content": content, "ugc_right": int(ugc_right)}
        if images is not None:
            params["images"] = images
        if target_uins is not None:
            params["target_uins"] = [int(u) for u in target_uins]
        return await self._adapter.call_api(
            "send_qzone_msg", _account_id=self._account_id, **params
        )

    async def get_qzone_msg_list(
        self,
        *,
        target_uin: Union[str, int, None] = None,
        pos: int = 0,
        num: int = 20,
    ) -> dict[str, Any]:
        """
        获取 QQ 空间说说列表（默认机器人自己的空间）

        :param target_uin: 目标 QQ 号（省略则取机器人自己）
        :param pos: 起始偏移
        :param num: 本页数量
        """
        params: dict[str, Any] = {"pos": int(pos), "num": int(num)}
        if target_uin is not None:
            params["target_uin"] = int(target_uin)
        return await self._adapter.call_api(
            "get_qzone_msg_list", _account_id=self._account_id, **params
        )

    async def get_qzone_feeds(self, *, page_num: int = 1, count: int = 10) -> dict[str, Any]:
        """
        获取 QQ 空间好友动态

        SnowLuma 后端校验 page_num ≥ 1（签名与后端校验同步：
        默认值取 1，非正值自动钳制为 1，避免不传参时报错）。
        深翻页需时间游标，服务端暂未实现。

        :param page_num: 页码（≥1，仅首页可靠）
        :param count: 本页数量
        """
        page_num = max(1, int(page_num))
        return await self._adapter.call_api(
            "get_qzone_feeds", _account_id=self._account_id,
            page_num=page_num, count=count,
        )

    async def like_qzone(
        self,
        *,
        tid: str,
        target_uin: Union[str, int, None] = None,
        abstime: int = 0,
    ) -> dict[str, Any]:
        """
        给 QQ 空间说说点赞

        :param target_uin: 说说所属 QQ 号（省略则为机器人自己）
        :param abstime: 说说发表时间（unix 秒），传真实值更可靠
        """
        params: dict[str, Any] = {"tid": str(tid), "abstime": int(abstime)}
        if target_uin is not None:
            params["target_uin"] = int(target_uin)
        return await self._adapter.call_api(
            "like_qzone", _account_id=self._account_id, **params
        )

    async def unlike_qzone(
        self,
        *,
        tid: str,
        target_uin: Union[str, int, None] = None,
        abstime: int = 0,
    ) -> dict[str, Any]:
        """
        取消对一条 QQ 空间说说的点赞（取消赞端点待真机核实）

        :param target_uin: 说说所属 QQ 号（省略则为机器人自己）
        :param abstime: 说说发表时间（unix 秒），传真实值更可靠
        """
        params: dict[str, Any] = {"tid": str(tid), "abstime": int(abstime)}
        if target_uin is not None:
            params["target_uin"] = int(target_uin)
        return await self._adapter.call_api(
            "unlike_qzone", _account_id=self._account_id, **params
        )

    async def comment_qzone(
        self,
        *,
        tid: str,
        content: str,
        target_uin: Union[str, int, None] = None,
        images: Union[list[str], None] = None,
    ) -> dict[str, Any]:
        """
        评论 QQ 空间说说（支持纯文字或带图；传 images 自动上传）

        :param target_uin: 说说所属 QQ 号（省略则为机器人自己）
        :param images: 图片数组，支持 file:// http:// base64://
        """
        params: dict[str, Any] = {"tid": str(tid), "content": content}
        if target_uin is not None:
            params["target_uin"] = int(target_uin)
        if images is not None:
            params["images"] = images
        return await self._adapter.call_api(
            "comment_qzone", _account_id=self._account_id, **params
        )

    async def delete_qzone_msg(self, *, tid: str) -> dict[str, Any]:
        """删除 QQ 空间说说"""
        return await self._adapter.call_api(
            "delete_qzone_msg", _account_id=self._account_id, tid=str(tid),
        )

    # ==================== 合并转发 / 单条转发 ====================

    async def get_forward_msg(
        self,
        *,
        id: Union[str, int, None] = None,
        message_id: Union[str, int, None] = None,
    ) -> dict[str, Any]:
        """获取合并转发消息（id 或 message_id 至少传一个；message_id 线上为字符串）"""
        params: dict[str, Any] = {}
        if id is not None:
            params["id"] = str(id)
        if message_id is not None:
            params["message_id"] = str(message_id)
        return await self._adapter.call_api(
            "get_forward_msg", _account_id=self._account_id, **params
        )

    async def upload_forward_msg(
        self,
        *,
        messages: Union[list[dict], None] = None,
        message: Union[list[dict], None] = None,
        group_id: Union[str, int, None] = None,
    ) -> dict[str, Any]:
        """
        上传合并转发消息，获取 resid

        :param messages: 转发节点数组（与 message 二选一）
        :param message: 转发节点数组（与 messages 二选一）
        :param group_id: 群号（可选，影响上传上下文）
        """
        params: dict[str, Any] = {}
        if messages is not None:
            params["messages"] = messages
        if message is not None:
            params["message"] = message
        if group_id is not None:
            params["group_id"] = int(group_id)
        return await self._adapter.call_api(
            "upload_forward_msg", _account_id=self._account_id, **params
        )

    async def send_forward_msg(
        self,
        *,
        messages: Union[list[dict], None] = None,
        message: Union[list[dict], None] = None,
        message_type: Union[str, None] = None,
        group_id: Union[str, int, None] = None,
        user_id: Union[str, int, None] = None,
        source: Union[str, None] = None,
        summary: Union[str, None] = None,
        prompt: Union[str, None] = None,
        news: Any = None,
    ) -> dict[str, Any]:
        """
        发送合并转发（按 message_type/群号自动路由群聊或私聊）

        :param messages: 转发节点数组（与 message 二选一）
        :param source: 外显标题
        :param summary: 外显摘要
        :param prompt: 通知文案
        :param news: 外显预览（列表，最多 4 条）
        """
        params: dict[str, Any] = {}
        if messages is not None:
            params["messages"] = messages
        if message is not None:
            params["message"] = message
        if message_type is not None:
            params["message_type"] = str(message_type)
        if group_id is not None:
            params["group_id"] = int(group_id)
        if user_id is not None:
            params["user_id"] = int(user_id)
        if source is not None:
            params["source"] = str(source)
        if summary is not None:
            params["summary"] = str(summary)
        if prompt is not None:
            params["prompt"] = str(prompt)
        if news is not None:
            params["news"] = news
        return await self._adapter.call_api(
            "send_forward_msg", _account_id=self._account_id, **params
        )

    async def forward_group_single_msg(
        self, *, group_id: Union[str, int], message_id: Union[str, int]
    ) -> dict[str, Any]:
        """转发单条消息到群"""
        return await self._adapter.call_api(
            "forward_group_single_msg", _account_id=self._account_id,
            group_id=int(group_id), message_id=int(message_id),
        )

    async def forward_friend_single_msg(
        self, *, user_id: Union[str, int], message_id: Union[str, int]
    ) -> dict[str, Any]:
        """转发单条消息给好友"""
        return await self._adapter.call_api(
            "forward_friend_single_msg", _account_id=self._account_id,
            user_id=int(user_id), message_id=int(message_id),
        )

    # ==================== Ark 卡片 / 小程序 / 分享链接 ====================

    async def send_ark_share(
        self,
        *,
        user_id: Union[str, int, None] = None,
        group_id: Union[str, int, None] = None,
        phone_number: str = "",
    ) -> dict[str, Any]:
        """
        分享用户/群 Ark 卡片（NapCat 标准名，仅生成卡片 JSON，不发送）

        :returns: { arkMsg } Ark 卡片 JSON 字符串
        """
        params: dict[str, Any] = {"phone_number": phone_number}
        if user_id is not None:
            params["user_id"] = int(user_id)
        if group_id is not None:
            params["group_id"] = int(group_id)
        return await self._adapter.call_api(
            "send_ark_share", _account_id=self._account_id, **params
        )

    async def send_group_ark_share(self, *, group_id: Union[str, int]) -> dict[str, Any]:
        """
        分享群 Ark 卡片（NapCat 标准名，仅生成卡片 JSON，不发送）

        :returns: 群推荐 Ark 卡片 JSON 字符串
        """
        return await self._adapter.call_api(
            "send_group_ark_share", _account_id=self._account_id, group_id=int(group_id),
        )

    async def share_peer(
        self,
        *,
        user_id: Union[str, int, None] = None,
        group_id: Union[str, int, None] = None,
        phone_number: str = "",
    ) -> dict[str, Any]:
        """分享用户/群 Ark 卡片（仅生成卡片 JSON，不发送）"""
        params: dict[str, Any] = {"phone_number": phone_number}
        if user_id is not None:
            params["user_id"] = int(user_id)
        if group_id is not None:
            params["group_id"] = int(group_id)
        return await self._adapter.call_api(
            "share_peer", _account_id=self._account_id, **params
        )

    async def share_group_ex(self, *, group_id: Union[str, int]) -> dict[str, Any]:
        """分享群 Ark 卡片（仅生成卡片 JSON，不发送）"""
        return await self._adapter.call_api(
            "share_group_ex", _account_id=self._account_id, group_id=int(group_id),
        )

    async def send_tuwen_ark(
        self,
        *,
        title: str,
        desc: str,
        jump_url: str,
        user_id: Union[str, int, None] = None,
        group_id: Union[str, int, None] = None,
        summary: str = "[分享]",
        preview_url: str = "https://tangram-1251316161.file.myqcloud.com/files/20210721/e50a8e37e08f29bf1ffc7466e1950690.png",
    ) -> dict[str, Any]:
        """
        发送图文 Ark 卡片（私聊/群聊，二选一传入）

        :param title: 卡片标题
        :param desc: 卡片描述
        :param jump_url: 跳转链接
        :param preview_url: 预览图 URL
        """
        params: dict[str, Any] = {
            "title": title, "desc": desc, "jump_url": jump_url,
            "summary": summary, "preview_url": preview_url,
        }
        if user_id is not None:
            params["user_id"] = int(user_id)
        if group_id is not None:
            params["group_id"] = int(group_id)
        return await self._adapter.call_api(
            "send_tuwen_ark", _account_id=self._account_id, **params
        )

    async def get_mini_app_ark(
        self,
        *,
        type: Union[str, None] = None,
        title: Union[str, None] = None,
        desc: Union[str, None] = None,
        pic_url: Union[str, None] = None,
        jump_url: Union[str, None] = None,
    ) -> dict[str, Any]:
        """
        获取小程序卡片 ark JSON

        传 pic_url/jump_url 时会同时下发 picUrl/jumpUrl 兼容字段。
        """
        params: dict[str, Any] = {}
        if type is not None:
            params["type"] = str(type)
        if title is not None:
            params["title"] = str(title)
        if desc is not None:
            params["desc"] = str(desc)
        if pic_url is not None:
            params["pic_url"] = str(pic_url)
            params["picUrl"] = str(pic_url)
        if jump_url is not None:
            params["jump_url"] = str(jump_url)
            params["jumpUrl"] = str(jump_url)
        return await self._adapter.call_api(
            "get_mini_app_ark", _account_id=self._account_id, **params
        )

    async def get_share_link(self, *, fileset_id: str) -> dict[str, Any]:
        """获取闪传文件分享链接"""
        return await self._adapter.call_api(
            "get_share_link", _account_id=self._account_id, fileset_id=str(fileset_id),
        )

    # ==================== AI 语音 ====================

    async def get_ai_characters(
        self, *, group_id: Union[str, int], chat_type: int = 1
    ) -> dict[str, Any]:
        """
        获取 AI 语音角色（按分类分组，含角色 id、名称与试听 URL）

        :param chat_type: 上下文类型（1=群聊，2=私聊）
        """
        return await self._adapter.call_api(
            "get_ai_characters", _account_id=self._account_id,
            group_id=int(group_id), chat_type=int(chat_type),
        )

    async def get_ai_record(
        self,
        *,
        group_id: Union[str, int],
        character: str,
        text: str,
        chat_type: int = 1,
    ) -> dict[str, Any]:
        """
        生成 AI 语音（不发送，仅生成）

        :param character: AI 语音角色 ID（来自 get_ai_characters）
        :param text: 要合成的文本
        """
        return await self._adapter.call_api(
            "get_ai_record", _account_id=self._account_id,
            group_id=int(group_id), character=str(character),
            text=text, chat_type=int(chat_type),
        )

    async def send_group_ai_record(
        self,
        *,
        group_id: Union[str, int],
        character: str,
        text: str,
        chat_type: int = 1,
    ) -> dict[str, Any]:
        """
        发送 AI 语音到群

        :param character: AI 语音角色 ID（来自 get_ai_characters）
        :param text: 要合成的文本
        """
        return await self._adapter.call_api(
            "send_group_ai_record", _account_id=self._account_id,
            group_id=int(group_id), character=str(character),
            text=text, chat_type=int(chat_type),
        )

    # ==================== 群公告 / 机型 / 装扮 ====================

    async def get_group_notice(self, *, group_id: Union[str, int]) -> dict[str, Any]:
        """获取群公告（普通公告与新成员公告合并数组）"""
        return await self._adapter.call_api(
            "_get_group_notice", _account_id=self._account_id, group_id=int(group_id),
        )

    async def send_group_notice(
        self,
        *,
        group_id: Union[str, int],
        content: str,
        image: str = "",
        pinned: int = 0,
        type: Union[int, None] = None,
        send_to_new_members: Union[bool, None] = None,
        is_show_edit_card: int = 1,
        tip_window_type: int = 1,
        confirm_required: int = 1,
    ) -> dict[str, Any]:
        """
        发送群公告（支持置顶、弹窗、新成员、群昵称引导与确认）

        :param image: 可选公告图片（本地路径、URL 或 base64）
        :param pinned: 1=置顶，0=不置顶
        :param type: 发布类型：1=普通公告，20=新成员公告；建议用 send_to_new_members
        :param send_to_new_members: 是否在成员新加入群时发送（与 type=20 等价）
        :param is_show_edit_card: 是否引导群成员修改群昵称：1=是，0=否
        :param tip_window_type: 弹窗展示：0=开启弹窗，1=关闭弹窗（QQ 原始字段为反向语义）
        :param confirm_required: 是否需要群成员确认收到：1=是，0=否
        """
        params: dict[str, Any] = {
            "group_id": int(group_id),
            "content": content,
            "image": image,
            "pinned": int(pinned),
            "is_show_edit_card": int(is_show_edit_card),
            "tip_window_type": int(tip_window_type),
            "confirm_required": int(confirm_required),
        }
        if type is not None:
            params["type"] = int(type)
        if send_to_new_members is not None:
            params["send_to_new_members"] = send_to_new_members
        return await self._adapter.call_api(
            "_send_group_notice", _account_id=self._account_id, **params
        )

    async def delete_group_notice(
        self,
        *,
        group_id: Union[str, int],
        fid: Union[str, None] = None,
        notice_id: Union[str, None] = None,
    ) -> dict[str, Any]:
        """
        删除群公告（fid 或 notice_id 二选一）
        """
        params: dict[str, Any] = {"group_id": int(group_id)}
        if fid is not None:
            params["fid"] = str(fid)
        if notice_id is not None:
            params["notice_id"] = str(notice_id)
        return await self._adapter.call_api(
            "_del_group_notice", _account_id=self._account_id, **params
        )

    async def get_model_show(self, *, model: str = "") -> dict[str, Any]:
        """获取机型展示（SnowLuma 兼容 mock 实现）"""
        return await self._adapter.call_api(
            "_get_model_show", _account_id=self._account_id, model=model,
        )

    async def set_model_show(self, *, model: str = "") -> dict[str, Any]:
        """设置机型展示（SnowLuma 服务端为占位实现）"""
        return await self._adapter.call_api(
            "_set_model_show", _account_id=self._account_id, model=model,
        )

    async def get_friend_dress(self, *, user_id: Union[str, int]) -> dict[str, Any]:
        """获取指定 QQ 号正在使用的个性装扮（挂件/名片/来电/输入状态等）"""
        return await self._adapter.call_api(
            "_get_friend_dress", _account_id=self._account_id, user_id=int(user_id),
        )

    # ==================== 媒体 / OCR ====================

    async def ocr_image(self, *, image: str) -> dict[str, Any]:
        """OCR 图片识别（服务端，需图片 URL 或已缓存的图片 file_id）"""
        return await self._adapter.call_api(
            "ocr_image", _account_id=self._account_id, image=image,
        )

    async def get_image(self, *, file: str = "", file_id: str = "") -> dict[str, Any]:
        """
        获取图片信息（仅图片/语音缓存；群文件请用 get_group_file_url）

        :param file: 图片标识
        :param file_id: 缓存的图片 ID
        """
        return await self._adapter.call_api(
            "get_image", _account_id=self._account_id, file=file, file_id=file_id,
        )

    async def get_record(
        self, *, file: str = "", file_id: str = "", out_format: str = "mp3"
    ) -> dict[str, Any]:
        """
        获取语音信息并转码（传 out_format 则服务端转码并附带 base64）

        :param file: 语音标识
        :param file_id: 缓存的语音 ID
        :param out_format: mp3/amr/wma/m4a/spx/ogg 等
        """
        return await self._adapter.call_api(
            "get_record", _account_id=self._account_id,
            file=file, file_id=file_id, out_format=out_format,
        )

    async def fetch_ptt_text(self, *, message_id: Union[str, int]) -> dict[str, Any]:
        """
        语音转文字

        :param message_id: 语音消息 ID（服务端按消息定位语音）
        """
        return await self._adapter.call_api(
            "fetch_ptt_text", _account_id=self._account_id, message_id=int(message_id),
        )

    # ==================== 账号信息 / 凭证 / 能力 ====================

    async def get_cookies(self, *, domain: str = "qun.qq.com") -> dict[str, Any]:
        """获取 Cookies"""
        return await self._adapter.call_api(
            "get_cookies", _account_id=self._account_id, domain=domain,
        )

    async def get_csrf_token(self) -> dict[str, Any]:
        """获取 CSRF 令牌"""
        return await self._adapter.call_api(
            "get_csrf_token", _account_id=self._account_id
        )

    async def get_credentials(self, *, domain: str = "qun.qq.com") -> dict[str, Any]:
        """获取凭证"""
        return await self._adapter.call_api(
            "get_credentials", _account_id=self._account_id, domain=domain,
        )

    async def get_clientkey(self) -> dict[str, Any]:
        """获取 clientkey"""
        return await self._adapter.call_api(
            "get_clientkey", _account_id=self._account_id
        )

    async def can_send_image(self) -> dict[str, Any]:
        """查询是否可以发送图片"""
        return await self._adapter.call_api("can_send_image", _account_id=self._account_id)

    async def can_send_record(self) -> dict[str, Any]:
        """查询是否可以发送语音"""
        return await self._adapter.call_api("can_send_record", _account_id=self._account_id)

    async def get_version_info(self) -> dict[str, Any]:
        """获取 SnowLuma 实现与协议版本信息"""
        return await self._adapter.call_api("get_version_info", _account_id=self._account_id)

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
        """
        设置 QQ 资料（nickname / personal_note / sex；sex: 0 未知，1 男，2 女）
        """
        return await self._adapter.call_api(
            "set_qq_profile", _account_id=self._account_id, **profile,
        )

    async def get_profile_like(
        self, *, user_id: Union[str, int] = 0, start: int = 0, count: int = 10
    ) -> dict[str, Any]:
        """
        获取资料点赞

        :param user_id: 目标 QQ 号（0 表示自己）
        :param start: 起始偏移
        :param count: 本页数量
        """
        return await self._adapter.call_api(
            "get_profile_like", _account_id=self._account_id,
            user_id=int(user_id), start=int(start), count=int(count),
        )

    # ==================== 工具 / 杂项 ====================

    async def check_url_safely(self) -> dict[str, Any]:
        """检查链接安全性（SnowLuma 占位实现，恒返回 level=1）"""
        return await self._adapter.call_api("check_url_safely", _account_id=self._account_id)

    async def clean_cache(self) -> dict[str, Any]:
        """清理 SnowLuma 服务端缓存"""
        return await self._adapter.call_api("clean_cache", _account_id=self._account_id)

    async def get_file(self, *, file_id: str = "", file: str = "") -> dict[str, Any]:
        """
        获取文件信息（仅图片/语音缓存；群文件请用 get_group_file_url）
        """
        return await self._adapter.call_api(
            "get_file", _account_id=self._account_id, file_id=file_id, file=file,
        )

    async def get_rkey(self) -> dict[str, Any]:
        """获取下载 rkey"""
        return await self._adapter.call_api("get_rkey", _account_id=self._account_id)

    async def get_rkey_server(self) -> dict[str, Any]:
        """获取 rkey 服务器信息（过期时间与私聊/群聊 rkey）"""
        return await self._adapter.call_api("get_rkey_server", _account_id=self._account_id)

    async def translate_en2zh(self, *, words: list[str]) -> dict[str, Any]:
        """
        英译中

        :param words: 英文词句数组
        :returns: { words } 与输入等长的中文译文数组
        """
        return await self._adapter.call_api(
            "translate_en2zh", _account_id=self._account_id, words=words,
        )

    async def get_word_slices(self, *, content: str) -> dict[str, Any]:
        """分词（SnowLuma 服务端未实现）"""
        return await self._adapter.call_api(
            ".get_word_slices", _account_id=self._account_id, content=content,
        )

    async def set_restart(self) -> dict[str, Any]:
        """重启（SnowLuma 服务端不支持，调用将返回失败）"""
        return await self._adapter.call_api("set_restart", _account_id=self._account_id)

    async def click_inline_keyboard_button(
        self,
        *,
        group_id: Union[str, int],
        bot_appid: Union[str, int],
        msg_seq: Union[str, int],
        button_id: str,
        callback_data: str = "",
    ) -> dict[str, Any]:
        """
        点击内联键盘按钮（QQ 官方机器人在群内推送的键盘消息）

        :param bot_appid: 机器人 appid
        :param msg_seq: 键盘消息序号
        :param button_id: 按钮 ID
        :param callback_data: 按钮回调数据
        """
        return await self._adapter.call_api(
            "click_inline_keyboard_button", _account_id=self._account_id,
            group_id=int(group_id), bot_appid=int(bot_appid),
            msg_seq=int(msg_seq), button_id=str(button_id),
            callback_data=callback_data,
        )

    # ==================== 下载 / 文件 ====================

    async def download_file(
        self,
        *,
        url: str = "",
        base64: str = "",
        name: str = "",
        headers: Any = None,
    ) -> dict[str, Any]:
        """
        下载文件（url 或 base64）到服务端 data/downloads

        :param base64: 与 url 二选一
        :param headers: 下载请求头（可选）
        :returns: { file } 服务端文件路径
        """
        params: dict[str, Any] = {"url": url, "base64": base64, "name": name}
        if headers is not None:
            params["headers"] = headers
        return await self._adapter.call_api(
            "download_file", _account_id=self._account_id, **params
        )
