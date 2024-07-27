from os import environ
from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN: Final = environ.get("TOKEN", "")
BOT_USERNAME: Final = environ.get("BOT_USERNAME", "")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hola 👋... Bienvenido al descargador de anime gratis subtitulado al español")


if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start_command))

    # Messages

    # Errors

    # Polls the bot
    app.run_polling(poll_interval=3)

