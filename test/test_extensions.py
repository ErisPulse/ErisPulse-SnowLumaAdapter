"""
SnowLuma OB11 扩展动作测试：get_qzone_feeds 页码钳制
"""

from SnowLumaAdapter.ob11_extensions import OB11ExtensionApi


class RecordingAdapter:
    def __init__(self):
        self.calls = []

    async def call_api(self, endpoint, _account_id=None, **params):
        self.calls.append((endpoint, params))
        return {"status": "ok", "retcode": 0, "data": {}}


def make_ext():
    ext = OB11ExtensionApi()
    ext._adapter = RecordingAdapter()
    ext._account_id = "default"
    return ext


class TestGetQzoneFeeds:
    def test_default_page_num_is_one(self):
        ext = make_ext()
        asyncio_run(ext.get_qzone_feeds())
        endpoint, params = ext._adapter.calls[0]
        assert endpoint == "get_qzone_feeds"
        assert params["page_num"] == 1

    def test_non_positive_clamped_to_one(self):
        ext = make_ext()
        asyncio_run(ext.get_qzone_feeds(page_num=0))
        assert ext._adapter.calls[0][1]["page_num"] == 1

    def test_valid_page_num_preserved(self):
        ext = make_ext()
        asyncio_run(ext.get_qzone_feeds(page_num=3))
        assert ext._adapter.calls[0][1]["page_num"] == 3


def asyncio_run(coro):
    import asyncio

    return asyncio.run(coro)
