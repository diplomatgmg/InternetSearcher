from abc import ABC
from datetime import datetime, timedelta
from http import HTTPStatus

import requests

from default import bad_request_message, good_request_message, color


class BaseParser(ABC):
    SITE_URL = None

    def __init__(
        self, keywords: list | bool = False, time_interval: int | bool = False
    ) -> None:
        self.keywords = keywords
        self.time_interval = datetime.now() - timedelta(hours=time_interval)

        self.categories_hrefs = set()
        self.subcategories_hrefs = set()
        self.posts_hrefs = set()
        self.num_sent_posts = 0

    def check_connection(
        self, page: str = None, printable=False
    ) -> requests.Response | bool:
        try:
            response = requests.get(page or self.SITE_URL)

            if response.status_code != HTTPStatus.OK:
                bad_request_message(self.__class__.__name__)

            if printable:
                good_request_message(self.__class__.__name__)

            return response

        except requests.ConnectionError:
            print(
                color("Проверьте соединение с интернетом.", "red", "bold"),
                color("Для выхода закройте окно или нажмите Enter.", "red"),
                sep="\n",
            )
            exit(input())

    def get_count_sent_posts(self):
        class_name = color(f"[{self.__class__.__name__}]", "cyan", "bold")
        sent = color(
            f"- Отправлено {self.num_sent_posts}/{len(self.posts_hrefs)}", "orange"
        )
        return f"{class_name} {sent}"
