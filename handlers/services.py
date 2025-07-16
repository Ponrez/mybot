from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler
from data.services import SERVICES
from config import ADMIN_ID
import re
import logging

logger = logging.getLogger(__name__)

NAME, PHONE, SERVICE = range(3)

async def show_services(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    message = """**Наши услуги:**

**Разработка Telegram-ботов под ключ**
• Автоматизация заявок, рассылок, FAQ, квизов
• Воронки, формы, CRM-интеграции

**Создание Mini Apps (встроенных приложений в Telegram)**
• Интерфейс с кнопками, формами, каталогами
• Подключение к API, базам данных, платёжным системам

**Сопровождение и доработка ботов**
• Поддержка существующих решений
• Рефакторинг, добавление новых функций
• Оптимизация скорости

**Консультации и проектирование**
• Поможем спроектировать логику бота от А до Я под вашу задачу
• Оценим сложность, сроки, подскажем лучшие практики"""
    
    await update.message.reply_text(
        message,
        parse_mode='Markdown'
    )


async def service_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data.startswith("service_"):
        service_id = query.data.replace("service_", "")
        service_info = SERVICES.get(service_id)
        
        if service_info:
            keyboard = [[
                InlineKeyboardButton("Заказать эту услугу", callback_data=f"order_{service_id}")
            ]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            message = f"**{service_info['title']}**\n\n{service_info['description']}"
            
            await query.edit_message_text(
                message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
    
    elif query.data == "order" or query.data.startswith("order_"):
        service_id = query.data.replace("order_", "") if query.data.startswith("order_") else None
        context.user_data['selected_service'] = service_id
        
        await query.edit_message_text("Как вас зовут?")
        return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        name = update.message.text.strip()
        logger.info(f"[{update.effective_user.id}] Ввел имя: {name}")
        
        is_valid, error_message = validate_name(name)

        if not is_valid:
            logger.warning(f"[{update.effective_user.id}] Невалидное имя: {name} — {error_message}")
            await update.message.reply_text(
                f"{error_message}\n\nПопробуйте еще раз:"
            )
            return NAME

        context.user_data['name'] = name
        await update.message.reply_text("Отлично! Теперь введите ваш номер телефона:")
        return PHONE

    except Exception as e:
        logger.exception(f"[{update.effective_user.id}] Ошибка в get_name: {e}")
        await update.message.reply_text("Произошла ошибка при вводе имени.")
        return NAME


async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        phone = update.message.text.strip()
        logger.info(f"[{update.effective_user.id}] Ввел телефон: {phone}")

        is_valid, error_message = validate_phone(phone)

        if not is_valid:
            logger.warning(f"[{update.effective_user.id}] Невалидный телефон: {phone} — {error_message}")
            await update.message.reply_text(
                f"{error_message}\n\nПопробуйте еще раз:"
            )
            return PHONE

        clean_phone = re.sub(r'[\s\-\(\)]', '', phone)
        if clean_phone.startswith('8'):
            clean_phone = '+7' + clean_phone[1:]
        elif clean_phone.startswith('7'):
            clean_phone = '+' + clean_phone

        context.user_data['phone'] = clean_phone

        logger.info(f"[{update.effective_user.id}] Телефон нормализован: {clean_phone}")

        keyboard = []
        for service_id, service_info in SERVICES.items():
            keyboard.append([
                InlineKeyboardButton(service_info["title"], callback_data=f"final_service_{service_id}")
            ])

        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "Выберите интересующую услугу:",
            reply_markup=reply_markup
        )
        return SERVICE

    except Exception as e:
        logger.exception(f"[{update.effective_user.id}] Ошибка в get_phone: {e}")
        await update.message.reply_text("Произошла ошибка при вводе телефона.")
        return PHONE



async def get_service(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        await query.answer()

        service_id = query.data.replace("final_service_", "")
        context.user_data['selected_service'] = service_id

        logger.info(f"[{update.effective_user.id}] Выбрал услугу: {service_id}")
        return await send_order(update, context)
    
    except Exception as e:
        logger.exception(f"[{update.effective_user.id}] Ошибка в get_service: {e}")
        await update.callback_query.edit_message_text("Произошла ошибка при выборе услуги.")
        return ConversationHandler.END

async def send_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        name = context.user_data.get('name')
        phone = context.user_data.get('phone')
        service_id = context.user_data.get('selected_service')
        service_name = SERVICES.get(service_id, {}).get('title', 'Не указана')

        logger.info(f"[{update.effective_user.id}] Отправка заявки: имя={name}, телефон={phone}, услуга={service_name}")

        admin_message = f""" **Новая заявка!**

**Имя:** {name}
**Телефон:** {phone}
**Услуга:** {service_name}

**ID пользователя:** {update.effective_user.id}"""

        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=admin_message,
            parse_mode='Markdown'
        )

        user_message = f""" **Заявка принята!**

Спасибо, {name}! Ваша заявка передана нашей команде.
Мы свяжемся с вами в ближайшее время по номеру {phone}.

**Выбранная услуга:** {service_name}"""

        if hasattr(update, 'callback_query') and update.callback_query:
            await update.callback_query.edit_message_text(user_message, parse_mode='Markdown')
        else:
            await update.message.reply_text(user_message, parse_mode='Markdown')

        logger.info(f"[{update.effective_user.id}] Заявка успешно отправлена")
        context.user_data.clear()
        return ConversationHandler.END

    except Exception as e:
        logger.exception(f"[{update.effective_user.id}] Ошибка при отправке заявки: {e}")
        await update.message.reply_text("Произошла ошибка при отправке заявки. Попробуйте снова.")
        return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отмена оформления заявки"""
    await update.message.reply_text("Оформление заявки отменено.")
    context.user_data.clear()
    return ConversationHandler.END


import re

def validate_name(name):
    if not name or len(name) < 3:
        return False, "Имя должно содержать минимум 3 символа"
    
    if len(name) > 15:
        return False, "Имя слишком длинное (максимум 15 символов)"
    
    if not re.match(r'^[а-яёА-ЯЁ\s\-]+$', name):
        return False, "Имя должно содержать только русские буквы, пробелы и дефисы"
    
    if re.search(r'(.)\1{2,}', name):
        return False, "Имя не может содержать более 2 одинаковых букв подряд"
    
    unique_chars = set(name.lower().replace(' ', '').replace('-', ''))
    if len(unique_chars) == 1:
        return False, "Имя не может состоять из одинаковых букв"
    
    if len(name) >= 4:
        half_len = len(name) // 2
        if name[:half_len] == name[half_len:half_len*2]:
            return False, "Имя выглядит как повторяющийся шаблон"
    
    if len(name) >= 3 and len(unique_chars) < 2:
        return False, "Имя должно содержать минимум 2 разные буквы"
    
    keyboard_patterns = [
        'йцукен', 'фыва', 'ячсм', 'абвг', 'тест', 'йцу'
    ]
    
    name_lower = name.lower().replace(' ', '').replace('-', '')
    for pattern in keyboard_patterns:
        if pattern in name_lower:
            return False, "Имя выглядит подозрительно, введите настоящее имя"
    
    if name.count(' ') > 2:
        return False, "Слишком много пробелов в имени"
    
    if name != name.strip():
        return False, "Уберите лишние пробелы в начале и конце"
    
    return True, "OK"

def validate_phone(phone):
    clean_phone = re.sub(r'[\s\-\(\)]', '', phone)
    
    patterns = [
        r'^\+7\d{10}$',        # +79991234567
        r'^8\d{10}$',          # 89991234567
        r'^7\d{10}$',          # 79991234567
    ]
    
    if not any(re.match(pattern, clean_phone) for pattern in patterns):
        return False, "Неверный формат телефона. Используйте: +79991234567 или 89991234567"
    
    return True, "OK"
