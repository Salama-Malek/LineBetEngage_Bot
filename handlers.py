from telegram import ReplyKeyboardMarkup
from utils.text_loader import get_texts
from utils.storage import save_user_data
from constants import (
    LANGUAGE,
    MAIN_MENU,
    REGISTRATION_INFO,
    REG_NAME,
    REG_LAST_NAME,
    REG_TELEGRAM,
    REG_EMAIL,
    REG_PHONE,
    REG_COUNTRY,
    REG_PROMO,
)
import re
from telegram.constants import ParseMode
import logging
import os
import json
import requests
from dotenv import load_dotenv
from telegram.helpers import escape_markdown
from constants import SUPPORTED_LANGUAGES

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = "-1002325909184"

# إعداد التسجيل (logging)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


# Utility function to create reply markup with Back and Main Menu buttons
def create_reply_markup(buttons, texts, add_back=False, add_main_menu=True):
    """
    Creates a reply keyboard markup with optional Back and Main Menu buttons.

    Args:
        buttons (list): List of buttons for the current step.
        texts (dict): Dictionary containing button texts.
        add_back (bool): Whether to include the Back button.
        add_main_menu (bool): Whether to include the Main Menu button.

    Returns:
        ReplyKeyboardMarkup: Reply keyboard markup with added navigation buttons.
    """
    # Add Back button if requested
    if add_back:
        buttons.append([texts["button_back"]])

    # Add Main Menu button if requested
    if add_main_menu:
        buttons.append([texts["button_main_menu"]])

    return ReplyKeyboardMarkup(buttons, one_time_keyboard=True, resize_keyboard=True)

# Start command handler
async def start(update, context):
    lang = (
        update.message.from_user.language_code[:2]
        if update.message.from_user.language_code
        else "en"
    )
    context.user_data["language"] = lang if lang in SUPPORTED_LANGUAGES else "en"
    texts = get_texts(context.user_data["language"])

    reply_markup = ReplyKeyboardMarkup(
        texts["languages"], one_time_keyboard=True, resize_keyboard=True
    )
    await update.message.reply_text(texts["welcome"], parse_mode=ParseMode.MARKDOWN)
    await update.message.reply_text(
        texts["language_prompt"], reply_markup=reply_markup
    )
    return LANGUAGE


# Language selection handler
async def choose_language(update, context):
    available_languages = {
        "en": {"language_name": "🇬🇧 English"},
        "fr": {"language_name": "🇫🇷 Français"},
        "ar": {"language_name": "🇦🇪 العربية"},
        "ru": {"language_name": "🇷🇺 Русский"},
        "fa": {"language_name": "🇮🇷 فارسی"},
        "sw": {"language_name": "🇰🇪 Kiswahili"},
        "ha": {"language_name": "🇳🇬 Hausa"},
        "am": {"language_name": "🇪🇹 አማርኛ"},
        "zu": {"language_name": "🇿🇦 isiZulu"},
        "ig": {"language_name": "🇳🇬 Igbo"},
    }
    lang_map = {
        details["language_name"]: code for code, details in available_languages.items()
    }
    selected_language = update.message.text
    lang = lang_map.get(selected_language)

    if not lang:
        lang = "en"

    context.user_data["language"] = lang
    texts = get_texts(lang)

    reply_markup = ReplyKeyboardMarkup(
        texts["menu_buttons"], one_time_keyboard=True, resize_keyboard=True
    )
    await update.message.reply_text(
        texts["main_menu_prompt"], reply_markup=reply_markup
    )
    return MAIN_MENU


# Main menu handler
async def main_menu(update, context):
    lang = context.user_data.get("language", "en")
    texts = get_texts(lang)

    user_choice = update.message.text

    if user_choice == texts["button_register"]:
        return await start_registration(update, context)

    if user_choice == texts["button_commission"]:
        await update.message.reply_text(texts["commission"], parse_mode="Markdown")
        return MAIN_MENU

    if user_choice == texts["button_marketing"]:
        await update.message.reply_text(texts["marketing_tips"], parse_mode="Markdown")
        return MAIN_MENU

    if user_choice == texts["button_faq"]:
        await update.message.reply_text(texts["faq"], parse_mode="Markdown")
        return MAIN_MENU

    if user_choice == texts["button_support"]:
        await update.message.reply_text(texts["support"], parse_mode="Markdown")
        return MAIN_MENU

    if user_choice == texts["button_back"] or user_choice == texts["button_main_menu"]:
        return await start(update, context)

    await update.message.reply_text(
        texts.get("invalid_option", "❌ Invalid option. Please try again."),
        parse_mode="Markdown",
    )
    return MAIN_MENU


