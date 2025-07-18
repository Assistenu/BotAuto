# main.py - tozalangan va xatoliklar tuzatilgan versiya

import os
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (ApplicationBuilder, CallbackQueryHandler, CommandHandler, ContextTypes,
                          ConversationHandler, MessageHandler, filters)
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
bot_token = os.getenv("BOT_TOKEN")

user_data = {}

ADD_ACCOUNT, UPLOAD_SESSION = range(2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("\ud83d\udcc2 .session fayl yuborish", callback_data="upload_session")],
        [InlineKeyboardButton("\ud83d\udcf1 Telefon raqam orqali qo\u2018shish", callback_data="add_account")],
        [InlineKeyboardButton("\uD83E\uDD16 Bot qo\u2018shish", callback_data="add_bot")],
        [InlineKeyboardButton("\u25B6\ufe0f Start Clicker", callback_data="start_click")],
        [InlineKeyboardButton("\ud83d\udd1d Stop Clicker", callback_data="stop_click")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("\uD83D\uDC4B Salom! Nima qilmoqchisiz?", reply_markup=reply_markup)
    return ConversationHandler.END

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "upload_session":
        await query.edit_message_text("\ud83d\udccb Iltimos, .session faylni yuboring:")
        return UPLOAD_SESSION
    elif query.data == "add_account":
        await query.edit_message_text("\u2709\ufe0f Telefon raqamingizni yuboring:")
        return ADD_ACCOUNT
    else:
        await query.edit_message_text("\u274c Bu funksional hali yozilmagan.")
        return ConversationHandler.END

async def handle_uploaded_session(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    os.makedirs("sessions", exist_ok=True)

    document = update.message.document
    if not document.file_name.endswith(".session"):
        await update.message.reply_text("❌ Bu .session fayl emas!")
        return ConversationHandler.END

    file_path = f"sessions/{user_id}_{document.file_name}"
    file = await document.get_file()
    await file.download_to_drive(file_path)

    try:
        client = TelegramClient(file_path, api_id, api_hash)
        await client.connect()
        if not await client.is_user_authorized():
            await update.message.reply_text("❌ Session yaroqsiz. Avtorizatsiyadan o'ting.")
            await client.disconnect()
            return ConversationHandler.END
        if user_id not in user_data:
            user_data[user_id] = {"accounts": []}
        user_data[user_id]['accounts'].append(client)
        await update.message.reply_text("✅ Session muvaffaqiyatli yuklandi!")
    except Exception as e:
        await update.message.reply_text(f"❌ Xatolik: {e}")
        return ConversationHandler.END

    return ConversationHandler.END

def main():
    app = ApplicationBuilder().token(bot_token).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            UPLOAD_SESSION: [MessageHandler(filters.Document.MimeType("application/octet-stream"), handle_uploaded_session)],
        },
        fallbacks=[]
    )

    app.add_handler(conv_handler)
    app.add_handler(CallbackQueryHandler(button_handler))

    app.run_polling()

if __name__ == '__main__':
    main()
