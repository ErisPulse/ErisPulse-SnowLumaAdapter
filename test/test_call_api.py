"""
SnowLuma call_api 测试：None 参数剥离、echo 防碰撞、http 模式调用
"""

import asyncio
import json
from types import SimpleNamespace
from unittest.mock import patch

import pytest

import SnowLumaAdapter.Core as CoreModule
from SnowLumaAdapter.Core import SnowLumaAdapter, SnowLumaAccountConfig


class FakeConnection:
    """伪 WS 连接：捕获发送的 payload 并立即回填 echo 响应"""

    def __init__(self, adapter, account_name):
        self.adapter = adapter
        self.account_name = account_name
        self.closed = False
        self.sent = []

    async def send_text(self, text):
        self.sent.append(text)
        payload = json.loads(text)
        echo = payload["echo"]
        loop = asyncio.get_event_loop()
        loop.call_soon(
            self._resolve,
            echo,
            {"status": "ok", "retcode": 0, "data": {"message_id": 1}, "echo": echo},
        )

    def _resolve(self, echo, response):
        future = self.adapter._api_response_futures.get(self.account_name, {}).get(echo)
        if future and not future.done():
            future.set_result(response)


def make_adapter(mode: str = "client", token: str = ""):
    # BaseAdapter 仅在传入 sdk 引用时建立 self.logger，测试用桩提供
    from ErisPulse.Core import logger as global_logger

    sdk_stub = SimpleNamespace(
        logger=SimpleNamespace(
            get_child=lambda name, relative=False: global_logger
        )
    )
    adapter = SnowLumaAdapter(sdk_ref=sdk_stub)
    account = SnowLumaAccountConfig(mode=mode, token=token)
    adapter._resolve_account = lambda _account_id=None: ("default", account)
    return adapter, account


class TestNoneParamStripping:
    def test_group_send_strips_user_id_none(self):
        """群发时显式传入的 user_id=None 必须被剥离（SnowLuma 拒收 null 报 1400）"""
        adapter, _ = make_adapter()
        conn = FakeConnection(adapter, "default")
        adapter.connections["default"] = conn

        result = asyncio.run(adapter.call_api(
            "send_msg",
            _account_id="default",
            message_type="group",
            user_id=None,
            group_id=123456,
            message=[{"type": "text", "data": {"text": "hi"}}],
        ))
        assert result["status"] == "ok"
        payload = json.loads(conn.sent[0])
        # None 参数必须被剥离，不得以 null 形式出现在 params 中
        assert "user_id" not in payload["params"]
        assert payload["params"]["group_id"] == 123456


class TestEchoUniqueness:
    def test_concurrent_identical_calls_no_echo_collision(self):
        """并发同参数调用的 echo 必须不同（旧 hash 实现会串台）"""
        adapter, _ = make_adapter()
        conn = FakeConnection(adapter, "default")
        adapter.connections["default"] = conn

        async def run():
            kwargs = dict(
                _account_id="default",
                message_type="group",
                group_id=1,
                message=[{"type": "text", "data": {"text": "x"}}],
            )
            return await asyncio.gather(adapter.call_api("send_msg", **kwargs), adapter.call_api("send_msg", **kwargs))

        r1, r2 = asyncio.run(run())
        echoes = [json.loads(s)["echo"] for s in conn.sent]
        assert len(set(echoes)) == 2, "两个并发请求的 echo 不应相同"
        assert r1["status"] == "ok" and r2["status"] == "ok"


class TestHttpMode:
    def test_http_call_posts_json_without_none(self):
        adapter, account = make_adapter(mode="http", token="s3cret")
        account.http_url = "http://127.0.0.1:3000"

        captured = {}

        class FakeResp:
            async def json(self):
                return {"status": "ok", "retcode": 0, "data": {"message_id": 9}, "echo": ""}

        class FakeClient:
            async def post(self, url, *, json=None, headers=None, timeout=None):
                captured["url"] = url
                captured["json"] = json
                captured["headers"] = headers
                return FakeResp()

        async def run():
            with patch.object(CoreModule, "client", FakeClient()):
                return await adapter.call_api(
                    "send_msg",
                    _account_id="default",
                    message_type="private",
                    user_id=42,
                    group_id=None,
                    message=[],
                )

        result = asyncio.run(run())
        assert result["status"] == "ok"
        assert captured["url"] == "http://127.0.0.1:3000/send_msg"
        assert "group_id" not in captured["json"]
        assert captured["json"]["user_id"] == 42
        assert captured["headers"]["Authorization"] == "Bearer s3cret"
