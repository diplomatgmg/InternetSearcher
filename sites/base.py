import time
from abc import ABC
from datetime import datetime, timedelta
from http import HTTPStatus

import requests

from managment import settings
from managment.openai_gpt import translate_chat_gpt
from managment.send_tg import send_telegram
from managment.services import bad_request_message, good_request_message, translator


class BaseParser(ABC):
    SITE_URL = None
    language = None
    session = None
    time_correction: int = 0
    interval: float = 0

    def __init__(self, keywords: list = None, time_interval: int = False) -> None:
        self.keywords = self.translate_keywords(keywords)
        self.time_interval = self.get_time_interval(time_interval)
        self.categories_hrefs = set()
        self.subcategories_hrefs = set()
        self.pages_hrefs = set()
        self.posts_hrefs = set()

    def translate_keywords(self, keywords: list):
        return [
            translator.translate(word, self.language, "ru").text.lower() for word in keywords
        ]

    def get_time_interval(self, time_interval):
        return datetime.now() - timedelta(hours=time_interval + self.time_correction)

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

                if cls.interval:
                    time.sleep(cls.interval)

                return response

            except:
                if retries == 10:
                    print(f"Издание {cls.__name__} не ответило.")

                    return False

                print(
                    f"Издание {cls.__name__} не отвечает. Идет повторное подключение..."
                )

                retries += 1
                time.sleep(retries * 2)

    def start(self):
        self.get_categories_hrefs()
        self.get_posts_hrefs_from_category()
        self.get_subcategories_hrefs()
        self.get_pages_hrefs()
        self.get_posts_hrefs()
        self.check_page_delivery()

    def get_categories_hrefs(self):
        pass

    def get_posts_hrefs_from_category(self):
        pass

    def get_subcategories_hrefs(self):
        pass

    def get_pages_hrefs(self):
        pass

    def get_posts_hrefs(self):
        pass

    def check_page_delivery(self):
        pass

    def print_send_post(self):
        print(f"[{self.__class__.__name__}] Новость подходит!")

    def send(self, to_translate, post_href, need_translate=True):
        is_test = settings.DEBUG

        if not is_test:
            to_send = translate_chat_gpt(to_translate) if need_translate else to_translate
            to_send += f"\n\n{post_href}"
            send_telegram(to_send)
            self.print_send_post()
        else:
            self.print_send_post()
            print(post_href)
            print()
