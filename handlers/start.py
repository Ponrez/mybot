from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes
import logging

logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    logger.info(f"[{update.effective_user.id}] Вызвана команда /start")  
    
    keyboard = [
        [KeyboardButton("Услуги")],
        [KeyboardButton("Оставить заявку")],
    ]
    
    reply_markup = ReplyKeyboardMarkup(
        keyboard, 
        resize_keyboard=True, 
        one_time_keyboard=False
    )
    
    welcome_message = """Привет! Это твой личный ассистент.
Я помогу тебе выбрать услугу и передам заявку нашей команде.

Нажми «Услуги», чтобы посмотреть, что мы предлагаем или выбери действие из меню ниже."""
    
    await update.message.reply_text(
        welcome_message,
        reply_markup=reply_markup
    )
