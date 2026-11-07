"""
SnowLuma 特有扩展动作（QQ 空间扩展 / 群相册 / 系统表情 / 流式接口 / 闪传 / 收藏表情 / 底层通道）

这些动作非 NapCat/Lagrange 通用，仅 SnowLuma 服务端提供，
与通用 OB11 扩展（ob11_extensions.py）分离，避免跨适配器混入时引入平台耦合。

用法（与 OB11ExtensionApi 一同混入适配器 Api 内部类）：

    class Api(BaseAdapter.Api, OB11ExtensionApi, SnowLumaExtensionApi):
        ...

所有方法直接委托给 call_api(action_name, ...)，
签名与参数名以官方动作目录（catalog.json，200 个动作）为准。

{!--< tips >!--}
1. 流式接口（upload/download_file_stream）为服务端流式帧协议，
   HTTP 模式下响应为分帧数据；WS 模式按 echo 关联返回
2. 服务器标记"未实现"的动作也一并封装并在 docstring 注明
{!--< /tips >!--}
"""

from typing import Any, Union


class SnowLumaExtensionApi:
    """
    SnowLuma 特有扩展动作 Mixin

    通过多继承混入适配器的 Api 内部类，获得 IDE 补全支持。
    使用 ``self._adapter.call_api(action, _account_id=self._account_id, ...)`` 委托。
    """

    # ==================== QQ 空间扩展 ====================

    async def get_qzone_msg_detail(
        self,
        *,
        tid: str,
        target_uin: Union[str, int, None] = None,
        pos: int = 0,
        num: int = 20,
    ) -> dict[str, Any]:
        """
        获取 QQ 空间说说详情与一页评论（含服务端内联回复，需有访问权限）

        :param tid: 说说 tid（来自 get_qzone_msg_list / send_qzone_msg）
        :param target_uin: 说说所属 QQ 号（省略则取机器人自己）
        :param pos: 一级评论起始偏移
        :param num: 请求的一级评论数量（实际数量受服务端限制）
        """
        params: dict[str, Any] = {"tid": str(tid), "pos": int(pos), "num": int(num)}
        if target_uin is not None:
            params["target_uin"] = int(target_uin)
        return await self._adapter.call_api(
            "get_qzone_msg_detail", _account_id=self._account_id, **params
        )

    async def set_qzone_ban(
        self, *, user_id: Union[str, int], enable: bool = True
    ) -> dict[str, Any]:
        """
        拉黑或解除拉黑某人（修改机器人自身 QQ 空间黑名单）

        :param enable: True 拉黑，False 解除拉黑
        """
        return await self._adapter.call_api(
            "set_qzone_ban", _account_id=self._account_id,
            user_id=int(user_id), enable=enable,
        )

    async def set_qzone_msg_right(
        self,
        *,
        tid: str,
        ugc_right: int,
        target_uins: Union[list[Union[str, int]], None] = None,
    ) -> dict[str, Any]:
        """
        修改一条已发说说的查看权限（QQ 空间，按 tid）

        :param ugc_right: 查看权限：1=所有人可见，4=好友可见，16=部分好友可见，
            64=仅自己可见，128=部分好友不可见
        :param target_uins: 权限作用 QQ 号数组（16 为可见名单，128 为不可见名单）
        """
        params: dict[str, Any] = {"tid": str(tid), "ugc_right": int(ugc_right)}
        if target_uins is not None:
            params["target_uins"] = [int(u) for u in target_uins]
        return await self._adapter.call_api(
            "set_qzone_msg_right", _account_id=self._account_id, **params
        )

    # ==================== 群相册 ====================

    async def get_qun_album_list(
        self, *, group_id: Union[str, int], attach_info: str = ""
    ) -> dict[str, Any]:
        """
        获取群相册列表（NapCat 风格封套：{album_list, attach_info, has_more}）

        :param attach_info: 下一页分页游标（上一页响应返回）
        """
        return await self._adapter.call_api(
            "get_qun_album_list", _account_id=self._account_id,
            group_id=int(group_id), attach_info=attach_info,
        )

    async def upload_image_to_qun_album(
        self,
        *,
        group_id: Union[str, int],
        album_id: str,
        album_name: str,
        file: str,
    ) -> dict[str, Any]:
        """
        上传图片到群相册

        :param album_id: 相册 ID
        :param album_name: 相册名称
        :param file: 图片（本地路径 / URL / base64://）
        """
        return await self._adapter.call_api(
            "upload_image_to_qun_album", _account_id=self._account_id,
            group_id=int(group_id), album_id=str(album_id),
            album_name=album_name, file=file,
        )

    async def upload_video_to_qun_album(
        self,
        *,
        group_id: Union[str, int],
        album_id: str,
        album_name: str,
        file: str,
    ) -> dict[str, Any]:
        """
        上传视频到群相册

        :param album_id: 相册 ID
        :param album_name: 相册名称
        :param file: 视频文件（本地路径 / URL / base64://）
        """
        return await self._adapter.call_api(
            "upload_video_to_qun_album", _account_id=self._account_id,
            group_id=int(group_id), album_id=str(album_id),
            album_name=album_name, file=file,
        )

    async def do_group_album_comment(
        self,
        *,
        group_id: Union[str, int],
        album_id: str,
        lloc: str,
        content: str,
    ) -> dict[str, Any]:
        """
        评论群相册媒体

        :param lloc: 图片长定位标识，或视频 id
        """
        return await self._adapter.call_api(
            "do_group_album_comment", _account_id=self._account_id,
            group_id=int(group_id), album_id=str(album_id),
            lloc=str(lloc), content=content,
        )

    async def del_group_album_media(
        self, *, group_id: Union[str, int], album_id: str, lloc: str
    ) -> dict[str, Any]:
        """
        删除群相册图片或视频

        :param lloc: 图片长定位标识，或视频 id
        """
        return await self._adapter.call_api(
            "del_group_album_media", _account_id=self._account_id,
            group_id=int(group_id), album_id=str(album_id), lloc=str(lloc),
        )

    async def set_group_album_media_like(
        self,
        *,
        group_id: Union[str, int],
        album_id: str,
        batch_id: str,
        lloc: Union[str, None] = None,
    ) -> dict[str, Any]:
        """
        给群相册媒体点赞

        :param batch_id: 相册批次 ID
        :param lloc: 图片长定位标识（可选）
        """
        params: dict[str, Any] = {
            "group_id": int(group_id),
            "album_id": str(album_id),
            "batch_id": str(batch_id),
        }
        if lloc is not None:
            params["lloc"] = str(lloc)
        return await self._adapter.call_api(
            "set_group_album_media_like", _account_id=self._account_id, **params
        )

    async def cancel_group_album_media_like(
        self,
        *,
        group_id: Union[str, int],
        album_id: str,
        batch_id: str,
        lloc: Union[str, None] = None,
    ) -> dict[str, Any]:
        """
        取消群相册媒体点赞

        :param batch_id: 相册批次 ID
        :param lloc: 图片长定位标识（可选）
        """
        params: dict[str, Any] = {
            "group_id": int(group_id),
            "album_id": str(album_id),
            "batch_id": str(batch_id),
        }
        if lloc is not None:
            params["lloc"] = str(lloc)
        return await self._adapter.call_api(
            "cancel_group_album_media_like", _account_id=self._account_id, **params
        )

    # ==================== 系统表情 ====================

    async def fetch_sys_faces(self, *, refresh: bool = False) -> dict[str, Any]:
        """
        获取 QQ 系统表情目录（按分组返回完整映射）

        :param refresh: 是否强制从 QQ 刷新目录
        """
        return await self._adapter.call_api(
            "fetch_sys_faces", _account_id=self._account_id, refresh=refresh,
        )

    async def search_sys_faces(self, *, query: str) -> dict[str, Any]:
        """
        搜索 QQ 系统表情（匹配编号、名称、别名或分组名）

        :param query: 搜索关键字
        """
        return await self._adapter.call_api(
            "search_sys_faces", _account_id=self._account_id, query=query,
        )

    async def fetch_face_entity(
        self, *, face_id: int, refresh: bool = False
    ) -> dict[str, Any]:
        """
        按编号查询 QQ 系统表情（编号不存在时返回 null）

        :param face_id: QQ 系统表情编号
        :param refresh: 是否强制从 QQ 刷新目录
        """
        return await self._adapter.call_api(
            "fetch_face_entity", _account_id=self._account_id,
            face_id=int(face_id), refresh=refresh,
        )

    async def fetch_super_face_id(
        self, *, face_id: int, refresh: bool = False
    ) -> dict[str, Any]:
        """
        判断 QQ 系统表情是否使用超级表情格式

        :param face_id: QQ 系统表情编号
        :param refresh: 是否强制从 QQ 刷新目录
        """
        return await self._adapter.call_api(
            "fetch_super_face_id", _account_id=self._account_id,
            face_id=int(face_id), refresh=refresh,
        )

    # ==================== 流式接口 ====================

    async def upload_file_stream(
        self,
        *,
        stream_id: str,
        chunk_data: Union[str, None] = None,
        chunk_index: Union[int, None] = None,
        total_chunks: Union[int, None] = None,
        file_size: Union[int, None] = None,
        expected_sha256: Union[str, None] = None,
        is_complete: Union[bool, None] = None,
        filename: Union[str, None] = None,
        reset: Union[bool, None] = None,
        verify_only: Union[bool, None] = None,
        file_retention: int = 300000,
    ) -> dict[str, Any]:
        """
        以流式分块方式上传文件到机器人本地（返回可用于发送的本地路径）

        分块协议：新流必传 total_chunks/file_size/filename，随后逐块传
        chunk_index + chunk_data(Base64)，最后一块传 is_complete=True 触发合并。

        :param stream_id: 流 ID（客户端生成的 UUID，限 [A-Za-z0-9_-]）
        :param reset: 重置并丢弃该流
        :param verify_only: 仅查询当前流状态
        :param file_retention: 合并文件保留毫秒（0=不回收）
        """
        params: dict[str, Any] = {
            "stream_id": str(stream_id),
            "file_retention": int(file_retention),
        }
        for key, value in (
            ("chunk_data", chunk_data), ("chunk_index", chunk_index),
            ("total_chunks", total_chunks), ("file_size", file_size),
            ("expected_sha256", expected_sha256), ("is_complete", is_complete),
            ("filename", filename), ("reset", reset), ("verify_only", verify_only),
        ):
            if value is not None:
                params[key] = value
        return await self._adapter.call_api(
            "upload_file_stream", _account_id=self._account_id, **params
        )

    async def download_file_stream(
        self,
        *,
        file: Union[str, None] = None,
        file_id: Union[str, None] = None,
        chunk_size: Union[int, None] = None,
    ) -> dict[str, Any]:
        """
        以流式方式下载文件（流式帧：file_info → file_chunk* → file_complete）

        :param file: 文件路径（限 stream 临时目录）/ http(s) URL
        :param file_id: 缓存的图片/语音 ID
        :param chunk_size: 分块大小（字节，默认 64KB）
        """
        return await self._call_download_stream(
            "download_file_stream", file=file, file_id=file_id, chunk_size=chunk_size,
        )

    async def download_file_image_stream(
        self,
        *,
        file: Union[str, None] = None,
        file_id: Union[str, None] = None,
        chunk_size: Union[int, None] = None,
    ) -> dict[str, Any]:
        """
        以流式方式下载图片（流式帧：file_info → file_chunk* → file_complete）

        :param file: 文件路径（限 stream 临时目录）/ http(s) URL
        :param file_id: 缓存的图片 ID
        :param chunk_size: 分块大小（字节，默认 64KB）
        """
        return await self._call_download_stream(
            "download_file_image_stream", file=file, file_id=file_id, chunk_size=chunk_size,
        )

    async def download_file_record_stream(
        self,
        *,
        file: Union[str, None] = None,
        file_id: Union[str, None] = None,
        chunk_size: Union[int, None] = None,
    ) -> dict[str, Any]:
        """
        以流式方式下载语音（流式帧：file_info → file_chunk* → file_complete）

        :param file: 文件路径（限 stream 临时目录）/ http(s) URL
        :param file_id: 缓存的语音 ID
        :param chunk_size: 分块大小（字节，默认 64KB）
        """
        return await self._call_download_stream(
            "download_file_record_stream", file=file, file_id=file_id, chunk_size=chunk_size,
        )

    async def clean_stream_temp_file(self) -> dict[str, Any]:
        """清理流式传输临时文件（仅清理 stream 上传/下载目录）"""
        return await self._adapter.call_api(
            "clean_stream_temp_file", _account_id=self._account_id
        )

    async def test_download_stream(self, *, error: bool = False) -> dict[str, Any]:
        """
        测试下载流（推送 10 个数据帧验证流式传输，不触达 QQ）

        :param error: 是否触发测试错误
        """
        return await self._adapter.call_api(
            "test_download_stream", _account_id=self._account_id, error=error,
        )

    async def _call_download_stream(
        self, action: str, *, file, file_id, chunk_size
    ) -> dict[str, Any]:
        params: dict[str, Any] = {}
        if file is not None:
            params["file"] = str(file)
        if file_id is not None:
            params["file_id"] = str(file_id)
        if chunk_size is not None:
            params["chunk_size"] = int(chunk_size)
        return await self._adapter.call_api(action, _account_id=self._account_id, **params)

    # ==================== 闪传 / 文件集 ====================

    async def create_flash_task(
        self,
        *,
        files: Any = None,
        name: Union[str, None] = None,
        thumb_path: Union[str, None] = None,
    ) -> dict[str, Any]:
        """
        创建闪传任务

        :param files: 路径、{ file, name }，或它们的数组
        """
        params: dict[str, Any] = {}
        if files is not None:
            params["files"] = files
        if name is not None:
            params["name"] = str(name)
        if thumb_path is not None:
            params["thumb_path"] = str(thumb_path)
        return await self._adapter.call_api(
            "create_flash_task", _account_id=self._account_id, **params
        )

    async def send_flash_msg(
        self,
        *,
        fileset_id: str,
        user_id: Union[str, int, None] = None,
        group_id: Union[str, int, None] = None,
    ) -> dict[str, Any]:
        """
        发送闪传消息（私聊或群聊，引用 fileset_id 让对端下载）

        :returns: { message_id }
        """
        params: dict[str, Any] = {"fileset_id": str(fileset_id)}
        if user_id is not None:
            params["user_id"] = int(user_id)
        if group_id is not None:
            params["group_id"] = int(group_id)
        return await self._adapter.call_api(
            "send_flash_msg", _account_id=self._account_id, **params
        )

    async def get_flash_file_list(self, *, fileset_id: str) -> dict[str, Any]:
        """获取闪传文件列表"""
        return await self._adapter.call_api(
            "get_flash_file_list", _account_id=self._account_id,
            fileset_id=str(fileset_id),
        )

    async def get_flash_file_url(
        self,
        *,
        fileset_id: str,
        file_name: Union[str, None] = None,
        file_index: Union[int, float, None] = None,
    ) -> dict[str, Any]:
        """
        获取闪传文件链接

        :param file_name: 按文件名定位（与 file_index 二选一）
        :param file_index: 按序号定位
        """
        params: dict[str, Any] = {"fileset_id": str(fileset_id)}
        if file_name is not None:
            params["file_name"] = str(file_name)
        if file_index is not None:
            params["file_index"] = file_index
        return await self._adapter.call_api(
            "get_flash_file_url", _account_id=self._account_id, **params
        )

    async def delete_flash_file(self, *, fileset_id: str) -> dict[str, Any]:
        """删除闪传文件集"""
        return await self._adapter.call_api(
            "delete_flash_file", _account_id=self._account_id,
            fileset_id=str(fileset_id),
        )

    async def rename_flash_file(
        self, *, fileset_id: str, new_name: str
    ) -> dict[str, Any]:
        """重命名闪传文件集"""
        return await self._adapter.call_api(
            "rename_flash_file", _account_id=self._account_id,
            fileset_id=str(fileset_id), new_name=new_name,
        )

    async def get_fileset_id(self, *, share_code: str) -> dict[str, Any]:
        """
        从 QQ 闪传分享码或官方分享链接获取 fileset_id

        :param share_code: 分享码，或 https://qfile.qq.com/q/... 官方分享链接
        """
        return await self._adapter.call_api(
            "get_fileset_id", _account_id=self._account_id, share_code=str(share_code),
        )

    async def get_fileset_info(self, *, fileset_id: str) -> dict[str, Any]:
        """获取文件集信息"""
        return await self._adapter.call_api(
            "get_fileset_info", _account_id=self._account_id,
            fileset_id=str(fileset_id),
        )

    async def list_filesets(self) -> dict[str, Any]:
        """列出当前账号的所有闪传文件集"""
        return await self._adapter.call_api("list_filesets", _account_id=self._account_id)

    async def download_fileset(
        self,
        *,
        fileset_id: str,
        file_name: Union[str, None] = None,
        file_index: Union[int, float, None] = None,
    ) -> dict[str, Any]:
        """
        解析闪传文件下载直链（不下载，由调用方实现下载）

        :returns: { url, file_name, file_size }
        """
        params: dict[str, Any] = {"fileset_id": str(fileset_id)}
        if file_name is not None:
            params["file_name"] = str(file_name)
        if file_index is not None:
            params["file_index"] = file_index
        return await self._adapter.call_api(
            "download_fileset", _account_id=self._account_id, **params
        )

    # ==================== 收藏表情 ====================

    async def add_custom_face(self, *, file: str) -> dict[str, Any]:
        """
        添加收藏表情

        :param file: 图片（本地路径 / URL / base64://）
        """
        return await self._adapter.call_api(
            "add_custom_face", _account_id=self._account_id, file=file,
        )

    async def fetch_custom_face(
        self, *, count: int = 10, return_type: str = "url"
    ) -> dict[str, Any]:
        """
        获取自定义表情

        :param count: 数量
        :param return_type: "url"（图片 URL）或 "id"（emoji_id）
        """
        return await self._adapter.call_api(
            "fetch_custom_face", _account_id=self._account_id,
            count=count, return_type=return_type,
        )

    async def fetch_custom_face_detail(self, *, count: int = 48) -> dict[str, Any]:
        """
        获取自定义表情详情（资源标识、图片地址、摘要与描述）

        :param count: 数量
        """
        return await self._adapter.call_api(
            "fetch_custom_face_detail", _account_id=self._account_id, count=count,
        )

    async def modify_custom_face(
        self, *, emoji_id: str, desc: str = ""
    ) -> dict[str, Any]:
        """
        修改收藏表情备注

        :param emoji_id: 收藏表情 ID
        """
        return await self._adapter.call_api(
            "modify_custom_face", _account_id=self._account_id,
            emoji_id=str(emoji_id), desc=desc,
        )

    async def move_custom_face_to_front(self, *, emoji_id: str) -> dict[str, Any]:
        """
        收藏表情移到最前

        :param emoji_id: 收藏表情 ID
        """
        return await self._adapter.call_api(
            "move_custom_face_to_front", _account_id=self._account_id,
            emoji_id=str(emoji_id),
        )

    async def delete_custom_face(self, *, emoji_id: str) -> dict[str, Any]:
        """
        删除收藏表情

        :param emoji_id: 收藏表情 ID
        """
        return await self._adapter.call_api(
            "delete_custom_face", _account_id=self._account_id,
            emoji_id=str(emoji_id),
        )

    async def get_collection_list(
        self, *, category: int = 0, count: int = 50
    ) -> dict[str, Any]:
        """
        获取收藏列表

        :param category: 收藏分类 ID（0 表示全部分类）
        :param count: 最多返回的收藏数量
        """
        return await self._adapter.call_api(
            "get_collection_list", _account_id=self._account_id,
            category=int(category), count=count,
        )

    async def create_collection(self) -> dict[str, Any]:
        """创建收藏（SnowLuma 服务端未实现）"""
        return await self._adapter.call_api("create_collection", _account_id=self._account_id)

    # ==================== 底层通道 ====================

    async def send_packet(
        self, *, cmd: str, data: str = "", rsp: bool = True
    ) -> dict[str, Any]:
        """
        发送原始 SSO 包（高级用法，需了解 QQ 内部协议）

        :param cmd: SSO 命令名
        :param data: 十六进制编码的包体
        :param rsp: 是否等待并返回响应包
        """
        return await self._adapter.call_api(
            "send_packet", _account_id=self._account_id,
            cmd=cmd, data=data, rsp=rsp,
        )

    async def request_decrypt_key(self, *, db_path: str) -> dict[str, Any]:
        """
        请求数据库解密密钥

        :param db_path: 数据库文件路径
        """
        return await self._adapter.call_api(
            "request_decrypt_key", _account_id=self._account_id, db_path=str(db_path),
        )

    async def nc_get_packet_status(self) -> dict[str, Any]:
        """获取 packet 状态（SnowLuma 占位实现，恒返回 null）"""
        return await self._adapter.call_api(
            "nc_get_packet_status", _account_id=self._account_id
        )

    async def bot_exit(self) -> dict[str, Any]:
        """退出机器人（SnowLuma 服务端进程退出）"""
        return await self._adapter.call_api("bot_exit", _account_id=self._account_id)
