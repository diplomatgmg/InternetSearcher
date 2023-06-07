import datetime
from abc import ABC
from abc import abstractmethod
from http import HTTPStatus

import requests

from default import bad_request_message, good_request_message, color


class BaseParser(ABC):
    SITE_URL = None

    def __init__(self, keywords: list = None, time_interval: datetime = None) -> None:
        self.keywords = keywords
        self.time_interval = time_interval
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

    @abstractmethod
    def get_categories_hrefs(self):
        pass

    @abstractmethod
    def get_subcategories_hrefs(self):
        pass

    @abstractmethod
    def get_posts(self):
        pass

    @abstractmethod
    def send_posts(self):
        pass

    def get_count_sent_posts(self):
        class_name = color(f"[{self.__class__.__name__}]", "cyan", "bold")
        sent = color(
            f"- Отправлено {self.num_sent_posts}/{len(self.posts_hrefs)}", "orange"
        )
        return f"{class_name} {sent}"

    def start(self):
        self.get_categories_hrefs()
        self.get_subcategories_hrefs()
        self.get_posts()
        self.send_posts()
