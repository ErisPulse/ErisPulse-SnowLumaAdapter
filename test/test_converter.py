"""
SnowLuma 转换器测试：mention alt 渲染兜底、CQ 反转义、bot_status 元事件转换
"""

from SnowLumaAdapter.Converter import SnowLumaConverter


def make_converter() -> SnowLumaConverter:
    return SnowLumaConverter(platform="snowluma")


def group_message_event(message) -> dict:
    return {
        "post_type": "message",
        "message_type": "group",
        "message_id": -12345,
        "group_id": 42,
        "self_id": 10000,
        "sender": {"user_id": 1, "nickname": "测试者"},
        "message": message,
    }


class TestMentionAltRender:
    def test_nickname_present(self):
        c = make_converter().convert(group_message_event([
            {"type": "at", "data": {"qq": "123", "name": "小张"}},
            {"type": "text", "data": {"text": " 你好"}},
        ]))
        assert c["alt_message"] == "@小张 你好"

    def test_nickname_missing_fallback_user_id(self):
        # mention 段构造时 user_name 默认存 ""，必须回退 user_id 而不是拼出空 "@"
        c = make_converter().convert(group_message_event([
            {"type": "at", "data": {"qq": "123", "name": ""}},
            {"type": "text", "data": {"text": " 帮助"}},
        ]))
        assert c["alt_message"] == "@123 帮助"

    def test_at_all(self):
        c = make_converter().convert(group_message_event([
            {"type": "at", "data": {"qq": "all"}},
            {"type": "text", "data": {"text": " 开会"}},
        ]))
        assert c["alt_message"] == "@全体成员 开会"

    def test_both_missing_omits_at(self):
        c = make_converter().convert(group_message_event([
            {"type": "at", "data": {}},
            {"type": "text", "data": {"text": "正文"}},
        ]))
        assert c["alt_message"] == "正文"

    def test_cq_string_at_all(self):
        c = make_converter().convert(group_message_event("[CQ:at,qq=all] 开会"))
        assert c["alt_message"] == "@全体成员 开会"


class TestCqUnescape:
    def test_url_with_escaped_comma(self):
        c = make_converter().convert(group_message_event(
            "[CQ:image,file=abc.jpg,url=https://a.com/x?foo=1&#44;bar=2]"
        ))
        seg = c["message"][0]
        assert seg["type"] == "image"
        assert seg["data"]["url"] == "https://a.com/x?foo=1,bar=2"

    def test_amp_and_brackets_in_text(self):
        c = make_converter().convert(group_message_event("A &amp; B &#91;tag&#93;"))
        assert c["message"][0]["data"]["text"] == "A & B [tag]"

    def test_plain_text_unescaped(self):
        c = make_converter().convert(group_message_event("a&#44;b"))
        assert c["message"][0]["data"]["text"] == "a,b"

    def test_array_form_not_escaped(self):
        # 数组格式的值是原始数据，不做反转义
        c = make_converter().convert(group_message_event([
            {"type": "text", "data": {"text": "a&#44;b"}}
        ]))
        assert c["message"][0]["data"]["text"] == "a&#44;b"


class TestBotStatus:
    def bot_status_event(self, sub_type) -> dict:
        return {
            "post_type": "notice",
            "notice_type": "bot_status",
            "sub_type": sub_type,
            "user_id": 10000,
            "self_id": 10000,
            "time": 1710000000,
        }

    def test_online_to_connect(self):
        c = make_converter().convert(self.bot_status_event("online"))
        assert c["type"] == "meta_event"
        assert c["detail_type"] == "connect"
        assert c["sub_type"] == "online"
        assert c["user_id"] == "10000"
        assert c["snowluma_meta"]["notice_type"] == "bot_status"

    def test_offline_to_disconnect(self):
        c = make_converter().convert(self.bot_status_event("offline"))
        assert c["detail_type"] == "disconnect"

    def test_bot_offline_to_disconnect(self):
        # 官方口径：被踢下线 sub_type 为 bot_offline
        c = make_converter().convert(self.bot_status_event("bot_offline"))
        assert c["detail_type"] == "disconnect"


class TestMessageId:
    def test_negative_message_id_preserved(self):
        # message_id 为非零有符号 32 位整数，负值有效，不得取绝对值
        c = make_converter().convert(group_message_event("hello"))
        assert c["message_id"] == "-12345"
