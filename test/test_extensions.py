"""
SnowLuma 扩展动作测试：参数转发、签名修正与条件组装

- OB11ExtensionApi（ob11_extensions.py）：通用扩展动作
- SnowLumaExtensionApi（snowluma_extensions.py）：SnowLuma 特有动作
"""

import asyncio

from SnowLumaAdapter.ob11_extensions import OB11ExtensionApi
from SnowLumaAdapter.snowluma_extensions import SnowLumaExtensionApi


class RecordingAdapter:
    def __init__(self):
        self.calls = []

    async def call_api(self, endpoint, _account_id=None, **params):
        self.calls.append((endpoint, params))
        return {"status": "ok", "retcode": 0, "data": {}}


def make_ext(cls=OB11ExtensionApi):
    ext = cls()
    ext._adapter = RecordingAdapter()
    ext._account_id = "default"
    return ext


def last(ext):
    return ext._adapter.calls[-1]


def asyncio_run(coro):
    return asyncio.run(coro)


class TestGetQzoneFeeds:
    def test_default_page_num_is_one(self):
        ext = make_ext()
        asyncio_run(ext.get_qzone_feeds())
        endpoint, params = last(ext)
        assert endpoint == "get_qzone_feeds"
        assert params["page_num"] == 1

    def test_non_positive_clamped_to_one(self):
        ext = make_ext()
        asyncio_run(ext.get_qzone_feeds(page_num=0))
        assert last(ext)[1]["page_num"] == 1

    def test_valid_page_num_preserved(self):
        ext = make_ext()
        asyncio_run(ext.get_qzone_feeds(page_num=3, count=5))
        endpoint, params = last(ext)
        assert params["page_num"] == 3
        assert params["count"] == 5


class TestSendQzoneMsg:
    def test_text_only(self):
        ext = make_ext()
        asyncio_run(ext.send_qzone_msg(content="hello"))
        endpoint, params = last(ext)
        assert endpoint == "send_qzone_msg"
        assert params == {"content": "hello", "ugc_right": 1}

    def test_with_images_and_right(self):
        ext = make_ext()
        asyncio_run(ext.send_qzone_msg(
            content="pic", images=["http://a.jpg"], ugc_right=4, target_uins=[123, "456"],
        ))
        params = last(ext)[1]
        assert params["images"] == ["http://a.jpg"]
        assert params["ugc_right"] == 4
        assert params["target_uins"] == [123, 456]

    def test_get_qzone_msg_list_target(self):
        ext = make_ext()
        asyncio_run(ext.get_qzone_msg_list(target_uin=10001, pos=20, num=10))
        params = last(ext)[1]
        assert params == {"pos": 20, "num": 10, "target_uin": 10001}

    def test_get_qzone_msg_detail(self):
        ext = make_ext(SnowLumaExtensionApi)
        asyncio_run(ext.get_qzone_msg_detail(tid="tid-1"))
        endpoint, params = last(ext)
        assert endpoint == "get_qzone_msg_detail"
        assert params == {"tid": "tid-1", "pos": 0, "num": 20}


