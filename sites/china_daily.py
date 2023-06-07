import datetime
import re
from http import HTTPStatus

import requests
from bs4 import BeautifulSoup

from default import bad_request_message, good_request_message, color
from default import translator


class ChinaDaily:
    SITE_URL = "https://www.chinadaily.com.cn/"

    def __init__(self, keywords: list = None, time_interval: datetime = None) -> None:
        self.keywords = keywords
        self.time_interval = time_interval
        self.categories_hrefs = set()
        self.subcategories_hrefs = set()
        self.posts_hrefs = set()

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

    def start(self):
        self.get_categories_hrefs()
        self.get_subcategories_hrefs()
        self.get_posts()
        self.send_posts()

    def get_categories_hrefs(self) -> None | bool:
        page = self.check_connection(self.SITE_URL)

        if not page:
            return False

        soup = BeautifulSoup(page.content, "html.parser")
        nav_bar = soup.find("div", class_="topNav")

        if nav_bar:
            regex = r"www\.chinadaily\.com\.cn\/\w+"
            categories = nav_bar.find_all("a", href=True)

            for category in categories:
                category_match = re.search(regex, category["href"])

                if category_match:
                    category_href = "https://" + category_match.group(0)
                    self.categories_hrefs.add(category_href)

    def get_subcategories_hrefs(self) -> None | bool:
        for category in self.categories_hrefs:
            page = self.check_connection(category)

            if not page:
                return False

            soup = BeautifulSoup(page.content, "html.parser")
            nav_bar = soup.find("div", class_="topNav2_art")

            if nav_bar:
                regex = r"www\.chinadaily\.com\.cn\/\w+\/\w+"
                subcategories = nav_bar.find_all("a", href=True)

                for subcategory in subcategories:
                    subcategory_match = re.search(regex, subcategory["href"])

                    if subcategory_match:
                        subcategory_href = "https://" + subcategory_match.group(0)
                        self.subcategories_hrefs.add(subcategory_href)

    def get_posts(self):
        for sub_category in self.subcategories_hrefs:
            page = self.check_connection(sub_category)

            if not page:
                return False

            soup = BeautifulSoup(page.content, "html.parser")
            posts = soup.find_all("div", class_="mb10 tw3_01_2")

            for post in posts:
                str_time = post.find("span", class_="tw3_01_2_t").find("b").text
                post_time = datetime.datetime.strptime(str_time, "%Y-%m-%d %H:%M")

                if post_time < self.time_interval:
                    break

                post_raw_href = post.find("a", href=True)["href"]
                regex = r"www\.chinadaily\.com\.cn\/a\/.+"
                post_match = re.search(regex, post_raw_href)

                if post_match:
                    post_href = "https://" + post_match.group(0)
                    self.posts_hrefs.add(post_href)

    def send_posts(self):
        for post_href in self.posts_hrefs:
            page = self.check_connection(post_href)

            if not page:
                return False

            soup = BeautifulSoup(page.content, "html.parser")
            header = soup.find("div", class_="lft_art").find("h1")
            paragraphs = soup.find("div", id="Content").find_all("p")

            if not header or not paragraphs:
                continue

            header_text = header.text.strip()
            content_text = " ".join(paragraph.text.strip() for paragraph in paragraphs)

            parse_text = (header_text + " " + content_text).lower()

            if any(keyword in parse_text for keyword in self.keywords):
                first_paragraph = paragraphs[0].text.strip()
                second_paragraph = paragraphs[1].text.strip()

                to_translate = (
                    f"{header_text}\n"
                    f"\n"
                    f"{first_paragraph}\n"
                    f"\n"
                    f"{second_paragraph}"
                )

                if len(to_translate) < 250:
                    third_paragraph = paragraphs[2].text.strip()
                    to_translate += f"\n\n{third_paragraph}"

                to_send = translator.translate(to_translate, dest="ru").text

                to_send += f"\n\n{post_href}"

                print(
                    f"{color('Новость подходит!', 'green')} {color('[China Daily]', 'cyan', 'bold')}"
                )
                # send_telegram(to_send)


# test_time = datetime.datetime.now() - datetime.timedelta(hours=24)
# keywords = ["world", "and", "not", "but"]
#
# china_daily = ChinaDaily(keywords, test_time)
#
# china_daily.check_connection()
# china_daily.start()
