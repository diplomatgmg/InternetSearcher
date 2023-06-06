from googletrans import Translator

import main


def get_correct_num(min_num: int, max_num: int, blank=False) -> int | str:
    while True:
        result = input().strip()

        if blank and result == "":
            return min_num

        if result.isdigit():
            result = int(result)

            if result == 0:
                return result

            if min_num <= result <= max_num:
                return result
        print(
            f"Убедитесь, что вводимое число находится в промежутке от {min_num} до {max_num}. Введите еще раз:"
        )


def print_hours_message(hours: int) -> None:
    if hours == 1:
        print(f"Выполняется поиск новостей за последний час")
    elif hours % 10 == 1 and hours % 100 != 11:
        print(f"Выполняется поиск новостей за последний {hours} час")
    elif hours % 10 in (2, 3, 4) and hours % 100 not in (12, 13, 14):
        print(f"Выполняется поиск новостей за последние {hours} часа")
    else:
        print(f"Выполняется поиск новостей за последние {hours} часов")


def translate_keywords(keywords: list, language: str) -> list:
    tr = Translator()

    result = []

    for word in keywords:
        result.append(tr.translate(word, language).lower())

    return result


def search(keywords: list):
    print(f"Ключевые слова: {keywords}")

    min_num = 1
    max_num = 96
    print(
        f"За какое время искать? (в часах). От {min_num} до {max_num}. Ввести заново ключевые слова - 0."
    )
    result = get_correct_num(min_num, max_num, blank=True)

    if result == 0:
        return main.main(False, keywords)

    print_hours_message(result)

    en_keywords = translate_keywords(keywords, "en")
    print(en_keywords)
