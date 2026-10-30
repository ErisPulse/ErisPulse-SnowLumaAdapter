"""
SnowLuma 适配器 i18n 翻译键声明

覆盖 5 种语言：zh-CN / zh-TW / en / ja / ru
"""

from ErisPulse.Core.Bases import BaseI18n, I18nKey


class SnowLumaI18n(BaseI18n):
    """SnowLuma 适配器翻译键声明"""

    mode: I18nKey = I18nKey(
        default="Connection mode: server (reverse WS) / client (forward WS) / http (HTTP API + polling) / webhook (HTTP API + event reporting)",
        zh_CN="连接模式: server(反向WS) / client(正向WS) / http(HTTP API+轮询) / webhook(HTTP API+上报)",
        zh_TW="連線模式: server(反向WS) / client(正向WS) / http(HTTP API+輪詢) / webhook(HTTP API+上報)",
        en="Connection mode: server (reverse WS) / client (forward WS) / http (HTTP API + polling) / webhook (HTTP API + event reporting)",
        ja="接続モード: server(逆方向WS) / client(順方向WS) / http(HTTP API+ポーリング) / webhook(HTTP API+イベント報告)",
        ru="Режим подключения: server (обратный WS) / client (прямой WS) / http (HTTP API + опрос) / webhook (HTTP API + приём событий)",
    )

    mode_server: I18nKey = I18nKey(
        default="Server",
        zh_CN="Server",
        zh_TW="Server",
        en="Server",
        ja="Server",
        ru="Server",
    )

    mode_client: I18nKey = I18nKey(
        default="Client",
        zh_CN="Client",
        zh_TW="Client",
        en="Client",
        ja="Client",
        ru="Client",
    )

    mode_http: I18nKey = I18nKey(
        default="HTTP",
        zh_CN="HTTP",
        zh_TW="HTTP",
        en="HTTP",
        ja="HTTP",
        ru="HTTP",
    )

    mode_webhook: I18nKey = I18nKey(
        default="Webhook",
        zh_CN="Webhook",
        zh_TW="Webhook",
        en="Webhook",
        ja="Webhook",
        ru="Webhook",
    )

    url: I18nKey = I18nKey(
        default="Client mode WebSocket URL (SnowLuma default: ws://127.0.0.1:3001)",
        zh_CN="Client模式 WebSocket 地址（SnowLuma 默认: ws://127.0.0.1:3001）",
        zh_TW="Client模式 WebSocket 位址（SnowLuma 預設: ws://127.0.0.1:3001）",
        en="Client mode WebSocket URL (SnowLuma default: ws://127.0.0.1:3001)",
        ja="Clientモード WebSocket URL（SnowLuma デフォルト: ws://127.0.0.1:3001）",
        ru="URL WebSocket в режиме client (SnowLuma по умолчанию: ws://127.0.0.1:3001)",
    )

    token: I18nKey = I18nKey(
        default="Access token (Bearer authentication)",
        zh_CN="访问令牌（Bearer 认证）",
        zh_TW="存取權杖（Bearer 認證）",
        en="Access token (Bearer authentication)",
        ja="アクセストークン（Bearer 認証）",
        ru="Токен доступа (аутентификация Bearer)",
    )

    server_path: I18nKey = I18nKey(
        default="Server mode WebSocket path",
        zh_CN="Server模式 WebSocket 路径",
        zh_TW="Server模式 WebSocket 路徑",
        en="Server mode WebSocket path",
        ja="Serverモード WebSocket パス",
        ru="Путь WebSocket в режиме server",
    )

    http_url: I18nKey = I18nKey(
        default="HTTP API URL (used by http/webhook modes, SnowLuma default: http://127.0.0.1:3000)",
        zh_CN="HTTP API 地址（http/webhook 模式调用动作使用，SnowLuma 默认: http://127.0.0.1:3000）",
        zh_TW="HTTP API 位址（http/webhook 模式呼叫動作用，SnowLuma 預設: http://127.0.0.1:3000）",
        en="HTTP API URL (used by http/webhook modes, SnowLuma default: http://127.0.0.1:3000)",
        ja="HTTP API URL（http/webhook モードで使用、SnowLuma デフォルト: http://127.0.0.1:3000）",
        ru="URL HTTP API (используется в режимах http/webhook, SnowLuma по умолчанию: http://127.0.0.1:3000)",
    )

    poll_interval: I18nKey = I18nKey(
        default="Event polling interval in seconds for http mode (0 = API only, no events)",
        zh_CN="HTTP模式事件轮询间隔（秒），0 表示纯 API 模式不拉取事件",
        zh_TW="HTTP模式事件輪詢間隔（秒），0 表示純 API 模式不拉取事件",
        en="Event polling interval in seconds for http mode (0 = API only, no events)",
        ja="http モードのイベントポーリング間隔（秒）。0 は API 専用モード",
        ru="Интервал опроса событий в секундах для режима http (0 = только API, без событий)",
    )

    webhook_path: I18nKey = I18nKey(
        default="Event reporting path for webhook mode (final route: /snowluma_{account}{path}, {account} placeholder supported)",
        zh_CN="Webhook模式接收事件上报的路径（最终路由为 /snowluma_{account}{path}，支持 {account} 占位符）",
        zh_TW="Webhook模式接收事件上報的路徑（最終路由為 /snowluma_{account}{path}，支援 {account} 佔位符）",
        en="Event reporting path for webhook mode (final route: /snowluma_{account}{path}, {account} placeholder supported)",
        ja="webhook モードのイベント受信パス（最終ルート: /snowluma_{account}{path}、{account} プレースホルダ対応）",
        ru="Путь приёма событий в режиме webhook (итоговый маршрут: /snowluma_{account}{path}, поддерживается плейсхолдер {account})",
    )

    group_connection: I18nKey = I18nKey(
        default="Connection",
        zh_CN="连接设置",
        zh_TW="連線設定",
        en="Connection",
        ja="接続設定",
        ru="Подключение",
    )

    group_server: I18nKey = I18nKey(
        default="Server",
        zh_CN="服务端模式",
        zh_TW="伺服器模式",
        en="Server",
        ja="サーバー",
        ru="Сервер",
    )

    group_client: I18nKey = I18nKey(
        default="Client",
        zh_CN="客户端模式",
        zh_TW="用戶端模式",
        en="Client",
        ja="クライアント",
        ru="Клиент",
    )

    group_http: I18nKey = I18nKey(
        default="HTTP",
        zh_CN="HTTP 模式",
        zh_TW="HTTP 模式",
        en="HTTP",
        ja="HTTP モード",
        ru="HTTP",
    )

    group_webhook: I18nKey = I18nKey(
        default="Webhook",
        zh_CN="Webhook 模式",
        zh_TW="Webhook 模式",
        en="Webhook",
        ja="Webhook モード",
        ru="Webhook",
    )
