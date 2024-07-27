from os import environ
from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from utils.api_requests import search_animes

TOKEN: Final = environ.get("TOKEN", "")
BOT_USERNAME: Final = environ.get("BOT_USERNAME", "")


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hola 👋... Bienvenido al descargador de anime gratis subtitulado al español")


async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Por favor, introduce el nombre de la serie de anime que deseas buscar.")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    results = search_animes(user_message)

    if results:
        for anime in results:
            caption = f"<b>{anime.title}</b>\n\n{anime.synopsis}"
            await update.message.reply_photo(photo=anime.poster, caption=caption, parse_mode="HTML")
    else:
        await update.message.reply_text("No se encontraron resultados para tu búsqueda.")


if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("search", search_command))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Errors

    # Polls the bot
    app.run_polling(poll_interval=3)
