import time
from abc import ABC, abstractmethod
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
        self.session = self.get_session()

    @abstractmethod
    def get_session(self):
        pass

    def check_connection(
        self, page: str = None, printable=False
    ) -> requests.Response | bool:
        retries = 0
        while True:
            try:
                response = self.session.get(page or self.SITE_URL, timeout=10)

                if response.status_code != HTTPStatus.OK:
                    bad_request_message(self.__class__.__name__)

                if printable:
                    good_request_message(self.__class__.__name__)

                return response

            except (
                requests.exceptions.ConnectionError or requests.exceptions.ReadTimeout
            ):
                if retries == 10:
                    print(
                        f"{color('Издание', 'red')} "
                        f"[{color(self.__class__.__name__, 'cyan')}] "
                        f"{color('не ответило.', 'red')}"
                    )
                    return False
                print(
                    f"{color('Издание', 'red')} "
                    f"[{color(self.__class__.__name__, 'cyan')}] "
                    f"{color('не отвечает. Идет повторное подключение...', 'red')}"
                )
                retries += 1
                time.sleep(1)

    def get_count_sent_posts(self):
        class_name = color(f"[{self.__class__.__name__}]", "cyan", "bold")
        sent = color(
            f"- Отправлено {self.num_sent_posts}/{len(self.posts_hrefs)}", "orange"
        )
        return f"{class_name} {sent}"

    @abstractmethod
    def start(self):
        pass

    def print_send_post(self):
        print(
            f"{color(f'[{self.__class__.__name__}]', 'cyan', 'bold')} "
            f"{color('Новость подходит!', 'green')} "
            f"{color(f'Отправлено {self.num_sent_posts}/{len(self.posts_hrefs)}')}"
        )
