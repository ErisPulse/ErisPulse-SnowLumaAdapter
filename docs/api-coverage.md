# SnowLumaAdapter × 官方 API 覆盖对照表

- 官方动作目录：`snowluma` API 文档数据源，共 **200 个动作**
- 通用封装（OB11ExtensionApi）：127 个 ｜ SnowLuma 特有封装（SnowLumaExtensionApi）：42 个 ｜ Core 直调：26 个 ｜ ApiDSL 透传：3 个 ｜ 别名：2 个 ｜ 未封装：0 个
- 未封装动作均可通过 `adapter.Api.call("动作名", ...)` 或 `adapter.call_api(动作名, _account_id=..., ...)` 透明调用

## 信息（5 个）

| 动作 | 状态 | 只读/可写 | 说明 |
|---|---|---|---|
| `can_send_image` | ✅ 通用封装 | 只读 | — |
| `can_send_record` | ✅ 通用封装 | 只读 | — |
| `get_login_info` | 🔧 Core 直调 | 只读 | — |
| `get_status` | ⚙️ ApiDSL 透传 | 只读 | — |
| `get_version_info` | ✅ 通用封装 | 只读 | — |

## 消息（6 个）

| 动作 | 状态 | 只读/可写 | 说明 |
|---|---|---|---|
| `delete_msg` | 🔧 Core 直调 | 可写 | 撤回消息 |
| `get_msg` | 🔧 Core 直调 | 只读 | 获取消息 |
| `send_custom_face` | 🔧 Core 直调 | 可写 | 发送账号收藏表情（emoji_id 或 MD5），保留表情显示样式 |
| `send_group_msg` | ⚙️ ApiDSL 透传 | 可写 | 发送群消息 |
| `send_msg` | 🔧 Core 直调 | 可写 | 发送消息（按 message_type/群号 自动路由群聊或私聊） |
| `send_private_msg` | ⚙️ ApiDSL 透传 | 可写 | 发送私聊消息 |

## 好友（3 个）

| 动作 | 状态 | 只读/可写 | 说明 |
|---|---|---|---|
| `delete_friend` | ✅ 通用封装 | 可写 | 删除好友 |
| `get_friend_list` | 🔧 Core 直调 | 只读 | 获取好友列表 |
| `get_stranger_info` | 🔧 Core 直调 | 只读 | 获取陌生人信息 |

## 群信息（7 个）

| 动作 | 状态 | 只读/可写 | 说明 |
|---|---|---|---|
| `get_group_honor_info` | ✅ 通用封装 | 只读 | 获取群荣誉信息 |
| `get_group_info` | 🔧 Core 直调 | 只读 | 获取群信息 |
| `get_group_list` | 🔧 Core 直调 | 只读 | 获取群列表 |
| `get_group_member_info` | 🔧 Core 直调 | 只读 | 获取群成员信息 |
| `get_group_member_list` | 🔧 Core 直调 | 只读 | 获取群成员列表 |
| `get_group_share_link` | ✅ 通用封装 | 只读 | 获取群分享链接 |
| `get_group_system_msg` | ✅ 通用封装 | 只读 | 获取群系统消息 |

## 群管理（21 个）