# Registration process handlers
async def start_registration(update, context):
    context.user_data["current_step"] = "registration"
    lang = context.user_data.get("language", "en")
    texts = get_texts(lang)

    buttons = [[texts["button_register_manually"], texts["button_register_step"]]]
    reply_markup = create_reply_markup(buttons, texts, add_main_menu=True)

    await update.message.reply_text(
        texts["registration_choice"], reply_markup=reply_markup, parse_mode="Markdown"
    )
    return REGISTRATION_INFO


# Generic function to handle back and main menu buttons in registration steps
async def handle_back_or_main_menu(update, context, current_step):
    lang = context.user_data.get("language", "en")
    texts = get_texts(lang)

    if update.message.text == texts["button_back"]:
        return await start_registration(update, context)

    if update.message.text == texts["button_main_menu"]:
        return await main_menu(update, context)

    return current_step

async def handle_registration_choice(update, context):
    """
    Handles the user's choice between manual or bot-assisted registration.
    """
    user_choice = update.message.text.strip()  # Get the user's choice
    lang = context.user_data.get("language", "en")  # Get the user's selected language
    texts = get_texts(lang)  # Load texts in the selected language

    # Log the user's choice for debugging
    logger.info(f"User {update.message.from_user.id} chose: {user_choice}")

    # Handle "Back" button
    if user_choice == texts.get("button_back"):
        # Go back to the main registration menu
        return await start_registration(update, context)

    # Handle "Main Menu" button
    if user_choice == texts.get("button_main_menu"):
        return await main_menu(update, context)

    # Handle "Register Manually"
    if user_choice == texts.get("button_register_manually"):
        # Send instruction message to the user
        await update.message.reply_text(
            texts.get(
                "manual_register_instruction",
                "🔗 Please send your registration details to activate your account."
            ),
            parse_mode=ParseMode.MARKDOWN
        )

        # Notify the group chat about the manual registration
        try:
            user = update.message.from_user
            username = f"@{user.username}" if user.username else "N/A"
            user_id = user.id

            # Define the fixed group message
            group_message = (
                f"📝 *Manual Registration Selected*:\n"
                f"👤 *User:* `{escape_markdown(username, version=2)}`\n"
                f"🆔 *User ID:* `{user_id}`"
            )

            # Send the group message using Telegram Bot API
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            payload = {
                "chat_id": CHAT_ID,
                "text": group_message,
                "parse_mode": "MarkdownV2"
            }
            response = requests.post(url, data=payload)
            if response.status_code != 200:
                logger.error(f"Failed to send message to group chat: {response.text}")
        except Exception as e:
            logger.error(f"Error sending message to group chat: {e}")

        # Return to the main menu
        return MAIN_MENU

    # Handle "Register Step by Step"
    elif user_choice == texts.get("button_register_step"):
        # Initialize new registration data
        context.user_data["registration"] = {}  # Clear any previous data
        await update.message.reply_text(
            texts["ask_first_name"], parse_mode=ParseMode.MARKDOWN
        )
        return REG_NAME  # Proceed to ask for the first name

    # Handle invalid input
    await update.message.reply_text(
        texts.get("invalid_option", "❌ Please choose a valid option from the menu."),
        reply_markup=ReplyKeyboardMarkup(
            [
                [texts.get("button_register_manually"), texts.get("button_register_step")],
                [texts.get("button_back"), texts.get("button_main_menu")],
            ],
            one_time_keyboard=True,
            resize_keyboard=True,
        ),
        parse_mode=ParseMode.MARKDOWN
    )
    return REGISTRATION_INFO


