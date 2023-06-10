import time

import openai

openai.api_key = "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"


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
