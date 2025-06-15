# PNP Television Telegram Bot

This bot manages paid subscriptions for PNP Television channels.

## HTML Text Customization

Administrators can personalize the bot's messages by editing the HTML templates found in the `templates/` directory. Each language has its own folder (`en`, `es`, etc.), and every file corresponds to a message key from `bot/texts.py`.

To change a message:
1. Open (or create) the file `templates/<lang>/<key>.html`.
2. Edit the HTML content and save the file.
3. Restart the bot to load the new text.

When an HTML template is present, it overrides the default text from `bot/texts.py`.

## Broadcast Messages
Admin users can send broadcast messages to specific user groups using the /broadcast command.

Usage:
```
/broadcast <GROUP> <message>
```
where `<GROUP>` is one of `NEVER_PURCHASED`, `ACTIVE_MEMBER`, `CHURNED`, or `ALL`.
Messages can include Markdown formatting and optional photos or videos. Users can unsubscribe from future broadcasts via an inline button.
