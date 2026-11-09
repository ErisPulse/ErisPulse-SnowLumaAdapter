"""
请求处理测试：上下文留存、端点路由（kwargs > 缓存 > 回退）、处理后清理
"""

import asyncio
import json
import time
from types import SimpleNamespace
from unittest.mock import patch

from SnowLumaAdapter.Core import SnowLumaAdapter, SnowLumaAccountConfig


GROUP_INVITE_EVENT = {
    "post_type": "request",
    "request_type": "group",
    "sub_type": "invite",
    "flag": "F1",
    "group_id": 123,
    "user_id": 42,
    "self_id": 10001,
    "time": 1700000000,
}


def make_adapter(mode: str = "client", token: str = ""):
    # BaseAdapter 仅在传入 sdk 引用时建立 self.logger，测试用桩提供
    from ErisPulse.Core import logger as global_logger

    sdk_stub = SimpleNamespace(
        logger=SimpleNamespace(get_child=lambda name, relative=False: global_logger)
    )
    adapter = SnowLumaAdapter(sdk_ref=sdk_stub)
    account = SnowLumaAccountConfig(mode=mode, token=token)
    return adapter, account


class RecordingAdapter:
    """桩适配器：记录 call_api 调用与 warning 日志"""

    def __init__(self, ctx=None):
        self.calls = []
        self.warnings = []
        self._request_ctx = dict(ctx or {})
        self.logger = SimpleNamespace(warning=lambda msg: self.warnings.append(msg))

    async def call_api(self, endpoint, _account_id=None, **params):
        self.calls.append((endpoint, _account_id, params))
        return {"status": "ok", "retcode": 0, "data": None, "message_id": "", "message": ""}

    def make_error(self, retcode=34001, message=""):
        return {"status": "failed", "retcode": retcode, "data": None, "message_id": "", "message": message}


def run_accept(make_call):
    """accept()/reject() 返回 Task，须在事件循环内调用并 await"""
    async def run():
        return await make_call()

    return asyncio.run(run())


def _resolve_echo(adapter, account_name, echo, response):
    future = adapter._api_response_futures.get(account_name, {}).get(echo)
    if future and not future.done():
        future.set_result(response)


class TestRememberRequest:
    def test_expiry_cleanup(self):
        adapter, _ = make_adapter()
        adapter._request_ctx["stale"] = {"request_type": "group", "ts": time.time() - 3601}
        adapter.remember_request("F1", request_type="friend")
        assert "stale" not in adapter._request_ctx
        assert adapter._request_ctx["F1"]["request_type"] == "friend"

    def test_capacity_eviction(self):
        adapter, _ = make_adapter()
        adapter._REQ_CTX_MAX = 3
        now = time.time()
        for i, rid in enumerate(["A", "B", "C"]):
            adapter._request_ctx[rid] = {"request_type": "friend", "ts": now + i}
        adapter.remember_request("D", request_type="friend")
        assert len(adapter._request_ctx) == 3
        assert "A" not in adapter._request_ctx  # 最旧 ts 被淘汰
        assert {"B", "C", "D"} <= set(adapter._request_ctx)

    def test_overwrite_idempotent(self):
        adapter, _ = make_adapter()
        adapter.remember_request("F1", request_type="friend", account="default")
        adapter.remember_request("F1", request_type="group", sub_type="invite", group_id="123")
        assert len(adapter._request_ctx) == 1
        entry = adapter._request_ctx["F1"]
        assert entry["request_type"] == "group"
        assert entry["sub_type"] == "invite"
        assert entry["group_id"] == "123"


class TestRoute:
    def test_kwargs_override_cache(self):
        stub = RecordingAdapter({"F1": {"request_type": "group", "sub_type": "invite", "account": "default"}})
        ctx = SnowLumaAdapter.Request(stub, "F1")._route(request_type="friend")
        assert ctx["request_type"] == "friend"
        assert stub.warnings == []

    def test_cache_fills_missing_fields(self):
        stub = RecordingAdapter(
            {"F1": {"request_type": "group", "sub_type": "invite", "group_id": "123", "account": "default"}}
        )
        ctx = SnowLumaAdapter.Request(stub, "F1")._route()
        assert ctx == {
            "request_type": "group",
            "sub_type": "invite",
            "group_id": "123",
            "account": "default",
        }

    def test_fallback_to_friend_with_warning(self):
        stub = RecordingAdapter()
        ctx = SnowLumaAdapter.Request(stub, "F1")._route()
        assert ctx["request_type"] == "friend"
        assert len(stub.warnings) == 1

    def test_private_kwargs_ignored(self):
        # 传 _request_type 私有名的调用方必须被忽略，走缓存路由
        stub = RecordingAdapter({"F1": {"request_type": "group", "sub_type": "invite", "account": "default"}})
        ctx = SnowLumaAdapter.Request(stub, "F1")._route(_request_type="friend")
        assert ctx["request_type"] == "group"


