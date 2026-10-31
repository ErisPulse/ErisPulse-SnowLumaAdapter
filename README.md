[English](README.md) | [简体中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md) | [Русский](README.ru.md)

<div align="center">

<img src="https://raw.githubusercontent.com/ErisPulse/ErisPulse/main/.github/assets/ErisPulseLogo.png" width="180" alt="ErisPulse-SnowLumaAdapter" />

# ErisPulse-SnowLumaAdapter

**ErisPulse SnowLuma 适配器 — NTQQ hook、原生合并转发、兼容 NapCat**

<p>
  <a href="https://pypi.org/project/ErisPulse-SnowLumaAdapter/"><img src="https://img.shields.io/pypi/v/ErisPulse-SnowLumaAdapter?style=for-the-badge&logo=pypi&logoColor=white" alt="PyPI"></a>
  <a href="https://pypi.org/project/ErisPulse-SnowLumaAdapter/"><img src="https://img.shields.io/badge/Python-3.10+-FFD43B?style=for-the-badge&logo=python&logoColor=blue" alt="Python"></a>
  <a href="https://github.com/ErisPulse/ErisPulse/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue?style=for-the-badge" alt="License"></a>
  <img src="https://raw.githubusercontent.com/ErisPulse/.github/main/assets/badges/adapter.svg" alt="ErisPulse">
</p>

</div>

---

## 特性

- **完整 OneBot v11 协议**：OB12 标准 ApiDSL 自动映射动作名（`get_self_info` → `get_login_info` 等）
- **合并转发**：`MergeForward` 三级回退（专用端点 → `upload_forward_msg` resid → 直发 node 段），`Raw_ob12` 纯 node 段自动路由
- **全面兼容 NapCat**：`url` 指向 NapCat 正向 WS 即可直接使用，或以 server 模式接收 NapCat 反向 WS
- **60+ 类型化扩展方法**（IDE 补全）：拍一拍 / QQ空间 / 群文件 / 群相册 / 消息历史 / 精华 / 已读状态 / OCR 等
- **109 个扩展动作**均可通过 `Api.call("action_name", ...)` 调用（NapCat/SnowLuma 通用）
- **多账户 + bot_id 自动识别**：无需配置 QQ 号，`event.reply()` 自动路由到来源账户
- **5 语言 i18n**（zh-CN / zh-TW / en / ja / ru）

## 安装

```bash
epsdk install SnowLumaAdapter
```

或直接安装：

```bash
pip install ErisPulse-SnowLumaAdapter
```

## 配置

在 `config/config.toml` 中添加：

```toml
[SnowLuma_Adapter.accounts.default]
mode = "client"                     # client=主动连接（推荐）/ server=被动监听
url = "ws://127.0.0.1:3001"         # SnowLuma 默认 WS 端口 3001
token = "your_access_token"
enabled = true

# 多账户示例
[SnowLuma_Adapter.accounts.second]
mode = "client"
url = "ws://192.168.1.100:3001"
token = "another_token"
enabled = true
```

### 配置字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `mode` | string | 否 | 运行模式：`"client"`（主动连接，默认）或 `"server"`（被动监听） |
| `url` | string | 否 | Client 模式的 WebSocket 地址（默认 `ws://127.0.0.1:3001`） |
| `token` | string | 否 | 访问令牌（Bearer 认证） |
| `server_path` | string | 否 | Server 模式的 WebSocket 路径（默认 `/`） |
| `enabled` | bool | 否 | 是否启用（默认 true） |

> `bot_id`（QQ 号）无需配置：适配器连接后自动识别。连接 NapCat 时把 `url` 指向其 OneBot11 正向 WS 地址即可，标准动作、扩展动作与合并转发均可直接使用。

## 快速开始

```python
from ErisPulse import sdk
from ErisPulse.Core.Event import command, message

@command("hello")
async def hello_handler(event):
    await event.reply("Hello from SnowLuma!")

async def main():
    await sdk.run(keep_running=True)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

## 消息发送

所有发送方法通过链式 DSL 调用：

```python
snowluma = sdk.adapter.get("snowluma")

# 文本消息（链式修饰：@ + 回复）
await snowluma.Send.To("group", 123456).At(789012).Reply(msg_id).Text("Hello World!")

# 私聊 / 图片 / 语音 / 视频 / 文件（支持 URL、Base64、bytes）
await snowluma.Send.To("user", 789012).Text("私聊消息")
await snowluma.Send.To("group", 123456).Image("https://example.com/img.png")

# 合并转发（三级回退，SnowLuma / NapCat 均适用）
nodes = [
    {
        "type": "node",
        "data": {
            "user_id": "10000",
            "nickname": "MyBot",
            "content": [{"type": "text", "data": {"text": "【1/3】标题\n正文…"}}],
        },
    },
]
await snowluma.Send.To("group", 123456).MergeForward(nodes)

# 群操作（需 To("group", group_id)）
await snowluma.Send.To("group", 123456).Ban(789012, duration=3600)   # 禁言
await snowluma.Send.To("group", 123456).Kick(789012)                 # 踢出
await snowluma.Send.To("group", 123456).SetCard(789012, card="新名片")

# 拍一拍 / QQ空间 / 消息历史
await snowluma.Send.To("group", 123456).GroupPoke(789012)
await snowluma.Send.QzoneMsg("发表说说")
result = await snowluma.Send.To("group", 123456).GetGroupMsgHistory(count=20)

# OneBot12 组合消息（纯 node 段列表自动路由合并转发）
ob12_message = [
    {"type": "text", "data": {"text": "你好！"}},
    {"type": "reply", "data": {"message_id": "12345"}},
]
await snowluma.Send.To("group", 123456).Raw_ob12(ob12_message)

# 多账户指定账户发送
await snowluma.Send.Using("second").To("group", 123456).Text("来自第二个账户")
```

## API 调用

```python
# OB12 标准 ApiDSL（自动映射动作名）
info = await snowluma.Api.get_self_info()
await snowluma.Api.delete_message(message_id=123456)

# 类型化扩展方法（IDE 补全）
await snowluma.Api.send_poke(user_id=789, group_id=123456)
await snowluma.Api.set_msg_emoji_like(message_id=123, emoji_id="76")
result = await snowluma.Api.get_group_msg_history(group_id=123456, count=20)
result = await snowluma.Api.get_group_file_url(group_id=123456, file_id="...")

# 解析已收到的合并转发消息（入站 forward 段 data.id 为 resid）
result = await snowluma.Api.get_forward_msg(id="resid_xxx")

# 未封装的动作用 call()（NapCat/SnowLuma 通用）
result = await snowluma.Api.call("send_group_ai_record", group_id=123456, content="...")
```

## 事件

事件遵循 OneBot12 规范：消息事件 `detail_type` 为 `private` / `group`，通知事件映射为标准命名；平台特有事件（poke/honor 等）使用 `snowluma_` 前缀，未识别的 CQ 码以 `onebot11_{type}` 透传，原始数据保留在 `snowluma_raw` 字段。

## 依赖

- `filetype`：媒体类型检测

## 许可证

MIT License