| 动作 | 状态 | 只读/可写 | 说明 |
|---|---|---|---|
| `add_group_tag` | ✅ 通用封装 | 可写 | 向某个群分类添加资料标签 |
| `delete_group_tag` | ✅ 通用封装 | 可写 | 从某个群分类移除资料标签 |
| `get_group_admin_settings` | ✅ 通用封装 | 只读 | 获取群管理设置的当前值 |
| `get_group_tags` | ✅ 通用封装 | 只读 | 读取某个群分类下的资料标签 |
| `set_group_add_option` | ✅ 通用封装 | 可写 | 设置加群选项 |
| `set_group_admin` | 🔧 Core 直调 | 可写 | 设置/取消管理员 |
| `set_group_anonymous` | ✅ 通用封装 | 可写 | 匿名开关（未实现，返回 ok） |
| `set_group_anonymous_ban` | ✅ 通用封装 | 可写 | 匿名禁言（未实现，返回 ok） |
| `set_group_ban` | 🔧 Core 直调 | 可写 | 禁言群成员（duration=0 解除） |
| `set_group_card` | 🔧 Core 直调 | 可写 | 设置群名片（空字符串清除） |
| `set_group_kick` | 🔧 Core 直调 | 可写 | 踢出群成员 |
| `set_group_kick_members` | ✅ 通用封装 | 可写 | 批量踢出群成员 |
| `set_group_leave` | 🔧 Core 直调 | 可写 | 退群 |
| `set_group_member_invite_policy` | ✅ 通用封装 | 可写 | 设置群成员邀请策略 |
| `set_group_member_permissions` | ✅ 通用封装 | 可写 | 设置群成员权限（仅群主可改） |
| `set_group_name` | 🔧 Core 直调 | 可写 | 设置群名 |
| `set_group_new_member_history_visibility` | ✅ 通用封装 | 可写 | 设置新成员是否可查看历史消息 |
| `set_group_portrait` | 🔧 Core 直调 | 可写 | 设置群头像 |
| `set_group_search` | ✅ 通用封装 | 可写 | 设置群被搜索方式（群指纹 / 群号搜索开关） |
| `set_group_special_title` | 🔧 Core 直调 | 可写 | 设置群头衔 |
| `set_group_whole_ban` | 🔧 Core 直调 | 可写 | 全员禁言开关 |

## 群文件（12 个）

| 动作 | 状态 | 只读/可写 | 说明 |
|---|---|---|---|
| `create_group_file_folder` | ✅ 通用封装 | 可写 | 创建群文件夹 |
| `delete_group_file` | ✅ 通用封装 | 可写 | 删除群文件 |
| `delete_group_file_folder` | ✅ 通用封装 | 可写 | 删除群文件夹 |
| `get_group_file_url` | ✅ 通用封装 | 只读 | 获取群文件下载链接 |
| `get_group_files_by_folder` | ✅ 通用封装 | 只读 | 获取群子目录文件列表 |
| `get_group_root_files` | ✅ 通用封装 | 只读 | 获取群根目录文件列表 |
| `get_private_file_url` | ✅ 通用封装 | 只读 | 获取私聊文件下载链接 |
| `move_group_file` | ✅ 通用封装 | 可写 | 移动群文件 |
| `rename_group_file` | ✅ 通用封装 | 可写 | 重命名群文件 |
| `rename_group_file_folder` | ✅ 通用封装 | 可写 | 重命名群文件夹 |
| `upload_group_file` | 🔧 Core 直调 | 可写 | 上传群文件 |
| `upload_private_file` | 🔧 Core 直调 | 可写 | 上传私聊文件 |

## 请求（2 个）

| 动作 | 状态 | 只读/可写 | 说明 |
|---|---|---|---|
| `set_friend_add_request` | 🔧 Core 直调 | 可写 | 处理好友添加请求 |
| `set_group_add_request` | 🔧 Core 直调 | 可写 | 处理加群请求 |

## 群相册（9 个）

| 动作 | 状态 | 只读/可写 | 说明 |
|---|---|---|---|
| `cancel_group_album_media_like` | ❄️ SnowLuma 特有封装 | 可写 | — |
| `del_group_album_media` | ❄️ SnowLuma 特有封装 | 可写 | 删除群相册图片或视频 |
| `do_group_album_comment` | ❄️ SnowLuma 特有封装 | 可写 | — |
| `get_group_album_list` | ✅ 通用封装 | 只读 | — |
| `get_group_album_media_list` | ✅ 通用封装 | 只读 | — |
| `get_qun_album_list` | ❄️ SnowLuma 特有封装 | 只读 | — |
| `set_group_album_media_like` | ❄️ SnowLuma 特有封装 | 可写 | — |
| `upload_image_to_qun_album` | ❄️ SnowLuma 特有封装 | 可写 | — |
| `upload_video_to_qun_album` | ❄️ SnowLuma 特有封装 | 可写 | 上传视频到群相册 |

## 空间（10 个）

