import logging

from default import color
import seacher
from sites.china_daily import ChinaDaily
from sites.dziennik_wschodni import DziennikWschodni


def start_with_logger(class_object):
    try:
        class_object.start()
        print(class_object.get_count_sent_posts())
    except:
        print(
            color(
                f"Ошибка при работе с [{class_object.__class__.__name__}]. "
                f"Логи сохранены в файл под названием {class_object.__class__.__name__}.log",
                "red",
                "bold",
            )
        )
        logging.basicConfig(
            level=logging.ERROR,
            filename=f"{class_object.__class__.__name__}.log",
            filemode="w",
            format="%(asctime)s %(levelname)s %(message)s",
        )

        logging.error(
            f"Ошибка при работе с [ChinaDaily]. Keywords: {seacher.global_keywords}",
            exc_info=True,
        )


def start_china_daily(keywords: list, time_interval: int):
    china_daily = ChinaDaily(keywords, time_interval)
    status = china_daily.check_connection()

    if status:
        start_with_logger(china_daily)


def start_dziennik_wschodni(keywords: list, time_interval: int):
    china_daily = DziennikWschodni(keywords, time_interval)
    status = china_daily.check_connection()

    if status:
        start_with_logger(china_daily)
