import logging

import seacher
from default import color
from sites.china_daily import ChinaDaily
from sites.dziennik_wschodni import DziennikWschodni
from sites.khaleejtimes import KhaleejTimes
from sites.lefigaro import Lefigaro
from sites.sky_news import SkyNews
from sites.spiegel import Spiegel


def start_with_logger(class_object):
    try:
        class_object.start()
        print(class_object.get_count_sent_posts())
    except:
        print(
            color(
                f"Ошибка при работе с [{class_object.__class__.__name__}]. "
                f"Логи сохранены в файл под названием errors.log",
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
            f"Ошибка при работе с [{class_object.__class__.__name__}]. Keywords: {seacher.global_keywords}",
            exc_info=True,
        )


def start_china_daily(keywords: list, time_interval: int):
    china_daily = ChinaDaily(keywords, time_interval - 5)
    status = china_daily.check_connection()

    if status:
        start_with_logger(china_daily)


def start_dziennik_wschodni(keywords: list, time_interval: int):
    china_daily = DziennikWschodni(keywords, time_interval + 1)
    status = china_daily.check_connection()

    if status:
        start_with_logger(china_daily)


def start_khaleej_times(keywords: list, time_interval: int):
    khaleej_times = KhaleejTimes(keywords, time_interval)
    status = khaleej_times.check_connection()

    if status:
        start_with_logger(khaleej_times)


def start_lefigaro(keywords: list, time_interval: int):
    lefigaro = Lefigaro(keywords, time_interval + 2)
    status = lefigaro.check_connection()

    if status:
        start_with_logger(lefigaro)


def start_sky_news(keywords: list, time_interval: int):
    sky_news = SkyNews(keywords, time_interval + 2)
    status = sky_news.check_connection()

    if status:
        start_with_logger(sky_news)


def start_spiegel(keywords: list, time_interval: int):
    spiegel = Spiegel(keywords, time_interval + 1)
    status = spiegel.check_connection()

    if status:
        start_with_logger(spiegel)
