import re
from datetime import datetime, timedelta

from bs4 import BeautifulSoup, Comment

from default import translator
from sites.base import BaseParser


class KhaleejTimes(BaseParser):
    SITE_URL = "https://www.khaleejtimes.com"

    def start(self):
        self.get_categories()
        self.get_posts_hrefs_from_category()
        self.send_posts()

    def get_categories(self):
        self.categories_hrefs = [
            "https://www.khaleejtimes.com/world",
            "https://www.khaleejtimes.com/opinion",
            "https://www.khaleejtimes.com/business",
            "https://www.khaleejtimes.com/sports",
            "https://www.khaleejtimes.com/entertainment",
            "https://www.khaleejtimes.com/lifestyle",
            "https://www.khaleejtimes.com/supplements",
        ]

    def get_posts_hrefs_from_category(self):
        for category_href in self.categories_hrefs:
            page = self.check_connection(category_href)

            if not page:
                return False

            soup = BeautifulSoup(page.content, "html.parser")
            posts_divs = soup.find_all("article", class_="post")
            time_pattern = r"(\d) (\w+) (\w+)"

            for post_div in posts_divs:
                str_time_raw = str(
                    post_div(text=lambda text: isinstance(text, Comment))[0]
                )
                str_time = re.search(time_pattern, str_time_raw)
                num_time = int(str_time.group(1))
                name_time = str_time.group(2)
                post_time = self.parse_str_time(num_time, name_time)

                if not post_time or post_time < self.time_interval:
                    continue

                page_href = post_div.find("h2", class_="post-title").find("a")["href"]
                self.posts_hrefs.add(page_href)

    def parse_str_time(self, num_time: int, name_time: str):
        if name_time.startswith("minute"):
            return datetime.now() - timedelta(minutes=num_time)
        elif name_time.startswith("hour"):
            return datetime.now() - timedelta(hours=num_time)
        elif name_time.startswith("day"):
            return datetime.now() - timedelta(days=num_time)
        elif (
            name_time.startswith("month")
            or name_time.startswith("week")
            or name_time.startswith("year")
        ):
            return False

    def send_posts(self):
        for post_href in self.posts_hrefs:
            page = self.check_connection(post_href)

            if not page:
                return False

            soup = BeautifulSoup(page.content, "html.parser")
            parse_text_raw = soup.find("div", class_="article-paragraph-wrapper")

            if not parse_text_raw:
                parse_text_raw = soup.find("div", class_="article-wrapper")

            if not parse_text_raw:
                continue

            post_raw_time = (
                parse_text_raw.find("div", class_="article-top-author-nw-nf-right")
                .find("p")
                .text.strip()
            )

            post_time = self.get_time_from_string(post_raw_time)

            if post_time < self.time_interval:
                continue

            parse_text_raw = parse_text_raw.text.lower()

            parse_text = " ".join(parse_text_raw.replace("\n", " ").split())

            if any(keyword in parse_text.split() for keyword in self.keywords):
                header = soup.find("h1").text.strip()
                subheader = soup.find("h3", class_="preamble-nf").text.strip()
                paragraph = soup.find_all("p")[2].text

                if paragraph.startswith("Last updated:"):
                    paragraph = soup.find_all("p")[3].text.strip()

                to_translate = f"{header}\n" f"\n" f"{subheader}\n" f"\n" f"{paragraph}"
                to_send = translator.translate(to_translate, dest="ru").text
                to_send += f"\n\n{post_href}"
                self.print_send_post()

                # TODO
                # send_telegram(to_send)

    def get_time_from_string(self, string: str):
        str_time = string.split(maxsplit=1)[1]
        post_time = datetime.strptime(str_time, "%a %d %b %Y, %H:%M %p")
        return post_time


def test():
    keywords = [chr(letter) for letter in range(ord("a"), ord("z") + 1)]
    time = 1
    obj = KhaleejTimes(keywords, time)
    obj.start()


