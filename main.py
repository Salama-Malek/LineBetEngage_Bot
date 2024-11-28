import os
from telegram.ext import ApplicationBuilder, ConversationHandler, CommandHandler, MessageHandler, filters
from dotenv import load_dotenv
from handlers import (
    start, choose_language, main_menu, registration_info, handle_registration_choice, ask_for_first_name,
    ask_for_last_name, ask_for_telegram, ask_for_email, ask_for_phone, ask_for_country, save_registration, fallback
)
from scheduler import schedule_weekly_summary
from constants import LANGUAGE, MAIN_MENU, REGISTRATION_INFO, REG_NAME, REG_LAST_NAME, REG_TELEGRAM, REG_EMAIL, REG_PHONE, REG_COUNTRY, REG_PROMO

# Load environment variables
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

if not TOKEN:
    raise ValueError("TELEGRAM_TOKEN is not set. Please check your .env file.")

def main():
    # Build the Telegram bot application
    app = ApplicationBuilder().token(TOKEN).build()

    # Schedule weekly summary
    schedule_weekly_summary(app.bot)

    # Define the conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            LANGUAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_language)],
            MAIN_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu)],
            REGISTRATION_INFO: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_registration_choice)],
            REG_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_for_first_name)],
            REG_LAST_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_for_last_name)],
            REG_TELEGRAM: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_for_telegram)],
            REG_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_for_email)],
            REG_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_for_phone)],
            REG_COUNTRY: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_for_country)],
            REG_PROMO: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_registration)],
        },
        fallbacks=[CommandHandler('cancel', start)] 
    )


    # Add handlers to the bot
    app.add_handler(conv_handler)

    # Start the bot
    app.run_polling()

if __name__ == "__main__":
    main()
