import logging
from threading import Thread

import main
import sites

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
            f"от {min_num} до {max_num}.Введите еще раз:"
        )


def print_hours_message(hours: int) -> None:
    if hours == 1:
        print(f"\nВыполняется поиск новостей за последний {'час'}")
    elif hours % 10 == 1 and hours % 100 != 11:
        print(f"\nВыполняется поиск новостей за последний {hours} час")
    elif hours % 10 in (2, 3, 4) and hours % 100 not in (12, 13, 14):
        print(f"\nВыполняется поиск новостей за последние {hours} часа")
    else:
        print(f"\nВыполняется поиск новостей за последние {hours} часов")


def search(keywords: list):
    global global_keywords
    global_keywords = keywords
    print(f"\nКлючевые слова: {str(keywords)}")

    min_num = 1
    max_num = 96
    print(
        f"За какое время искать? (в часах). "
        f"От {min_num} до {max_num}. "
        f"Ввести заново ключевые слова - 0."
    )
    time_interval = get_correct_num(min_num, max_num, blank=True)

    if time_interval == 0:
        return main.main(False, keywords)

    print_hours_message(time_interval)

    threads = []
    for parser_class in sites.all_sites.SITES:
        site_thread = Thread(
            target=start_with_logger, args=(parser_class, keywords, time_interval)
        )
        site_thread.start()
        threads.append(site_thread)

    for thread in threads:
        thread.join()

    input("\nПоиск новостей окончен.")


def start_with_logger(parser_class, keywords: list, time_interval: int):
    try:
        parser_class(keywords, time_interval).start()
    except:
        print(
            f"Ошибка при работе с [{parser_class.__class__.__name__}]. "
            f"Логи сохранены в файл под названием errors.log",
        )
        logging.basicConfig(
            level=logging.ERROR,
            filename=f"errors.log",
            filemode="w",
            format="%(asctime)s %(levelname)s %(message)s",
        )

        logging.error(
            f"Ошибка при работе с [{parser_class.__class__.__name__}]. Keywords: {global_keywords}",
            exc_info=True,
        )