async def ask_for_first_name(update, context):
    lang = context.user_data.get("language", "en")
    texts = get_texts(lang)

    # Handle Back and Main Menu navigation
    if update.message.text == texts["button_back"]:
        return await start_registration(update, context)
    if update.message.text == texts["button_main_menu"]:
        return await main_menu(update, context)

    # Validate first name
    first_name = update.message.text.strip()
    if not first_name:
        await update.message.reply_text(
            texts.get(
                "error_empty_first_name", "❌ First name cannot be empty. Try again."
            ),
            parse_mode="Markdown",
        )
        return REG_NAME

    # Save the first name
    context.user_data["registration"]["first_name"] = first_name

    # Show the next step with Back and Main Menu buttons
    buttons = []
    reply_markup = create_reply_markup(buttons, texts, add_back=True, add_main_menu=True)

    await update.message.reply_text(
        texts.get("ask_last_name", "📝 Great! Now, your last name?"),
        reply_markup=reply_markup,
        parse_mode="Markdown",
    )
    return REG_LAST_NAME


async def ask_for_last_name(update, context):
    lang = context.user_data.get("language", "en")
    texts = get_texts(lang)

    # Handle Back and Main Menu navigation
    if update.message.text == texts["button_back"]:
        return await ask_for_first_name(update, context)
    if update.message.text == texts["button_main_menu"]:
        return await main_menu(update, context)

    # Validate last name
    last_name = update.message.text.strip()
    if not last_name:
        await update.message.reply_text(
            texts.get("error_empty_last_name", "❌ Last name cannot be empty."),
            parse_mode="Markdown",
        )
        return REG_LAST_NAME

    # Save the last name
    context.user_data["registration"]["last_name"] = last_name

    # Show the next step with Back and Main Menu buttons
    buttons = []
    reply_markup = create_reply_markup(buttons, texts, add_back=True, add_main_menu=True)

    await update.message.reply_text(
        texts.get("ask_telegram_username", "📛 Your Telegram username?"),
        reply_markup=reply_markup,
        parse_mode="Markdown",
    )
    return REG_TELEGRAM


async def ask_for_telegram(update, context):
    current_step = await handle_back_or_main_menu(update, context, REG_TELEGRAM)
    if current_step != REG_TELEGRAM:
        return current_step

    lang = context.user_data.get("language", "en")
    texts = get_texts(lang)

    telegram_username = update.message.text.strip()
    if not telegram_username.startswith("@"):
        await update.message.reply_text(
            texts.get(
                "error_invalid_telegram",
                "❌ Telegram username must start with '@'. Please enter a valid username.",
            ),
            parse_mode="Markdown",
        )
        return REG_TELEGRAM

    context.user_data["registration"]["telegram"] = telegram_username
    buttons = []
    reply_markup = create_reply_markup(buttons, texts)

    await update.message.reply_text(
        texts.get("ask_email", "📧 What is your *email address*?"),
        reply_markup=reply_markup,
        parse_mode="Markdown",
    )
    return REG_EMAIL


# Repeat similar handlers for email, phone, country, and promo code...

# Main Menu Button Handling
async def handle_main_menu(update, context):
    lang = context.user_data.get("language", "en")
    texts = get_texts(lang)

    reply_markup = ReplyKeyboardMarkup(
        texts["menu_buttons"], one_time_keyboard=True, resize_keyboard=True
    )
    await update.message.reply_text(
        texts["main_menu_prompt"], reply_markup=reply_markup
    )
    return MAIN_MENU


async def ask_for_email(update, context):
    current_step = await handle_back_or_main_menu(update, context, REG_EMAIL)
    if current_step != REG_EMAIL:
        return current_step

    lang = context.user_data.get("language", "en")
    texts = get_texts(lang)

    email = update.message.text.strip()
    email_pattern = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    if not re.match(email_pattern, email):
        await update.message.reply_text(
            texts.get(
                "error_invalid_email",
                "❌ Invalid email address. Please provide a valid email.",
            ),
            parse_mode="Markdown",
        )
        return REG_EMAIL

    context.user_data["registration"]["email"] = email
    buttons = []
    reply_markup = create_reply_markup(buttons, texts)

    await update.message.reply_text(
        texts.get("ask_phone_number", "📱 What is your *phone number*?"),
        reply_markup=reply_markup,
        parse_mode="Markdown",
    )
    return REG_PHONE


