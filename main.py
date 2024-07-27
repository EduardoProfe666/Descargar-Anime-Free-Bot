from os import environ
from typing import Final
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatMember
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

from utils.api_requests import search_animes, get_anime_episodes, get_link

TOKEN: Final = environ.get("TOKEN", "")

BOT_USERNAME: Final = environ.get("BOT_USERNAME", "")



async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hola 👋... Bienvenido al descargador de anime gratis subtitulado al español... Empieza a buscar tus animes favoritos... Pon el comando /search para mayor información")


async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Por favor, introduce el nombre de la serie de anime que deseas buscar. Luego selecciona el anime que quieras, para luego seleccionar el/los episodio/s a descargar desde el servidor que quieras")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    search_message = await update.message.reply_text("Buscando...")

    results = search_animes(user_message)

    if results:
        keyboard = [[InlineKeyboardButton(anime.title, callback_data=f"anime_{anime.id}")] for anime in results]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await search_message.edit_text("Selecciona un anime:", reply_markup=reply_markup)
    else:
        await search_message.edit_text("No se encontraron resultados para tu búsqueda.")


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    search_message = await query.message.reply_text("Buscando...")

    if data.startswith("anime_"):
        anime_id = data.split("_")[1]
        try:
            episodes = get_anime_episodes(anime_id)
        except Exception as e:
            await search_message.edit_text(text=f"Error al obtener los episodios: {e}")
            return

        if episodes:
            chunk_size = 50  # Because of Telegram limit for inline keyboard buttons
            for i in range(0, len(episodes), chunk_size):
                chunk = episodes[i:i + chunk_size]
                keyboard = [
                    [InlineKeyboardButton(f"Episodio {episode.id}", callback_data=f"episode_{anime_id}_{episode.id}")]
                    for
                    episode in chunk]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.message.reply_text(text=f"Selecciona un episodio: Página {int(i / 50 + 1)}",
                                               reply_markup=reply_markup)
            await search_message.edit_text(text="Episodios enviados. Revisa los mensajes anteriores.")
        else:
            await search_message.edit_text(text="No se encontraron episodios para este anime.")
    elif data.startswith("episode_"):
        anime_id, episode_id = data.split("_")[1:]
        try:
            download_links = get_link(episode_id, anime_id)
        except Exception as e:
            await search_message.edit_text(text=f"Error al obtener los enlaces de descarga: {e}")
            return

        if download_links:
            keyboard = [[InlineKeyboardButton(f"{link.server}", url=link.url)] for link in download_links]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await search_message.edit_text(text=f"Selecciona un servidor para descargar el episodio {episode_id}:",
                                           reply_markup=reply_markup)
        else:
            await search_message.edit_text(text="No se encontraron enlaces de descarga para este episodio.")


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message to the user indicating there was an error."""
    await update.effective_message.reply_text("Hubo un error con su petición, inténtelo más tarde.")


async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Clear all messages and restart the chat."""
    chat_id = update.effective_chat.id
    bot = context.bot

    # Check if the bot has permission to delete messages
    chat_member = await bot.get_chat_member(chat_id, bot.id)
    if chat_member.status not in [ChatMember.ADMINISTRATOR, ChatMember.CREATOR] or not chat_member.can_delete_messages:
        await update.message.reply_text(
            "El bot no tiene permisos para borrar mensajes. Por favor, otorgue los permisos necesarios y vuelva a intentarlo.")
        return

    messages = context.chat_data.get('messages', [])
    for message_id in messages:
        try:
            await bot.delete_message(chat_id=chat_id, message_id=message_id)
        except Exception as e:
            print(f"Could not delete message {message_id}: {e}")
    context.chat_data.clear()
    await update.message.reply_text("Chat reiniciado.")


if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("search", search_command))
    app.add_handler(CommandHandler("clear", clear_command))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Callbacks
    app.add_handler(CallbackQueryHandler(button))

    # Errors
    app.add_error_handler(error_handler)

    # Polls the bot
    app.run_polling(poll_interval=3)