import os
import time

import openai

from managment import settings
from managment.services import translator


def get_openai_api_key():
    if settings.DEBUG:
        return True

    openai_key = os.environ.get("OPENAI_KEY")
    return openai_key


openai.api_key = get_openai_api_key()


def translate_chat_gpt(message: str):
    while True:
        try:
            start_message = "Переведи этот текст на русский язык максимально понятно: "
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "user",
                        "content": start_message + message,
                    }
                ],
            )
            translated = completion.choices[0].message.content
            return translated
        except openai.error.RateLimitError:
            time.sleep(30)
        except openai.error.AuthenticationError:
            print(
                "Ошибка при получении токена для ChatGPT. "
                "Дальнейшая работа программы невозможна. "
                "Возможно, вы указали неверный токен."
                "Обратитесь к программисту."
            )
            raise openai.error.AuthenticationError
        except openai.error.APIConnectionError:
            translated = translator.translate(message, dest="ru").text
            return translated