| 动作 | 状态 | 只读/可写 | 说明 |
|---|---|---|---|
| `comment_qzone` | ✅ 通用封装 | 可写 | 评论一条说说（QQ 空间，支持纯文字或带图；传 images 自动上传） |
| `delete_qzone_msg` | ✅ 通用封装 | 可写 | 删除一条说说（QQ 空间，按 tid） |
| `get_qzone_feeds` | ✅ 通用封装 | 只读 | 获取 QQ 空间好友动态（feed）；page_num 仅首页可靠，深翻页需时间游标（暂未实现） |
| `get_qzone_msg_detail` | ❄️ SnowLuma 特有封装 | 只读 | 获取 QQ 空间说说详情与一页评论（含服务端内联回复，需有访问权限） |
| `get_qzone_msg_list` | ✅ 通用封装 | 只读 | 获取 QQ 空间说说列表（默认机器人自己的空间） |
| `like_qzone` | ✅ 通用封装 | 可写 | 给一条说说点赞（QQ 空间） |
| `send_qzone_msg` | ✅ 通用封装 | 可写 | 发表说说（QQ 空间，支持纯文字或带图；传 images 自动上传；可设置查看权限） |
| `set_qzone_ban` | ❄️ SnowLuma 特有封装 | 可写 | 拉黑或解除拉黑某人（修改机器人自身 QQ 空间黑名单；enable=true 拉黑，false 解除） |
| `set_qzone_msg_right` | ❄️ SnowLuma 特有封装 | 可写 | 修改一条已发说说的查看权限（QQ 空间，按 tid） |
| `unlike_qzone` | ✅ 通用封装 | 可写 | 取消对一条说说的点赞（QQ 空间；取消赞端点待真机核实） |

## 系统表情（4 个）

| 动作 | 状态 | 只读/可写 | 说明 |
|---|---|---|---|
| `fetch_face_entity` | ❄️ SnowLuma 特有封装 | 只读 | 按编号查询 QQ 系统表情 |
| `fetch_super_face_id` | ❄️ SnowLuma 特有封装 | 只读 | 判断 QQ 系统表情是否使用超级表情格式 |
| `fetch_sys_faces` | ❄️ SnowLuma 特有封装 | 只读 | 获取 QQ 系统表情目录 |
| `search_sys_faces` | ❄️ SnowLuma 特有封装 | 只读 | 搜索 QQ 系统表情 |

## 流式接口（6 个）

| 动作 | 状态 | 只读/可写 | 说明 |
|---|---|---|---|
| `clean_stream_temp_file` | ❄️ SnowLuma 特有封装 | 可写 | 清理流式传输临时文件(仅清理 stream 上传/下载目录) |
| `download_file_image_stream` | ❄️ SnowLuma 特有封装 | 可写 | 以流式方式下载图片(缓存图片 id / URL / stream 目录本地文件) |
| `download_file_record_stream` | ❄️ SnowLuma 特有封装 | 可写 | 以流式方式下载语音(缓存语音 id / URL / stream 目录本地文件) |
| `download_file_stream` | ❄️ SnowLuma 特有封装 | 可写 | 以流式方式下载文件(stream 目录本地文件 / URL / 缓存媒体) |
| `test_download_stream` | ❄️ SnowLuma 特有封装 | 可写 | 测试下载流(推送 10 个数据帧,验证流式传输,不触达 QQ) |
| `upload_file_stream` | ❄️ SnowLuma 特有封装 | 可写 | 以流式分块方式上传文件到机器人本地(返回可用于发送的本地路径) |

## 扩展（115 个）

