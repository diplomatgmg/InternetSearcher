import time

import openai


def get_openai_api_key():
    try:
        with open("openai_key", "r") as openai_key:
            return openai_key.read()
    except FileNotFoundError:
        with open("openai_key", "w"):
            pass


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
            raise openai.error.AuthenticationError(
                "Ошибка при получении токена для ChatGPT. "
                "Дальнейшая работа программы невозможна. "
                "Обратитесь к программисту."
            )
