from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

from config import BOT_TOKEN
from db import init_db, create_user, set_tag, set_autopost, set_channel, get_user
from amazon import find_amazon_links, convert_link, get_product_info


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    create_user(user_id)
    await update.message.reply_text(
        "👋 Welcome to Amazon Link Shortener Bot!\n\n"
        "🔹 Send any Amazon link and I will convert it with your affiliate tag.\n"
        "🔹 Your current tag: Not set\n"
        "🔹 Your auto-posting status: Disabled ❌\n"
        "🔹 Your linked channel: Not set\n\n"
        "💡 To set your Amazon affiliate tag, use:\n/set_tag yourtag-21\n\n"
        "📢 To enable auto-posting, use:\n/autopost on\n"
        "📌 Then set your channel with:\n/set_channel @yourchannel\n\n"
        "📌 Send me any Amazon link, and I’ll convert it for you!"
    )


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    create_user(user_id)
    tag, autopost_status, channel = get_user(user_id)
    await update.message.reply_text(
        f"📊 Your Stats\n\n"
        f"Affiliate tag: {tag or 'Not set'}\n"
        f"Auto-posting: {'Enabled ✅' if autopost_status else 'Disabled ❌'}\n"
        f"Linked channel: {channel or 'Not set'}"
    )


async def set_tag_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    create_user(user_id)
    if not context.args:
        await update.message.reply_text("Usage: /set_tag yourtag-21")
        return
    tag = context.args[0]
    set_tag(user_id, tag)
    await update.message.reply_text(f"✅ Affiliate tag set: {tag}")


async def autopost(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    create_user(user_id)
    if not context.args or context.args[0].lower() not in ["on", "off"]:
        await update.message.reply_text("Usage: /autopost on or /autopost off")
        return
    enabled = context.args[0].lower() == "on"
    set_autopost(user_id, enabled)
    if enabled:
        await update.message.reply_text("✅ Auto-posting enabled! Now set your channel using /set_channel <channel_id>.")
    else:
        await update.message.reply_text("❌ Auto-posting disabled.")


async def set_channel_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    create_user(user_id)
    if not context.args:
        await update.message.reply_text("Usage: /set_channel @yourchannel")
        return
    channel = context.args[0]
    set_channel(user_id, channel)
    await update.message.reply_text(f"✅ Channel set: {channel}")


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/start - Register bot\n"
        "/stats - View your details\n"
        "/set_tag yourtag-21 - Set Amazon affiliate tag\n"
        "/autopost on - Enable auto-post\n"
        "/autopost off - Disable auto-post\n"
        "/set_channel @channel - Set auto-post channel\n"
        "/help - Show help"
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    create_user(user_id)

    message = update.effective_message
    text = message.text or message.caption or ""
    links = find_amazon_links(text)
    if not links:
        return

    tag, autopost_status, channel_id = get_user(user_id)
    if not tag:
        await message.reply_text("⚠️ Please set your affiliate tag first:\n/set_tag yourtag-21")
        return

    original_link = links[0]
    affiliate_link = convert_link(original_link, tag)
    title, image_url = get_product_info(original_link)

    caption = f'<b>{title}</b>\n\n<a href="{affiliate_link}">🛒 Buy on Amazon</a>'

    if image_url:
        await message.reply_photo(photo=image_url, caption=caption, parse_mode="HTML")
    else:
        await message.reply_text(caption, parse_mode="HTML", disable_web_page_preview=False)

    if autopost_status and channel_id:
        try:
            if image_url:
                await context.bot.send_photo(chat_id=channel_id, photo=image_url, caption=caption, parse_mode="HTML")
            else:
                await context.bot.send_message(chat_id=channel_id, text=caption, parse_mode="HTML")
        except Exception as e:
            await message.reply_text(f"⚠️ Auto-post failed. Make sure bot is admin in channel.\nError: {e}")
 def main():
    init_db()

    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN is missing")
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("set_tag", set_tag_cmd))
    app.add_handler(CommandHandler("autopost", autopost))
    app.add_handler(CommandHandler("set_channel", set_channel_cmd))
    app.add_handler(CommandHandler("help", help_cmd))

    app.add_handler(MessageHandler(filters.TEXT | filters.Caption, handle_message))

    print("Bot running...")
    app.run_polling()


if __name__ == "__main__":
    main()