async def ask_for_phone(update, context):
    current_step = await handle_back_or_main_menu(update, context, REG_PHONE)
    if current_step != REG_PHONE:
        return current_step

    lang = context.user_data.get("language", "en")
    texts = get_texts(lang)

    phone = update.message.text.strip()
    phone_pattern = r"^\+?[0-9]{7,15}$"  # Allow optional '+' for international numbers
    if not re.match(phone_pattern, phone):
        await update.message.reply_text(
            texts.get(
                "error_invalid_phone",
                "❌ Phone number must be numeric and 7-15 digits long. Please enter a valid phone number.",
            ),
            parse_mode="Markdown",
        )
        return REG_PHONE

    context.user_data["registration"]["phone"] = phone
    buttons = []
    reply_markup = create_reply_markup(buttons, texts)

    await update.message.reply_text(
        texts.get("ask_country", "🌍 Which *country* are you in?"),
        reply_markup=reply_markup,
        parse_mode="Markdown",
    )
    return REG_COUNTRY


async def ask_for_country(update, context):
    current_step = await handle_back_or_main_menu(update, context, REG_COUNTRY)
    if current_step != REG_COUNTRY:
        return current_step

    lang = context.user_data.get("language", "en")
    texts = get_texts(lang)

    country = update.message.text.strip()
    if not country.isalpha():
        await update.message.reply_text(
            texts.get(
                "error_invalid_country",
                "❌ Country name must contain only letters. Please enter a valid country.",
            ),
            parse_mode="Markdown",
        )
        return REG_COUNTRY

    context.user_data["registration"]["country"] = country
    buttons = []
    reply_markup = create_reply_markup(buttons, texts)

    await update.message.reply_text(
        texts.get(
            "ask_promo_code",
            "🎫 Finally, what is your preferred *promo code* (e.g., 'Linebet2024')?",
        ),
        reply_markup=reply_markup,
        parse_mode="Markdown",
    )
    return REG_PROMO

async def ask_for_promo_code(update, context):
    """
    Handles the user's input for the promo code.
    Saves the promo code and proceeds to save the registration.
    """
    lang = context.user_data.get("language", "en")
    texts = get_texts(lang)

    # Handle navigation buttons
    if update.message.text == texts["button_back"]:
        return await ask_for_country(update, context)
    if update.message.text == texts["button_main_menu"]:
        return await main_menu(update, context)

    # Save the promo code
    promo_code = update.message.text.strip()
    if len(promo_code) > 20:
        await update.message.reply_text(
            texts.get(
                "error_invalid_promo",
                "❌ Invalid promo code. Please provide a valid promo code (max 20 characters).",
            ),
            parse_mode="Markdown",
        )
        return REG_PROMO  # Stay in the Promo Code step

    # Add promo code to registration data
    context.user_data["registration"]["promo"] = promo_code
    print("Promo Code Saved:", promo_code)  # Debugging log

    # Notify the user of success
    # await update.message.reply_text(
    #     texts.get(
    #         "registration_complete",
    #         "✅ Thank you! Your registration is complete. We'll contact you shortly.",
    #     ),
    #     reply_markup=ReplyKeyboardMarkup(
    #         [[texts["button_main_menu"]]],
    #         one_time_keyboard=True,
    #         resize_keyboard=True,
    #     ),
    #     parse_mode="Markdown",
    # )

    # Proceed to save the registration
    return await save_registration(update, context)

