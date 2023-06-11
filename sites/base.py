import time
from abc import ABC
from datetime import datetime, timedelta
from http import HTTPStatus

import requests

import main
from default import bad_request_message, good_request_message, translator


class BaseParser(ABC):
    SITE_URL = None
    language = None
    session = None

    def __init__(self, keywords: list = None, time_interval: int = False) -> None:
        self.keywords = self.translate_keywords(keywords)
        self.time_interval = datetime.now() - timedelta(hours=time_interval)
        self.is_test = main.is_test
        self.categories_hrefs = set()
        self.subcategories_hrefs = set()
        self.pages_hrefs = set()
        self.posts_hrefs = set()

    def translate_keywords(self, keywords: list):
        return [
            translator.translate(word, self.language, "ru").text.lower() for word in keywords
        ]

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
                response = session.get(page or cls.SITE_URL, timeout=20)

                if response.status_code != HTTPStatus.OK:
                    bad_request_message(cls.__name__)

                if printable:
                    good_request_message(cls.__name__)

                return response

            except:
                if retries == 10:
                    print(f"Издание {cls.__name__} не ответило.")

                    return False

                print(
                    f"Издание {cls.__name__} не отвечает. Идет повторное подключение..."
                )

                retries += 1
                time.sleep(retries)

    def start(self):
        pass

    def get_categories_hrefs(self):
        pass

    def get_subcategories_hrefs(self):
        pass

    def get_posts_hrefs(self):
        pass

    def send_posts(self):
        pass

    def print_send_post(self):
        print(f"[{self.__class__.__name__}] Новость подходит!")