class TestFixedSignatures:
    """对照官方 catalog 修正过参数名的封装"""

    def test_set_group_todo_uses_message_id(self):
        ext = make_ext()
        asyncio_run(ext.set_group_todo(group_id=1, message_id=42))
        endpoint, params = last(ext)
        assert endpoint == "set_group_todo"
        assert params == {"group_id": 1, "message_id": 42}

    def test_mark_msg_as_read(self):
        ext = make_ext()
        asyncio_run(ext.mark_msg_as_read(message_id=7))
        assert last(ext)[1] == {"message_id": 7}

    def test_mark_msg_as_read_with_target(self):
        ext = make_ext()
        asyncio_run(ext.mark_msg_as_read(message_id=7, target_id=10001))
        assert last(ext)[1] == {"message_id": 7, "target_id": 10001}

    def test_fetch_ptt_text_uses_message_id(self):
        ext = make_ext()
        asyncio_run(ext.fetch_ptt_text(message_id=9))
        endpoint, params = last(ext)
        assert endpoint == "fetch_ptt_text"
        assert params == {"message_id": 9}

    def test_get_emoji_likes_requires_emoji_id(self):
        ext = make_ext()
        asyncio_run(ext.get_emoji_likes(message_id=5, emoji_id=128))
        params = last(ext)[1]
        assert params == {"message_id": 5, "emoji_id": "128"}

    def test_group_reaction_is_set(self):
        ext = make_ext()
        asyncio_run(ext.set_group_reaction(message_id=3, code=128, is_set=False))
        endpoint, params = last(ext)
        assert endpoint == "set_group_reaction"
        assert params == {"message_id": 3, "code": "128", "is_set": False}

    def test_group_reaction_group_id_optional(self):
        ext = make_ext()
        asyncio_run(ext.set_group_reaction(group_id=1, message_id=3, code="4"))
        params = last(ext)[1]
        assert params["group_id"] == 1

    def test_fetch_emoji_like_wire_param_emojiId(self):
        ext = make_ext()
        asyncio_run(ext.fetch_emoji_like(message_id=5, emoji_id="128", count=20))
        endpoint, params = last(ext)
        assert endpoint == "fetch_emoji_like"
        assert params["emojiId"] == "128"
        assert params["count"] == 20

    def test_get_forward_msg_message_id_string(self):
        ext = make_ext()
        asyncio_run(ext.get_forward_msg(message_id="abc"))
        assert last(ext)[1] == {"message_id": "abc"}


class TestGroupManagement:
    def test_kick_members_batch(self):
        ext = make_ext()
        asyncio_run(ext.set_group_kick_members(group_id=1, user_id=["2", 3]))
        endpoint, params = last(ext)
        assert endpoint == "set_group_kick_members"
        assert params["user_id"] == [2, 3]

    def test_invite_policy_enum(self):
        ext = make_ext()
        asyncio_run(ext.set_group_member_invite_policy(group_id=1, policy="require_approval"))
        endpoint, params = last(ext)
        assert endpoint == "set_group_member_invite_policy"
        assert params["policy"] == "require_approval"

    def test_member_permissions_skips_none(self):
        ext = make_ext()
        asyncio_run(ext.set_group_member_permissions(
            group_id=1, allow_member_upload_album=True,
        ))
        params = last(ext)[1]
        assert params == {"group_id": 1, "allow_member_upload_album": True}

    def test_group_tags(self):
        ext = make_ext()
        asyncio_run(ext.get_group_tags(group_class=2))
        endpoint, params = last(ext)
        assert endpoint == "get_group_tags"
        assert params == {"group_class": 2}

    def test_send_group_notice_defaults(self):
        ext = make_ext()
        asyncio_run(ext.send_group_notice(group_id=1, content="公告"))
        endpoint, params = last(ext)
        assert endpoint == "_send_group_notice"
        assert params["pinned"] == 0
        assert params["tip_window_type"] == 1
        assert "type" not in params
        assert "send_to_new_members" not in params


class TestFriends:
    def test_set_friends_category_wire_names(self):
        ext = make_ext()
        asyncio_run(ext.set_friends_category(uin=123, category_name="同学"))
        endpoint, params = last(ext)
        assert endpoint == "set_friends_category"
        assert params == {"uin": 123, "categoryName": "同学"}

    def test_delete_friend_block_default(self):
        ext = make_ext()
        asyncio_run(ext.delete_friend(user_id=123))
        endpoint, params = last(ext)
        assert endpoint == "delete_friend"
        assert params == {"user_id": 123, "block": False}