async def save_registration(update, context):
    """
    Finalizes the registration process by saving data and notifying the admin group.
    """
    lang = context.user_data.get("language", "en")
    texts = get_texts(lang)

    # Retrieve registration data
    registration_data = context.user_data.get("registration", {})
    promo_code = registration_data.get("promo", "No Promo Code")  # Default to 'No Promo Code'

    # Collect registration details
    user_id = update.message.from_user.id
    raw_username = update.message.from_user.username
    username = f"@{raw_username}" if raw_username else "N/A"

    # Debugging log
    print("Full Registration Data:", registration_data)

    # Format the message for the group chat
    try:
        from datetime import datetime

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f"""
📝 *New Registration*:
📅 *Time*: `{timestamp}`
👤 *Username*: `{escape_markdown(username, version=2)}`
🧾 *Full Name*: `{escape_markdown(registration_data.get('first_name', '') + ' ' + registration_data.get('last_name', ''), version=2)}`
📛 *Telegram*: `{escape_markdown(registration_data.get('telegram', ''), version=2)}`
📧 *Email*: `{escape_markdown(registration_data.get('email', ''), version=2)}`
📱 *Phone*: `{escape_markdown(registration_data.get('phone', ''), version=2)}`
🌍 *Country*: `{escape_markdown(registration_data.get('country', ''), version=2)}`
🎫 *Promo Code*: `{escape_markdown(promo_code, version=2)}`
        """
        # Send message to group chat
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "MarkdownV2"}
        response = requests.post(url, data=payload)

        if response.status_code != 200:
            print(f"Failed to send message to group chat: {response.text}")
    except Exception as e:
        print(f"Error sending data to group chat: {e}")

    # Save to JSON (if desired)
    try:
        file_path = "user_data.json"
        all_data = []

        if os.path.exists(file_path):
            with open(file_path, "r") as file:
                all_data = json.load(file)

        all_data.append({
            "user_id": user_id,
            "username": username,  # Now includes '@'
            "registration_data": registration_data
        })

        with open(file_path, "w") as file:
            json.dump(all_data, file, indent=4)

    except Exception as e:
        await update.message.reply_text(
            "❌ An error occurred while saving your registration. Please try again later.",
            parse_mode='Markdown'
        )
        return MAIN_MENU

    # Notify the user of successful registration
    await update.message.reply_text(
        texts.get(
            "registration_success",
            "✅ Thank you for registering! Our team will contact you shortly.",
        ),
        parse_mode="Markdown"
    )

    # Return to the main menu
    return MAIN_MENU

async def fallback(update, context):
    lang = context.user_data.get("language", "en")
    texts = get_texts(lang)

    current_step = context.user_data.get("current_step", "main_menu")

    if current_step == "registration":
        await update.message.reply_text(
            texts.get("invalid_option", "❌ Invalid option. Please provide valid input."),
            parse_mode="Markdown",
        )
        return REGISTRATION_INFO

    # Default to the main menu
    await update.message.reply_text(
        texts.get("invalid_option", "❌ Invalid option. Returning to the main menu."),
        reply_markup=ReplyKeyboardMarkup(
            texts["menu_buttons"], one_time_keyboard=True, resize_keyboard=True
        ),
    )
    return MAIN_MENU


async def registration_info(update, context):
    """
    Handles the final step of registration, saves user data, and confirms registration.
    """
    # Get selected language and texts
    lang = context.user_data.get("language", "en")  # Default to English
    texts = get_texts(lang)

    try:
        # Collect the user's registration data
        user_id = update.message.from_user.id
        username = update.message.from_user.username
        user_data = context.user_data.get("registration", {})

        # Save user data
        save_user_data(user_id, {"username": username, "registration_data": user_data})
        logger.info(f"User {user_id} ({username}) registration completed: {user_data}")

        # Notify the user of successful registration
        # await update.message.reply_text(
        #     texts.get(
        #         "after_registration_contact",
        #         "✅ Thank you! Our team will contact you shortly.",
        #     ),
        #     parse_mode="Markdown",
        # )

    except Exception as e:
        # Log the error and notify the user
        logger.error(
            f"Error during registration for user {update.message.from_user.id}: {e}"
        )
        await update.message.reply_text(
            "❌ An error occurred while processing your registration. Please try again later.",
            parse_mode="Markdown",
        )

    # Return to the main menu
    return MAIN_MENU


async def navigate_back(update, context):
    """
    Handles navigation when the Back button is clicked.
    Determines the user's current menu or step and redirects appropriately.
    """
    lang = context.user_data.get("language", "en")
    texts = get_texts(lang)

    # Check where the user is currently
    current_step = context.user_data.get("current_step", "main_menu")

    if current_step == "registration":
        return await start_registration(update, context)
    elif current_step == "main_menu":
        return await main_menu(update, context)
    else:
        # Default fallback to the main menu
        await update.message.reply_text(
            texts.get("main_menu_prompt", "Returning to the main menu."),
            reply_markup=ReplyKeyboardMarkup(
                texts["menu_buttons"], one_time_keyboard=True, resize_keyboard=True
            ),
        )
        return MAIN_MENU
