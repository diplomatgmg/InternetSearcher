from threading import Thread

import main
from default import color
from default import translator
from start_parsers import (
    start_china_daily,
    start_dziennik_wschodni,
    start_khaleej_times,
    start_lefigaro,
    start_sky_news,
    start_spiegel,
    start_theguardian,
    start_usa_today,
)

# TODO
global_keywords = []


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
            f"Убедитесь, что вводимое число находится в промежутке "
            f"от {color(min_num, 'cyan')} до {color(max_num, 'cyan')}.Введите еще раз:"
        )


def print_hours_message(hours: int) -> None:
    if hours == 1:
        print(f"Выполняется поиск новостей за последний {color('час', 'cyan')}")
    elif hours % 10 == 1 and hours % 100 != 11:
        print(f"Выполняется поиск новостей за последний {color(hours, 'cyan')} час")
    elif hours % 10 in (2, 3, 4) and hours % 100 not in (12, 13, 14):
        print(f"Выполняется поиск новостей за последние {color(hours, 'cyan')} часа")
    else:
        print(f"Выполняется поиск новостей за последние {color(hours, 'cyan')} часов")


def translate_keywords(keywords: list, to_language: str) -> list:
    return [
        translator.translate(word, to_language, "ru").text.lower() for word in keywords
    ]


def search(keywords: list):
    global global_keywords
    global_keywords = keywords
    print(f"Ключевые слова: {color(str(keywords), 'cyan')}")

    min_num = 1
    max_num = 96
    print(
        f"За какое время искать? (в часах). "
        f"От {color(min_num, 'cyan')} до {color(max_num, 'cyan')}. "
        f"Ввести заново ключевые слова - {color('0', 'cyan')}."
    )
    time_interval = get_correct_num(min_num, max_num, blank=True)

    if time_interval == 0:
        return main.main(False, keywords)

    print_hours_message(time_interval)

    en_keywords = translate_keywords(keywords, "en")
    pl_keywords = translate_keywords(keywords, "pl")
    fr_keywords = translate_keywords(keywords, "fr")
    de_keywords = translate_keywords(keywords, "de")

    china_daily_thread = Thread(
        target=start_china_daily, args=(en_keywords, time_interval)
    )
    dziennik_wschodni_thread = Thread(
        target=start_dziennik_wschodni, args=(pl_keywords, time_interval)
    )
    khaleej_times_thread = Thread(
        target=start_khaleej_times, args=(en_keywords, time_interval)
    )
    lefigaro_thread = Thread(target=start_lefigaro, args=(fr_keywords, time_interval))
    sky_news_thread = Thread(target=start_sky_news, args=(en_keywords, time_interval))
    spiegel_thread = Thread(target=start_spiegel, args=(de_keywords, time_interval))
    theguardian_thread = Thread(
        target=start_theguardian, args=(en_keywords, time_interval)
    )
    usa_today_thread = Thread(target=start_usa_today, args=(en_keywords, time_interval))

    china_daily_thread.start()
    dziennik_wschodni_thread.start()
    khaleej_times_thread.start()
    lefigaro_thread.start()
    sky_news_thread.start()
    spiegel_thread.start()
    theguardian_thread.start()
    usa_today_thread.start()
