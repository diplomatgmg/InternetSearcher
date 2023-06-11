import re
from datetime import datetime

from bs4 import BeautifulSoup

from default import translator
from openai_gpt import translate_chat_gpt
from send_tg import send_telegram
from sites.base import BaseParser


class Spiegel(BaseParser):
    SITE_URL = "https://www.spiegel.de"
    language = 'de'


    def start(self):
        self.get_categories_hrefs()
        self.get_posts_hrefs()
        self.send_posts()

    def get_categories_hrefs(self):
        page = self.check_connection()

        if not page:
            return False

        category_href = "https://www.spiegel.de/schlagzeilen/"
        self.categories_hrefs.add(category_href)

    def get_posts_hrefs(self):
        for category_href in self.categories_hrefs:
            page = self.check_connection(category_href)

            if not page:
                return False

            soup = BeautifulSoup(page.content, "html.parser")

            sections = soup.find_all("section", class_="z-10 w-full")[:3]

            for section in sections:
                day_raw = section.find("h2").text
                day_regex = r"\w+, (\d{1,2})\. \w+ \d{4}"
                day = int(re.search(day_regex, day_raw).group(1))
                posts = section.find_all("article")
                for post in posts:
                    post_raw_time = re.search("(\d\d)[.](\d\d) Uhr", post.text)

                    hours = int(post_raw_time.group(1))
                    minute = int(post_raw_time.group(2))

                    today = datetime.now()
                    year = today.year
                    month = today.month
                    post_time = datetime(
                        year=year, month=month, day=day, hour=hours, minute=minute
                    )

                    if post_time < self.time_interval:
                        continue

                    premium_page = post.find(
                        "span", {"data-contains-flags": "Spplus-paid"}
                    )

                    if premium_page:
                        continue

                    post_href = post.find("a")["href"]
                    self.posts_hrefs.add(post_href)

    def send_posts(self):
        for post_href in self.posts_hrefs:
            page = self.check_connection(post_href)

            if not page:
                return False

            soup = BeautifulSoup(page.content, "html.parser")

            header_and_subheader = soup.find(
                "div",
                class_="lg:w-10/12 md:w-10/12 lg:mx-auto md:mx-auto lg:px-24 md:px-24 sm:px-16",
            )

            if not header_and_subheader:
                continue

            header = " ".join(header_and_subheader.find("h2").text.split())
            subheader = " ".join(header_and_subheader.find("div").text.split())

            content = soup.find("div", {"data-area": "body"})

            sections = content.find_all("section")

            if sections:
                count_sections = len(sections)
                for _ in range(count_sections):
                    section = content.find("section")
                    if section:
                        section.decompose()

            paragraphs = content.find_all("div", {"data-area": "text"})

            if not paragraphs:
                continue

            clear_paragraphs = [
                " ".join(paragraph.text.strip().split()) for paragraph in paragraphs
            ]
            parse_paragraphs = " ".join(clear_paragraphs).lower()

            parse_text = f"{header} {subheader} {parse_paragraphs}".lower()

            if any(keyword in parse_text.split() for keyword in self.keywords):
                paragraph = " ".join(paragraphs[0].text.split())

                to_translate = f"{header}\n" f"\n" f"{subheader}\n" f"\n" f"{paragraph}"
                if not self.is_test:
                    to_send = translate_chat_gpt(to_translate)
                    to_send += f"\n\n{post_href}"
                    send_telegram(to_send)
                    self.print_send_post()
                else:
                    translated = translator.translate(header, dest='ru').text
                    self.print_send_post()
                    print(translated)
                    print(post_href)
                    print()


def test():
    keywords = [chr(letter) for letter in range(ord("a"), ord("z") + 1)]
    time = 1 + 24
    obj = Spiegel(keywords, time)
    obj.start()
