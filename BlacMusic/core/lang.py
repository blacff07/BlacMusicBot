# ==============================================================================
# lang.py - Multi-Language Support System
# ==============================================================================
# This file manages translations for the bot in multiple languages.
# - Translation files are stored in BlacMusic/locales/ as JSON files (en.json, si.json)
# - Each chat can have its own language preference stored in the database
# - The @language() decorator automatically injects translations into message handlers
# ==============================================================================

import json
from functools import wraps
from pathlib import Path

from BlacMusic import db, logger

# Supported language codes and their display names
lang_codes = {
    "en": "English",  # English language
}


class Language:
    """
    Language class for managing multilingual support using JSON language files.
    """

    def __init__(self):
        """Initialize the language system and load all translation files."""
        self.lang_codes = lang_codes
        # Directory containing translation files. Resolved relative to this
        # file (BlacMusic/core/lang.py -> BlacMusic/locales) rather than the
        # process's current working directory, so it keeps working no
        # matter where the bot is launched from.
        self.lang_dir = Path(__file__).resolve().parent.parent / "locales"
        self.languages = self.load_files()  # Load all language files into memory

    def load_files(self):
        """Load all language JSON files from the locales directory."""
        languages = {}
        for lang_code in self.lang_codes.keys():
            lang_file = self.lang_dir / \
                f"{lang_code}.json"  # Path to language file
            if lang_file.exists():
                with open(lang_file, "r", encoding="utf-8") as file:
                    languages[lang_code] = json.load(
                        file)  # Load translations into dict
        logger.info(f"🌐 Loaded languages: {', '.join(languages.keys())}")
        return languages

    async def get_lang(self, chat_id: int) -> dict:
        """Get the translation dictionary for a specific chat."""
        return self.languages["en"]  # Return the translation dictionary

    def language(self):
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                fallen = next(
                    (
                        arg
                        for arg in args
                        if hasattr(arg, "chat") or hasattr(arg, "message")
                    ),
                    None,
                )

                chat = None
                if fallen is not None:
                    if hasattr(fallen, "chat"):
                        chat = fallen.chat
                    elif hasattr(fallen, "message"):
                        chat = fallen.message.chat

                if chat is None:
                    # No handler arg exposed a chat (unexpected handler
                    # signature) - fail safe rather than crashing with an
                    # UnboundLocalError on the old code path.
                    logger.warning(
                        f"@language() could not resolve a chat for {func.__name__}; "
                        "skipping blacklist check and language injection."
                    )
                    return await func(*args, **kwargs)

                if chat.id in db.blacklisted:
                    return await chat.leave()

                lang_code = "en"
                lang_dict = self.languages[lang_code]

                setattr(fallen, "lang", lang_dict)
                return await func(*args, **kwargs)

            return wrapper

        return decorator