| 动作 | 状态 | 只读/可写 | 说明 |
|---|---|---|---|
| `.get_word_slices` | ✅ 通用封装 | 只读 | 分词（未实现） |
| `_del_group_notice` | ✅ 通用封装 | 可写 | 删除群公告（fid 或 notice_id 二选一） |
| `_get_friend_dress` | ✅ 通用封装 | 只读 | 获取指定 QQ 号正在使用的个性装扮（挂件/名片/来电/输入状态等） |
| `_get_group_notice` | ✅ 通用封装 | 只读 | 获取群公告 |
| `_get_model_show` | ✅ 通用封装 | 只读 | 获取机型展示（兼容 mock） |
| `_mark_all_as_read` | ✅ 通用封装 | 可写 | 标记全部已读 |
| `_send_group_notice` | ✅ 通用封装 | 可写 | 发送群公告（支持置顶、弹窗、新成员、群昵称引导与确认） |
| `_set_model_show` | ✅ 通用封装 | 可写 | 设置机型展示（占位） |
| `add_custom_face` | ❄️ SnowLuma 特有封装 | 可写 | 添加收藏表情 |
| `bot_exit` | ❄️ SnowLuma 特有封装 | 可写 | 退出机器人 |
| `cancel_group_todo` | ✅ 通用封装 | 可写 | 取消群待办 |
| `check_url_safely` | ✅ 通用封装 | 只读 | 检查链接安全性 |
| `clean_cache` | ✅ 通用封装 | 可写 | 清理缓存 |
| `click_inline_keyboard_button` | ✅ 通用封装 | 可写 | 点击内联键盘按钮 |
| `complete_group_todo` | ✅ 通用封装 | 可写 | 完成群待办 |
| `create_collection` | ❄️ SnowLuma 特有封装 | 可写 | 创建收藏（未实现） |
| `create_flash_task` | ❄️ SnowLuma 特有封装 | 可写 | 创建闪传任务 |
| `delete_custom_face` | ❄️ SnowLuma 特有封装 | 可写 | 删除收藏表情 |
| `delete_essence_msg` | ✅ 通用封装 | 可写 | 移除精华消息 |
| `delete_flash_file` | ❄️ SnowLuma 特有封装 | 可写 | 删除闪传文件 |
| `delete_group_folder` | ↩️ 别名（调 `delete_group_file_folder` 即可） | 可写 | 删除群文件夹 |
| `download_file` | ✅ 通用封装 | 可写 | 下载文件（url 或 base64）到 data/downloads |
| `download_fileset` | ❄️ SnowLuma 特有封装 | 可写 | 解析闪传文件下载直链（不下载，由调用方实现下载） |
| `fetch_custom_face` | ❄️ SnowLuma 特有封装 | 只读 | 获取自定义表情 |
| `fetch_custom_face_detail` | ❄️ SnowLuma 特有封装 | 只读 | 获取自定义表情详情 |
| `fetch_emoji_like` | ✅ 通用封装 | 只读 | 获取表情回应用户（NapCat 分页） |
| `fetch_ptt_text` | ✅ 通用封装 | 只读 | 获取语音转文字结果 |
| `forward_friend_single_msg` | ✅ 通用封装 | 可写 | 转发单条消息给好友 |
| `forward_group_single_msg` | ✅ 通用封装 | 可写 | 转发单条消息到群 |
| `friend_poke` | ✅ 通用封装 | 可写 | 好友拍一拍 |
| `get_ai_characters` | ✅ 通用封装 | 只读 | 获取 AI 语音角色 |
| `get_ai_record` | ✅ 通用封装 | 可写 | 生成 AI 语音 |
| `get_clientkey` | ✅ 通用封装 | 只读 | 获取 clientkey |
| `get_collection_list` | ❄️ SnowLuma 特有封装 | 只读 | 获取收藏列表 |
| `get_cookies` | ✅ 通用封装 | 只读 | 获取 Cookies |
| `get_credentials` | ✅ 通用封装 | 只读 | 获取凭证 |
| `get_csrf_token` | ✅ 通用封装 | 只读 | 获取 CSRF 令牌 |
| `get_doubt_friends_add_request` | ✅ 通用封装 | 只读 | 获取可疑好友申请 |
| `get_emoji_likes` | ✅ 通用封装 | 只读 | 获取表情回应用户 |
| `get_essence_msg_list` | ✅ 通用封装 | 只读 | 获取精华消息列表 |
| `get_file` | ✅ 通用封装 | 只读 | 获取文件信息（仅图片/语音缓存；群文件请用 get_group_file_url） |
| `get_fileset_id` | ❄️ SnowLuma 特有封装 | 只读 | 从 QQ 闪传分享码或官方分享链接获取 fileset_id |
| `get_fileset_info` | ❄️ SnowLuma 特有封装 | 可写 | 获取文件集信息 |
| `get_flash_file_list` | ❄️ SnowLuma 特有封装 | 可写 | 获取闪传文件列表 |
| `get_flash_file_url` | ❄️ SnowLuma 特有封装 | 可写 | 获取闪传文件链接 |
| `get_forward_msg` | ✅ 通用封装 | 只读 | 获取合并转发消息（id 或 message_id） |
| `get_friend_msg_history` | ✅ 通用封装 | 只读 | 获取好友消息历史（无锚点时从服务器获取最新双向记录） |
| `get_friends_with_category` | ✅ 通用封装 | 只读 | 获取分组好友列表 |
| `get_group_at_all_remain` | ✅ 通用封装 | 只读 | 获取群 @全体成员 剩余次数 |
| `get_group_detail_info` | ✅ 通用封装 | 只读 | 获取群详细信息 |
| `get_group_file_system_info` | ✅ 通用封装 | 只读 | 获取群文件系统信息 |
| `get_group_ignore_add_request` | ✅ 通用封装 | 只读 | 获取被忽略的入群请求（NapCat） |
| `get_group_ignored_notifies` | ✅ 通用封装 | 只读 | 获取被过滤的入群请求 |
| `get_group_info_ex` | ✅ 通用封装 | 只读 | 获取群信息（扩展） |
| `get_group_msg_history` | ✅ 通用封装 | 只读 | 获取群消息历史 |
| `get_group_shut_list` | ✅ 通用封装 | 只读 | 获取群禁言列表 |
| `get_group_signed_list` | ✅ 通用封装 | 只读 | 获取群今日打卡列表 |
| `get_group_todo_list` | ✅ 通用封装 | 只读 | 获取群待办列表 |
| `get_image` | ✅ 通用封装 | 只读 | 获取图片信息 |
| `get_mini_app_ark` | ✅ 通用封装 | 只读 | 获取小程序卡片 ark |
| `get_msg_emoji_likes` | ✅ 通用封装 | 只读 | 获取一条消息的全部表情回应 |
| `get_online_clients` | ✅ 通用封装 | 只读 | 获取在线客户端 |
| `get_profile_like` | ✅ 通用封装 | 只读 | 获取资料点赞 |
| `get_recent_contact` | ✅ 通用封装 | 只读 | 获取最近会话（占位） |
| `get_record` | ✅ 通用封装 | 只读 | 获取语音信息；传 out_format 则服务端转码并附带 base64 |
| `get_rkey` | ✅ 通用封装 | 只读 | 获取下载 rkey |
| `get_rkey_server` | ✅ 通用封装 | 只读 | 获取 rkey 服务器信息 |
| `get_share_link` | ✅ 通用封装 | 可写 | 获取文件分享链接 |
| `get_unidirectional_friend_list` | ✅ 通用封装 | 只读 | 获取单向好友列表 |
| `group_poke` | ✅ 通用封装 | 可写 | 群拍一拍 |
| `list_filesets` | ❄️ SnowLuma 特有封装 | 可写 | 列出当前账号的所有闪传文件集 |
| `mark_group_msg_as_read` | ✅ 通用封装 | 可写 | 标记群消息已读 |
| `mark_msg_as_read` | ✅ 通用封装 | 可写 | 标记消息已读（群聊/私聊自动路由） |
| `mark_private_msg_as_read` | ✅ 通用封装 | 可写 | 标记私聊消息已读 |
| `modify_custom_face` | ❄️ SnowLuma 特有封装 | 可写 | 修改收藏表情备注 |
| `move_custom_face_to_front` | ❄️ SnowLuma 特有封装 | 可写 | 收藏表情移到最前 |
| `nc_get_packet_status` | ❄️ SnowLuma 特有封装 | 只读 | 获取 packet 状态（占位） |
| `nc_get_user_status` | ✅ 通用封装 | 只读 | 获取用户在线/扩展状态 |
| `ocr_image` | ✅ 通用封装 | 只读 | OCR 图片（服务端，需图片 URL 或已缓存的图片 file_id） |
| `rename_flash_file` | ❄️ SnowLuma 特有封装 | 可写 | 重命名闪传文件 |
| `request_decrypt_key` | ❄️ SnowLuma 特有封装 | 可写 | 请求数据库解密密钥 |
| `send_ark_share` | ✅ 通用封装 | 只读 | 分享用户/群 Ark 卡片（NapCat 标准名） |
| `send_flash_msg` | ❄️ SnowLuma 特有封装 | 可写 | 发送闪传消息（私聊或群聊，引用 fileset_id 让对端下载） |
| `send_forward_msg` | ✅ 通用封装 | 可写 | 发送合并转发（按 message_type/群号自动路由） |
| `send_group_ai_record` | ✅ 通用封装 | 可写 | 发送 AI 语音到群 |
| `send_group_ark_share` | ✅ 通用封装 | 只读 | 分享群 Ark 卡片（NapCat 标准名） |
| `send_group_forward_msg` | 🔧 Core 直调 | 可写 | 发送群合并转发 |
| `send_like` | ✅ 通用封装 | 可写 | 点赞 |
| `send_packet` | ❄️ SnowLuma 特有封装 | 可写 | 发送原始 SSO 包（cmd + hex data） |
| `send_poke` | ✅ 通用封装 | 可写 | 拍一拍（群聊/私聊自动路由） |
| `send_private_forward_msg` | 🔧 Core 直调 | 可写 | 发送私聊合并转发 |
| `send_tuwen_ark` | ✅ 通用封装 | 可写 | 发送图文 Ark 卡片（私聊/群聊） |
| `set_diy_online_status` | ✅ 通用封装 | 可写 | 设置自定义在线状态 |
| `set_doubt_friends_add_request` | ✅ 通用封装 | 可写 | 处理可疑好友申请 |
| `set_essence_msg` | ✅ 通用封装 | 可写 | 设置精华消息 |
| `set_friend_remark` | ✅ 通用封装 | 可写 | 设置好友备注 |
| `set_friends_category` | ✅ 通用封装 | 可写 | 移动好友到指定分组 |
| `set_group_reaction` | ✅ 通用封装 | 可写 | 群聊表情回应 |
| `set_group_remark` | ✅ 通用封装 | 可写 | 设置群备注 |
| `set_group_robot_add_option` | ✅ 通用封装 | 可写 | 设置群机器人加群选项 |
| `set_group_sign` | ✅ 通用封装 | 可写 | 群签到 |
| `set_group_todo` | ✅ 通用封装 | 可写 | 设置群待办 |
| `set_input_status` | ✅ 通用封装 | 可写 | 设置输入状态 |
| `set_msg_emoji_like` | ✅ 通用封装 | 可写 | 设置消息表情回应 |
| `set_online_status` | ✅ 通用封装 | 可写 | 设置在线状态 |
| `set_qq_avatar` | ✅ 通用封装 | 可写 | 设置 QQ 头像 |
| `set_qq_profile` | ✅ 通用封装 | 可写 | 设置 QQ 资料 |
| `set_restart` | ✅ 通用封装 | 可写 | 重启（不支持） |
| `set_self_longnick` | ✅ 通用封装 | 可写 | 设置个性签名（longNick/long_nick，严格 string） |
| `share_group_ex` | ✅ 通用封装 | 只读 | 分享群 Ark 卡片 |
| `share_peer` | ✅ 通用封装 | 只读 | 分享用户/群 Ark 卡片 |
| `trans_group_file` | ✅ 通用封装 | 可写 | 转存群文件 |
| `translate_en2zh` | ✅ 通用封装 | 只读 | 英译中 |
| `upload_forward_msg` | ✅ 通用封装 | 可写 | 上传转发消息 |
| `upload_foward_msg` | ↩️ 别名（调 `upload_forward_msg` 即可） | 可写 | 上传转发消息（别名拼写） |
