# Amazon Affiliate Telegram Bot

## Features
- /start
- /stats
- /set_tag yourtag-21
- /autopost on|off
- /set_channel @channelusername or channel_id
- /help
- Converts Amazon links to affiliate links
- Sends clean hyperlinked messages
- Attempts to fetch first product image
- Auto-posts converted product message to channel

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
python bot.py
```

Add your bot token in `.env`.

For auto-posting, add the bot as admin in your Telegram channel.

Note: For production, use Amazon Product Advertising API for reliable title/image data.