class TestEndpointRouting:
    def test_group_invite_accept(self):
        stub = RecordingAdapter(
            {"F1": {"request_type": "group", "sub_type": "invite", "group_id": "123", "account": "default"}}
        )
        run_accept(lambda: SnowLumaAdapter.Request(stub, "F1").accept())
        endpoint, account_id, params = stub.calls[-1]
        assert endpoint == "set_group_add_request"
        assert account_id == "default"
        assert params["sub_type"] == "invite"
        assert params["approve"] is True

    def test_group_add_sub_type_defaults_to_add(self):
        stub = RecordingAdapter({"F1": {"request_type": "group", "account": "default"}})
        run_accept(lambda: SnowLumaAdapter.Request(stub, "F1").accept())
        endpoint, _, params = stub.calls[-1]
        assert endpoint == "set_group_add_request"
        assert params["sub_type"] == "add"

    def test_friend_accept(self):
        stub = RecordingAdapter({"F1": {"request_type": "friend", "account": "default"}})
        run_accept(lambda: SnowLumaAdapter.Request(stub, "F1").accept())
        endpoint, _, params = stub.calls[-1]
        assert endpoint == "set_friend_add_request"
        assert params["approve"] is True
        assert "sub_type" not in params

    def test_reject_passes_approve_false(self):
        stub = RecordingAdapter({"F1": {"request_type": "friend"}})
        run_accept(lambda: SnowLumaAdapter.Request(stub, "F1").reject())
        endpoint, _, params = stub.calls[-1]
        assert endpoint == "set_friend_add_request"
        assert params["approve"] is False

    def test_using_account_wins_over_cache(self):
        stub = RecordingAdapter({"F1": {"request_type": "friend", "account": "default"}})
        run_accept(lambda: SnowLumaAdapter.Request(stub, "F1").Using("bot2").accept())
        _, account_id, _ = stub.calls[-1]
        assert account_id == "bot2"


class TestCleanupAfterSuccess:
    def test_success_pops_cache(self):
        stub = RecordingAdapter({"F1": {"request_type": "friend", "account": "default"}})
        run_accept(lambda: SnowLumaAdapter.Request(stub, "F1").accept())
        assert "F1" not in stub._request_ctx

    def test_failure_keeps_cache(self):
        stub = RecordingAdapter({"F1": {"request_type": "friend", "account": "default"}})

        async def failing_call_api(endpoint, _account_id=None, **params):
            return {"status": "failed", "retcode": 1200, "data": None, "message_id": "", "message": "boom"}

        stub.call_api = failing_call_api
        result = run_accept(lambda: SnowLumaAdapter.Request(stub, "F1").accept())
        assert result["status"] == "failed"
        assert "F1" in stub._request_ctx


class TestEventHook:
    """事件入口留存：WS/poll/webhook 共用的 _dispatch_event 在 emit 前写入 _request_ctx"""

    def _dispatch(self, raw_event):
        adapter, _ = make_adapter()
        captured = {}

        async def fake_emit(event):
            captured.update(event)

        async def run():
            from ErisPulse.Core import adapter as adapter_mgr

            with patch.object(adapter_mgr, "emit", fake_emit):
                await adapter._dispatch_event(dict(raw_event), "default")

        asyncio.run(run())
        return adapter, captured

    def test_group_invite_event_remembered(self):
        adapter, captured = self._dispatch(GROUP_INVITE_EVENT)
        entry = adapter._request_ctx["F1"]
        assert entry["request_type"] == "group"
        assert entry["sub_type"] == "invite"
        assert entry["group_id"] == "123"
        # 缓存账户存账户受理名（call_api 可直接路由），非 bot_id
        assert entry["account"] == "default"

    def test_friend_event_remembered(self):
        adapter, _ = self._dispatch(
            {
                "post_type": "request",
                "request_type": "friend",
                "flag": "F2",
                "user_id": 42,
                "self_id": 10001,
                "time": 1700000000,
            }
        )
        entry = adapter._request_ctx["F2"]
        assert entry["request_type"] == "friend"
        assert entry["sub_type"] is None
        assert entry["group_id"] is None


class TestEndToEnd:
    """转换 + 留存 + 受理全链路：群邀请必须路由到 set_group_add_request"""

    def test_group_invite_dispatch_then_accept(self):
        adapter, account = make_adapter()
        adapter._resolve_account = lambda _account_id=None: ("default", account)
        conn_sent = []

        class FakeConnection:
            closed = False

            async def send_text(self, text):
                conn_sent.append(json.loads(text))
                echo = json.loads(text)["echo"]
                loop = asyncio.get_event_loop()
                loop.call_soon(
                    _resolve_echo, adapter, "default", echo,
                    {"status": "ok", "retcode": 0, "data": {}, "echo": echo},
                )

        adapter.connections["default"] = FakeConnection()

        async def fake_emit(event):
            pass

        async def run():
            from ErisPulse.Core import adapter as adapter_mgr

            with patch.object(adapter_mgr, "emit", fake_emit):
                await adapter._dispatch_event(dict(GROUP_INVITE_EVENT), "default")
                await adapter.Request("F1").accept()

        asyncio.run(run())
        assert len(conn_sent) == 1
        assert conn_sent[0]["action"] == "set_group_add_request"
        assert conn_sent[0]["params"]["sub_type"] == "invite"
        assert conn_sent[0]["params"]["approve"] is True
        assert conn_sent[0]["params"]["flag"] == "F1"
