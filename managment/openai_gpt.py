import os
import time

import openai

from managment import settings
from managment.services import translator


def set_openai_api_key():
    if settings.DEBUG:
        return True

    openai_key = os.environ.get("OPENAI_KEY")
    openai.api_key = openai_key


def translate_chat_gpt(message: str):
    translated = translator.translate(message, dest="ru").text
    return translated
