import time
from abc import ABC
from datetime import datetime, timedelta
from http import HTTPStatus

import requests

from default import bad_request_message, good_request_message, color


class BaseParser(ABC):
    SITE_URL = None
    session = None

    def __init__(self, keywords: list = None, time_interval: int = False) -> None:
        self.keywords = keywords
        self.time_interval = datetime.now() - timedelta(hours=time_interval)
        self.categories_hrefs = set()
        self.subcategories_hrefs = set()
        self.pages_hrefs = set()
        self.posts_hrefs = set()
        self.num_sent_posts = 0

    @classmethod
    def get_session(cls):
        session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(pool_connections=100, pool_maxsize=100)
        session.mount("https://", adapter)
        cls.session = session

        return cls.session

    @classmethod
    def check_connection(
        cls, page: str = None, printable=False
    ) -> requests.Response | bool:
        retries = 0
        session = cls.session or cls.get_session()

        while True:
            try:
                response = session.get(page or cls.SITE_URL, timeout=10)

                if response.status_code != HTTPStatus.OK:
                    bad_request_message(cls.__name__)

                if printable:
                    good_request_message(cls.__name__)

                return response

            except (
                requests.exceptions.ConnectionError or requests.exceptions.ReadTimeout
            ):
                if retries == 10:
                    print(
                        f"{color('Издание', 'red')} "
                        f"[{color(cls.__name__, 'cyan')}] "
                        f"{color('не ответило.', 'red')}"
                    )

                    return False

                print(
                    f"{color('Издание', 'red')} "
                    f"[{color(cls.__name__, 'cyan')}] "
                    f"{color('не отвечает. Идет повторное подключение...', 'red')}"
                )
                retries += 1
                time.sleep(retries)

    def get_count_sent_posts(self):
        class_name = color(f"[{self.__class__.__name__}]", "cyan", "bold")
        sent = color(
            f"- Отправлено {self.num_sent_posts}/{len(self.posts_hrefs)}", "orange"
        )

        return f"{class_name} {sent}"

    def start(self):
        pass

    def get_categories_hrefs(self):
        pass

    def get_pages_hrefs(self):
        pass

    def get_posts_hrefs(self):
        pass

    def send_posts(self):
        pass

    def print_send_post(self):
        print(
            f"{color(f'[{self.__class__.__name__}]', 'cyan', 'bold')} "
            f"{color('Новость подходит!', 'green')} "
            f"{color(f'Отправлено {self.num_sent_posts}/{len(self.posts_hrefs)}')}"
        )
