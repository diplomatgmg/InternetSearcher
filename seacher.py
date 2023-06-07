import logging
from datetime import datetime, timedelta
from threading import Thread

import main
from default import color
from default import translator

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
    result = get_correct_num(min_num, max_num, blank=True)

    if result == 0:
        return main.main(False, keywords)

    print_hours_message(result)

    time_interval = datetime.now() - timedelta(hours=result)

    en_keywords = translate_keywords(keywords, "en")
    # de_keywords = translate_keywords(keywords, "de")
    # fr_keywords = translate_keywords(keywords, "fr")
    # pl_keywords = translate_keywords(keywords, "pl")

    china_daily_thread = Thread(
        target=start_china_daily, args=(en_keywords, time_interval)
    )

    china_daily_thread.start()


def start_china_daily(keywords: list, time_interval: datetime):
    from sites.china_daily import ChinaDaily

    china_daily = ChinaDaily(keywords, time_interval)
    status = china_daily.check_connection()

    if status:
        logger(china_daily)


def logger(class_object):
    try:
        class_object.start()
        print(class_object.get_count_sent_posts())
    except:
        print(color(f"Ошибка при работе с [{class_object.__class__.__name__}]. "
                    f"Логи сохранены в файл под названием {class_object.__class__.__name__}.log", "red", "bold"))
        logging.basicConfig(
            level=logging.ERROR,
            filename=f"{class_object.__class__.__name__}.log",
            filemode="w",
            format="%(asctime)s %(levelname)s %(message)s",
        )

        logging.error(
            f"Ошибка при работе с [ChinaDaily]. Keywords: {global_keywords}",
            exc_info=True,
        )
