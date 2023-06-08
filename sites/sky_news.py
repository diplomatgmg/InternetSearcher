import re
from datetime import datetime

from bs4 import BeautifulSoup

from default import translator
from sites.base import BaseParser


class SkyNews(BaseParser):
    SITE_URL = "https://news.sky.com"

    def start(self):
        self.get_categories_hrefs()
        self.get_posts_hrefs()
        self.send_posts()

    def get_categories_hrefs(self):
        page = self.check_connection()

        if not page:
            return False

        soup = BeautifulSoup(page.content, "html.parser")
        nav_bar = soup.find("ul", class_="ui-news-header-nav-items")
        categories = nav_bar.find_all("a")

        for category in categories:
            category_href = self.SITE_URL + category["href"]
            self.categories_hrefs.add(category_href)

    def get_posts_hrefs(self):
        for category_href in self.categories_hrefs:
            page = self.check_connection(category_href)

            if not page:
                return False

            soup = BeautifulSoup(page.content, "html.parser")
            posts = soup.find_all("h3")

            for post in posts:
                post_raw_href = post.find("a")["href"]

                if post_raw_href.startswith("http://"):
                    continue

                if not post_raw_href.startswith("https://"):
                    post_href = self.SITE_URL + post_raw_href

                self.posts_hrefs.add(post_href)

    def send_posts(self):
        for post_href in self.posts_hrefs:
            page = self.check_connection(post_href)

            if not page:
                return False

            soup = BeautifulSoup(page.content, "html.parser")
            post_raw_time = soup.find("p", class_="sdc-article-date__date-time")

            if not post_raw_time:
                continue

            post_raw_time = post_raw_time.text.strip()
            post_time = self.convert_time(post_raw_time)

            if post_time < self.time_interval:
                continue

            content_raw = soup.find("div", class_="section-wrap")
            parse_text = " ".join(content_raw.text.replace("\n", " ").split()).lower()

            if any(keyword in parse_text.split() for keyword in self.keywords):
                header = content_raw.find("h1").text.strip()
                subheader = content_raw.find("p").text.strip()
                paragraph = content_raw.find("div", class_="sdc-article-body") or ""

                if paragraph:
                    paragraph = paragraph.find("p") or ""
                    if paragraph:
                        paragraph = paragraph.text.strip()

                to_translate = f"{header}\n" f"\n" f"{subheader}\n" f"\n" f"{paragraph}"
                self.num_sent_posts += 1
                to_send = translator.translate(to_translate, dest="ru").text
                to_send += f"\n\n{post_href}"
                self.print_send_post()

    @staticmethod
    def convert_time(raw_time: str):
        regex = r"(\d{1,2}) (\w+) (\d{4}) (\d{2}):(\d{2})"
        match = re.search(regex, raw_time)
        str_time = match.group()
        post_time = datetime.strptime(str_time, "%d %B %Y %H:%M")
        return post_time


def test():
    keywords = [chr(letter) for letter in range(ord("a"), ord("z") + 1)]
    time = 1 + 2
    obj = SkyNews(keywords, time)
    obj.start()