class TestSnowLumaExtension:
    def make(self):
        return make_ext(SnowLumaExtensionApi)

    def test_upload_image_to_qun_album(self):
        ext = self.make()
        asyncio_run(ext.upload_image_to_qun_album(
            group_id=1, album_id="a1", album_name="相册", file="base64://xxx",
        ))
        endpoint, params = last(ext)
        assert endpoint == "upload_image_to_qun_album"
        assert params == {
            "group_id": 1, "album_id": "a1", "album_name": "相册", "file": "base64://xxx",
        }

    def test_fetch_sys_faces_refresh(self):
        ext = self.make()
        asyncio_run(ext.fetch_sys_faces(refresh=True))
        endpoint, params = last(ext)
        assert endpoint == "fetch_sys_faces"
        assert params == {"refresh": True}

    def test_search_sys_faces(self):
        ext = self.make()
        asyncio_run(ext.search_sys_faces(query="微笑"))
        endpoint, params = last(ext)
        assert endpoint == "search_sys_faces"
        assert params == {"query": "微笑"}

    def test_download_file_stream_conditional(self):
        ext = self.make()
        asyncio_run(ext.download_file_stream(file_id="img-1"))
        endpoint, params = last(ext)
        assert endpoint == "download_file_stream"
        assert params == {"file_id": "img-1"}

    def test_upload_file_stream_new_flow(self):
        ext = self.make()
        asyncio_run(ext.upload_file_stream(
            stream_id="abc-1", total_chunks=2, file_size=10, filename="a.txt",
        ))
        endpoint, params = last(ext)
        assert endpoint == "upload_file_stream"
        assert params["stream_id"] == "abc-1"
        assert params["total_chunks"] == 2
        assert params["file_retention"] == 300000
        assert "chunk_data" not in params

    def test_send_flash_msg_group(self):
        ext = self.make()
        asyncio_run(ext.send_flash_msg(fileset_id="fs-1", group_id=1))
        endpoint, params = last(ext)
        assert endpoint == "send_flash_msg"
        assert params == {"fileset_id": "fs-1", "group_id": 1}

    def test_get_fileset_id(self):
        ext = self.make()
        asyncio_run(ext.get_fileset_id(share_code="abcd1234"))
        endpoint, params = last(ext)
        assert endpoint == "get_fileset_id"
        assert params == {"share_code": "abcd1234"}

    def test_set_qzone_ban_default(self):
        ext = self.make()
        asyncio_run(ext.set_qzone_ban(user_id=10001))
        endpoint, params = last(ext)
        assert endpoint == "set_qzone_ban"
        assert params == {"user_id": 10001, "enable": True}

    def test_set_qzone_msg_right_target_uins(self):
        ext = self.make()
        asyncio_run(ext.set_qzone_msg_right(tid="t1", ugc_right=128, target_uins=["1", 2]))
        params = last(ext)[1]
        assert params == {"tid": "t1", "ugc_right": 128, "target_uins": [1, 2]}


class TestAIRecord:
    def test_send_group_ai_record(self):
        ext = make_ext()
        asyncio_run(ext.send_group_ai_record(group_id=1, character="1002", text="你好"))
        endpoint, params = last(ext)
        assert endpoint == "send_group_ai_record"
        assert params == {
            "group_id": 1, "character": "1002", "text": "你好", "chat_type": 1,
        }

    def test_get_ai_characters(self):
        ext = make_ext()
        asyncio_run(ext.get_ai_characters(group_id=1))
        endpoint, params = last(ext)
        assert endpoint == "get_ai_characters"
        assert params == {"group_id": 1, "chat_type": 1}


class TestTuwenArk:
    def test_defaults(self):
        ext = make_ext()
        asyncio_run(ext.send_tuwen_ark(
            group_id=1, title="标题", desc="描述", jump_url="https://e.x",
        ))
        endpoint, params = last(ext)
        assert endpoint == "send_tuwen_ark"
        assert params["summary"] == "[分享]"
        assert params["preview_url"].startswith("https://tangram")

    def test_mini_app_ark_dual_keys(self):
        ext = make_ext()
        asyncio_run(ext.get_mini_app_ark(title="t", pic_url="http://p", jump_url="http://j"))
        endpoint, params = last(ext)
        assert endpoint == "get_mini_app_ark"
        assert params["pic_url"] == params["picUrl"] == "http://p"
        assert params["jump_url"] == params["jumpUrl"] == "http://j"
