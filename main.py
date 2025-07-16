import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ConversationHandler
from config import BOT_TOKEN
from handlers.start import start_command
from handlers.services import (
    show_services, service_callback, get_name, 
    get_phone, get_service, send_order, cancel,
    NAME, PHONE, SERVICE
)


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)



async def start_order(update, context):
    context.user_data['selected_service'] = None
    await update.message.reply_text("Как вас зовут?")
    return NAME

def main():
    
    app = Application.builder().token(BOT_TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(service_callback, pattern="^order"),
            MessageHandler(filters.Regex("^Оставить заявку$"), start_order),
        ],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            SERVICE: [CallbackQueryHandler(get_service, pattern="^final_service_")],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.Regex("^Услуги$"), show_services))
    app.add_handler(CallbackQueryHandler(service_callback, pattern="^service_"))
    app.add_handler(conv_handler)
    
    print("Бот запущен...")
    app.run_polling()

if __name__ == '__main__':
    main()
