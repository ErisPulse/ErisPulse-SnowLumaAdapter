[//]: # (Объявление об архивации)
> **[Объявление] Проект временно архивирован**
>
> По независящим обстоятельствам вышестоящий проект SnowLuma стал закрытым. В знак уважения к проекту SnowLuma и его автору, а также к сообществу открытого кода, **ErisPulse-SnowLumaAdapter временно архивируется с сегодняшнего дня**.
>
> - Опубликованные версии по-прежнему доступны на PyPI, существующие установки не затронуты
> - На время архивации проект не принимает новые запросы на функции и сообщения о проблемах
> - Уважение — автору SnowLuma, благодарность — сообществу за поддержку

[English](README.en.md) | 简体中文 | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md) | [Русский](README.ru.md)

<div align="center">

<img src="https://raw.githubusercontent.com/ErisPulse/ErisPulse/main/.github/assets/ErisPulseLogo.png" width="180" alt="ErisPulse-SnowLumaAdapter" />

# ErisPulse-SnowLumaAdapter

**Адаптер ErisPulse SnowLuma — NTQQ hook, пересылка, совместимость с NapCat**

<p>
  <a href="https://pypi.org/project/ErisPulse-SnowLumaAdapter/"><img src="https://img.shields.io/pypi/v/ErisPulse-SnowLumaAdapter?style=for-the-badge&logo=pypi&logoColor=white" alt="PyPI"></a>
  <a href="https://pypi.org/project/ErisPulse-SnowLumaAdapter/"><img src="https://img.shields.io/badge/Python-3.10+-FFD43B?style=for-the-badge&logo=python&logoColor=blue" alt="Python"></a>
  <a href="https://github.com/ErisPulse/ErisPulse/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue?style=for-the-badge" alt="License"></a>
  <img src="https://raw.githubusercontent.com/ErisPulse/.github/main/assets/badges/adapter.svg" alt="ErisPulse">
</p>

</div>

---

## Features

- **Full OneBot v11 protocol** — OB12-standard ApiDSL auto-maps action names (`get_self_info` → `get_login_info`, etc.)
- **Merge-forward** — `MergeForward` with three-level fallback (dedicated endpoint → `upload_forward_msg` resid → plain node segments); `Raw_ob12` auto-routes
- **NapCat compatible** — point `url` at a NapCat forward WS and it just works; or receive NapCat reverse WS in server mode
- **60+ typed extension methods** (IDE completion) — poke / Qzone / group files / group albums / message history / essence / read state / OCR and more
- **109 extension actions** all callable via `Api.call("action_name", ...)` (works with NapCat / SnowLuma)
- **Multi-account + auto bot_id** — no QQ number config needed; `event.reply()` routes to the source account
- **5-language i18n** (zh-CN / zh-TW / en / ja / ru)

## Install

```bash
epsdk install SnowLumaAdapter
```

## Links

- [ErisPulse main repo](https://github.com/ErisPulse/ErisPulse)
- [Module development guide](https://www.erisdev.com/#docs/developer-guide/README.md)

> The full documentation (configuration tables, event mappings, API reference) is in Chinese: switch to **简体中文** above.

## License

MIT
