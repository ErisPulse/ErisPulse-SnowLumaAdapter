# SnowLuma 平台特性文档

SnowLumaAdapter 基于 [SnowLuma](https://github.com/SnowLuma/SnowLuma)（NTQQ hook 框架），使用 OneBot v11 协议通信。作为 `ErisPulse-OneBot11Adapter[snowluma]` 可选扩展安装。

---

## 文档信息

- 对应模块版本: 0.1.0（随 OneBot11Adapter 4.2.0+ 发行）
- 协议版本: OneBot v11（NapCat/go-cqhttp 兼容扩展）
- 安装: `pip install ErisPulse-OneBot11Adapter[snowluma]`

## 基本信息

- 平台简介：SnowLuma 通过 ptrace 注入 NTQQ 客户端，以 OB11 协议暴露 API
- 适配器名称：SnowLumaAdapter
- 配置键名：`SnowLuma_Adapter`
- 默认端口：WS 3001 / HTTP 3000

## 配置

```toml
[SnowLuma_Adapter.accounts.default]
mode = "client"
url = "ws://127.0.0.1:3001"
token = "your_access_token"
enabled = true
```

| 字段 | 默认值 | 说明 |
|------|--------|------|
| `mode` | `"client"` | server(被动) 或 client(主动) |
| `url` | `"ws://127.0.0.1:3001"` | Client 模式 WS 地址 |
| `token` | `""` | Bearer 认证令牌 |
| `server_path` | `"/"` | Server 模式 WS 路径 |

## 标准 API 动作（ApiDSL）

SnowLuma 原生支持 OB11 协议，ApiDSL 自动映射 OB12 标准动作名：

```python
snowluma = sdk.adapter.get("snowluma")

# 标准 OB12 动作（自动映射到 OB11 动作名）
info = await snowluma.Api.get_self_info()          # → get_login_info
user = await snowluma.Api.get_user_info("123456")  # → get_stranger_info
await snowluma.Api.delete_message("msg_123")       # → delete_msg
await snowluma.Api.leave_group("group_123")        # → set_group_leave
```

### upload_file（扩展参数）

OB11 文件上传绑定目标，`upload_file` 扩展了 `group_id`/`user_id` 可选参数：

```python
await snowluma.Api.upload_file(type="path", name="doc.pdf", path="./doc.pdf", group_id="123456")
await snowluma.Api.upload_file(type="url", name="img.jpg", url="https://...", user_id="789")
```

## OB11 协议扩展

SnowLuma 兼容 NapCat/go-cqhttp 扩展接口（109 个动作）。这些是 **OB11 协议级扩展**，不加平台前缀，NapCat/Lagrange 等后端通用。

### 类型化 Api 方法（推荐，带 IDE 补全）

高频扩展动作已封装为 `Api` 类的类型化方法，支持 IDE 补全方法名和参数：

```python
snowluma = sdk.adapter.get("snowluma")

# 拍一拍
await snowluma.Api.send_poke(user_id=789, group_id=123456)
await snowluma.Api.group_poke(group_id=123456, user_id=789)
await snowluma.Api.friend_poke(user_id=789)

# 消息回应
await snowluma.Api.set_msg_emoji_like(message_id=123, emoji_id="76")
await snowluma.Api.set_essence_msg(message_id=123)
result = await snowluma.Api.get_essence_msg_list(group_id=123456)

# 已读 / 状态
await snowluma.Api.mark_msg_as_read(group_id=123456)
await snowluma.Api.set_online_status(status=11)

# 消息历史
result = await snowluma.Api.get_group_msg_history(group_id=123456, count=20)
result = await snowluma.Api.get_friend_msg_history(user_id=789, count=20)

# 群管理
await snowluma.Api.set_group_reaction(group_id=123456, message_id=123, code="76")
await snowluma.Api.set_group_sign(group_id=123456)
await snowluma.Api.set_group_remark(group_id=123456, remark="我的群")

# 群文件
result = await snowluma.Api.get_group_file_url(group_id=123456, file_id="abc")
result = await snowluma.Api.get_group_root_files(group_id=123456)

# QQ 空间
await snowluma.Api.send_qzone_msg(content="发表说说")
await snowluma.Api.like_qzone(tid="tid_123")
result = await snowluma.Api.get_qzone_feeds(page_num=0)

# 媒体 / OCR
result = await snowluma.Api.ocr_image(image="https://example.com/img.png")
result = await snowluma.Api.get_image(file="abc.png")
result = await snowluma.Api.fetch_ptt_text(file="voice.silk")

# 凭证
result = await snowluma.Api.get_cookies(domain="qzone.qq.com")
result = await snowluma.Api.get_csrf_token()
```

### Api.call 逃生舱（未封装的动作用）

```python
# 少数未封装的动作用 call() 直接调用
result = await snowluma.Api.call("send_group_ai_record", group_id=123456, content="...")
```

> **命名约定**：OB11 协议扩展直接用动作名（`send_poke`），不加 `snowluma.` 前缀。只有真正平台独有的功能才用 `{prefix}.xxx`。

## Send 便捷方法

### 标准消息发送

继承 OneBot11 全部发送能力（Text/Image/Voice/Video/Face/File/Raw_ob12）及群管理方法（Kick/Ban/SetAdmin 等）。

### SnowLuma/NapCat 扩展便捷方法

| 方法 | 对应动作 | 说明 |
|------|---------|------|
| `.QzoneMsg(content)` | `send_qzone_msg` | 发表 QQ 空间说说 |
| `.QzoneLike(tid)` | `like_qzone` | QQ 空间点赞 |
| `.QzoneUnlike(tid)` | `unlike_qzone` | 取消点赞 |
| `.QzoneComment(tid, content)` | `comment_qzone` | 评论说说 |
| `.QzoneDelete(tid)` | `delete_qzone_msg` | 删除说说 |
| `.GroupPoke(user_id)` | `group_poke` | 群拍一拍（需 To("group", gid)） |
| `.FriendPoke(user_id)` | `friend_poke` | 好友拍一拍 |
| `.SendPoke(user_id)` | `send_poke` | 拍一拍（自动路由） |
| `.SetMsgEmojiLike(msg_id, emoji_id)` | `set_msg_emoji_like` | 消息表情回应 |
| `.UploadGroupFile(file, name)` | `upload_group_file` | 上传群文件（需 To("group", gid)） |
| `.GetGroupFileUrl(file_id)` | `get_group_file_url` | 群文件下载链接 |
| `.MarkMsgAsRead()` | `mark_msg_as_read` | 标记已读（需 To()） |
| `.SetOnlineStatus(status)` | `set_online_status` | 设置在线状态 |
| `.GetGroupMsgHistory(seq, count)` | `get_group_msg_history` | 群消息历史 |
| `.GetFriendMsgHistory(uid, count)` | `get_friend_msg_history` | 好友消息历史 |
| `.GroupReaction(msg_id, emoji_id)` | `set_group_reaction` | 群表情回应 |
| `.SetEssenceMsg(msg_id)` | `set_essence_msg` | 设置精华消息 |
| `.DeleteEssenceMsg(msg_id)` | `delete_essence_msg` | 移除精华消息 |
| `.SetFriendRemark(uid, remark)` | `set_friend_remark` | 设置好友备注 |
| `.OcrImage(image)` | `ocr_image` | OCR 图片识别 |
| `.GetImage(file)` | `get_image` | 获取图片信息 |
| `.GetRecord(file)` | `get_record` | 获取语音信息 |
| `.FetchPttText(file)` | `fetch_ptt_text` | 语音转文字 |

```python
snowluma = sdk.adapter.get("snowluma")

# QQ 空间
await snowluma.Send.QzoneMsg("发表说说")
await snowluma.Send.QzoneLike("tid_123")

# 群操作
await snowluma.Send.To("group", 123456).GroupPoke(789012)
await snowluma.Send.To("group", 123456).UploadGroupFile("./doc.pdf", "文档.pdf")

# 消息回应
await snowluma.Send.SetMsgEmojiLike("msg_123", "76")
await snowluma.Send.SetEssenceMsg("msg_123")

# 标记已读
await snowluma.Send.To("group", 123456).MarkMsgAsRead()
```

## 事件类型

SnowLuma 事件完全遵循 OB11 标准，转换器将 OB11 事件映射为 OB12 格式（platform="snowluma"）。事件扩展字段使用 `snowluma_` 前缀：

- `snowluma_raw`：原始 OB11 事件数据
- `snowluma_raw_type`：原始事件类型
- `snowluma_notice` / `snowluma_request` / `snowluma_meta`：子事件原始数据

### EventMixin 方法

| 方法 | 返回类型 | 说明 |
|------|----------|------|
| `get_raw_event()` | `dict` | 获取原始事件（snowluma_raw） |
| `get_raw_self_id()` | `str` | 获取 Bot 的 QQ 号 |
| `get_sender_info()` | `dict` | 完整发送者信息 |
| `get_sender_role()` | `str` | 群角色（owner/admin/member） |
| `get_sender_level()` | `int` | 发送者等级 |
| `get_sender_title()` | `str` | 群头衔 |
| `is_system_message()` | `bool` | 是否系统消息 |

## i18n

支持 5 语言：zh-CN / zh-TW / en / ja / ru。
