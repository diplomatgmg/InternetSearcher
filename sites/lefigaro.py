import re
from datetime import datetime

from bs4 import BeautifulSoup

from sites.base import BaseParser


class Lefigaro(BaseParser):
    SITE_URL = "https://www.lefigaro.fr/"
    language = 'fr'
    time_correction = +2

    def get_categories_hrefs(self):
        page = self.check_connection()

        if not page:
            return False

        soup = BeautifulSoup(page.content, "html.parser")
        nav_bar = soup.find("ul", class_="fh-kw__list")
        categories = nav_bar.find_all("a")
        regex = r"https:\/\/www.lefigaro.fr\/.+"

        for category in categories:
            category_match = re.search(regex, category["href"])

            if category_match:
                category_href = category_match.group(0)
                self.categories_hrefs.add(category_href)

    def get_pages_hrefs(self):
        for category_href in self.categories_hrefs:
            page = self.check_connection(category_href)

            if not page:
                return False

            soup = BeautifulSoup(page.content, "html.parser")
            flash_news_href = soup.find("a", class_="fig-vitrine__showmore")

            if flash_news_href:
                flash_news_href = flash_news_href["href"]
                self.pages_hrefs.add(flash_news_href)

                for num_page in range(2, 7):
                    self.pages_hrefs.add(flash_news_href + f"?page={num_page}")

    def get_posts_hrefs(self):
        for page_href in self.pages_hrefs:
            page = self.check_connection(page_href)

            if not page:
                return False

            soup = BeautifulSoup(page.content, "html.parser")
            posts = soup.find_all("article", class_="fig-flash__item")

            for post in posts:
                post_raw_time = (
                    post.find("time")["datetime"].replace("CEST", " ").split("+")[0]
                )
                post_time = datetime.strptime(post_raw_time, "%Y-%m-%d %H:%M:%S")

                if post_time < self.time_interval:
                    continue

                post_href = post.find("a", class_="fig-flash__data")["href"]
                self.posts_hrefs.add(post_href)

    def check_page_delivery(self):
        for post_href in self.posts_hrefs:
            page = self.check_connection(post_href)

            if not page:
                return False

            soup = BeautifulSoup(page.content, "html.parser")
            content_raw = soup.find("article")
            parse_text = " ".join(content_raw.text.split()).lower()

            if any(keyword in parse_text.split() for keyword in self.keywords):
                header = content_raw.find("h1").text.strip()
                subheader = content_raw.find("p", class_="fig-standfirst")
                paragraphs = content_raw.find_all("p", class_="fig-paragraph")

                if subheader:
                    subheader = subheader.text.strip()
                    paragraph = paragraphs[0].text.strip()
                else:
                    subheader = paragraphs[0].text.strip()

                    if len(paragraphs) >= 2:
                        paragraph = paragraphs[1].text.strip()
                    else:
                        paragraph = ""

                if len(paragraph) <= 150 and len(paragraphs) >= 3:
                    paragraph = paragraphs[2].text.strip()

                to_translate = f"{header}\n" f"\n" f"{subheader}\n" f"\n" f"{paragraph}"

                self.send(to_translate, post_href)


def test():
    keywords = [chr(letter) for letter in range(ord("a"), ord("z") + 1)]
    time = 1 + 1
    obj = Lefigaro(keywords, time)
    obj.start()
