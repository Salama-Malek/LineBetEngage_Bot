from importlib import import_module
from constants import DEFAULT_LANGUAGE

# def get_texts(language_code):
#     """
#     Dynamically loads the text content for the given language.
#     Falls back to the default language if the specified language is unavailable.

#     Args:
#         language_code (str): The language code (e.g., 'en', 'ar', 'fr').

#     Returns:
#         dict: The text content for the specified language.
#     """
#     try:
#         module = import_module(f'languages.{language_code}')
#         return module.texts
#     except ImportError:
#         # Fallback to default language if the requested language file is missing
#         module = import_module(f'languages.{DEFAULT_LANGUAGE}')
        # return module.texts
def get_texts(language_code):
    try:
        module = import_module(f'languages.{language_code}')
        texts = module.texts
    except ImportError:
        module = import_module('languages.en')
        texts = module.texts

    # Fallback for missing keys
    def safe_get(key, fallback="Text not available"):
        return texts.get(key, fallback)

    return {key: safe_get(key) for key in texts}

