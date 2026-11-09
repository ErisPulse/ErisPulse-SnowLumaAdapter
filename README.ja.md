[//]: # (アーカイブのお知らせ)
> **[お知らせ] 本プロジェクトは一時的にアーカイブされました**
>
> やむを得ない事情により、SnowLuma 上流プロジェクトは非公開となりました。SnowLuma プロジェクトとその開発者への敬意、そしてオープンソースコミュニティへの感謝を込めて、**ErisPulse-SnowLumaAdapter は本日より一時的にアーカイブされます**。
>
> - 公開済みのリリースは PyPI から引き続き入手可能で、既存環境への影響はありません
> - アーカイブ期間中は、新たな機能リクエストや Issue の受け付けを停止します
> - SnowLuma の作者に敬意を、コミュニティの皆さまに感謝を

[English](README.en.md) | 简体中文 | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md) | [Русский](README.ru.md)

<div align="center">

<img src="https://raw.githubusercontent.com/ErisPulse/ErisPulse/main/.github/assets/ErisPulseLogo.png" width="180" alt="ErisPulse-SnowLumaAdapter" />

# ErisPulse-SnowLumaAdapter

**ErisPulse SnowLuma アダプター — NTQQ フック、ネイティブ転送、NapCat 互換**

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
