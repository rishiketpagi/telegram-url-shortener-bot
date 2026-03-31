import os
import requests
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:5000")

if not TOKEN:
    raise ValueError("BOT_TOKEN is not set")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Hello! I am your URL Shortener Bot\n\n"
        "Commands:\n"
        "/short <long_url> - shorten a URL\n"
        "/stats <short_code> - view click stats\n"
        "/help - show help"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📌 Commands:\n"
        "/short https://example.com/some/very/long/url\n"
        "/stats abc123"
    )


async def short(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage:\n/short https://example.com")
        return

    long_url = context.args[0]

    try:
        response = requests.post(
            f"{BACKEND_URL}/shorten",
            json={"long_url": long_url},
            timeout=10
        )

        data = response.json()

        if response.status_code != 200:
            await update.message.reply_text(f"❌ Error: {data.get('error', 'Unknown error')}")
            return

        await update.message.reply_text(
            f"✅ Short URL created!\n\n"
            f"🔗 Original: {data['long_url']}\n"
            f"✂️ Short: {data['short_url']}\n"
            f"🆔 Code: {data['short_code']}"
        )

    except Exception as e:
        await update.message.reply_text(f"❌ Backend error: {str(e)}")


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage:\n/stats abc123")
        return

    short_code = context.args[0]

    try:
        response = requests.get(f"{BACKEND_URL}/stats/{short_code}", timeout=10)
        data = response.json()

        if response.status_code != 200:
            await update.message.reply_text(f"❌ Error: {data.get('error', 'Unknown error')}")
            return

        await update.message.reply_text(
            f"📊 URL Stats\n\n"
            f"🆔 Code: {data['short_code']}\n"
            f"🔗 Original URL: {data['long_url']}\n"
            f"👆 Clicks: {data['clicks']}\n"
            f"🕒 Created: {data['created_at']}"
        )

    except Exception as e:
        await update.message.reply_text(f"❌ Backend error: {str(e)}")


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("short", short))
    app.add_handler(CommandHandler("stats", stats))

    print("🤖 Telegram bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()