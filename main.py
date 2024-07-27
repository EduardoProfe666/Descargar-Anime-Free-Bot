from os import environ
from typing import Final
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

from utils.api_requests import search_animes, get_anime_episodes, get_link

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
        keyboard = [[InlineKeyboardButton(anime.title, callback_data=f"anime_{anime.id}")] for anime in results]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Selecciona un anime:", reply_markup=reply_markup)
    else:
        await update.message.reply_text("No se encontraron resultados para tu búsqueda.")


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    if data.startswith("anime_"):
        anime_id = data.split("_")[1]
        episodes = get_anime_episodes(anime_id)

        if episodes:
            keyboard = [
                [InlineKeyboardButton(f"Episodio {episode.id}", callback_data=f"episode_{anime_id}_{episode.id}")] for
                episode in episodes]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(text="Selecciona un episodio:", reply_markup=reply_markup)
        else:
            await query.edit_message_text(text="No se encontraron episodios para este anime.")
    elif data.startswith("episode_"):
        anime_id, episode_id = data.split("_")[1:]
        video_path = get_link(episode_id, anime_id)

        if video_path:
            await query.message.reply_video(video=InputFile(video_path))
        else:
            await query.edit_message_text(text="No se encontró un video para este episodio.")


if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("search", search_command))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Callbacks
    app.add_handler(CallbackQueryHandler(button))

    # Errors

    # Polls the bot
    app.run_polling(poll_interval=3)
