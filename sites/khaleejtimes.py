import re
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from default import translator
from sites.base import BaseParser


class KhaleejTimes(BaseParser):
    SITE_URL = "https://www.khaleejtimes.com"

    def get_session(self):
        session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(pool_connections=100, pool_maxsize=100)
        session.mount("https://", adapter)
        return session
        pass

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
            post_divs = soup.find_all("div", class_="post-thumbnail")
            for post_div in post_divs:
                page_href = post_div.find("a", href=True)["href"]
                self.posts_hrefs.add(page_href)

    def send_posts(self):
        for post_href in self.posts_hrefs:
            page = self.check_connection(post_href)

            if not page:
                return False

            soup = BeautifulSoup(page.content, "html.parser")

            raw_post_time = soup.find("div", class_="article-top-author-nw-nf-right")

            if not raw_post_time:
                continue

            raw_post_time = raw_post_time.find("p").text
            post_time = self.convert_time(raw_post_time)

            if post_time <= self.time_interval:
                continue

            parse_text_raw = soup.find("div", class_="article-paragraph-wrapper")
            if not parse_text_raw:
                parse_text_raw = soup.find("div", class_="article-wrapper")

            if not parse_text_raw:
                continue

            parse_text_raw = parse_text_raw.text.lower()

            parse_text = " ".join(parse_text_raw.replace("\n", " ").split())

            if any(keyword in parse_text for keyword in self.keywords):
                header = soup.find("h1").text.strip()
                subheader = soup.find("h3", class_="preamble-nf").text.strip()
                paragraph = soup.find_all("p")[2].text

                if paragraph.startswith("Last updated:"):
                    paragraph = soup.find_all("p")[3].text.strip()

                to_translate = f"{header}\n" f"\n" f"{subheader}\n" f"\n" f"{paragraph}"
                self.num_sent_posts += 1
                to_send = translator.translate(to_translate, dest="ru").text
                to_send += f"\n\n{post_href}"

                self.print_send_post()

                # TODO
                # send_telegram(to_send)

    @staticmethod
    def convert_time(time: str):
        regex = r"(\w{3}) (\d{1,2}) (\w{3}) (\d{4}), (\d{1,2}):(\d{2}) ([AP]M)"
        match = re.search(regex, time)

        day = match.group(2)
        month = match.group(3)
        year = match.group(4)
        hour = int(match.group(5))
        minute = int(match.group(6))
        am_pm = match.group(7)

        month_dict = {
            "Jan": 1,
            "Feb": 2,
            "Mar": 3,
            "Apr": 4,
            "May": 5,
            "Jun": 6,
            "Jul": 7,
            "Aug": 8,
            "Sep": 9,
            "Oct": 10,
            "Nov": 11,
            "Dec": 12,
        }

        month_number = month_dict[month]

        if am_pm == "PM" and hour != 12:
            hour += 12
        elif am_pm == "AM" and hour == 12:
            hour = 0

        date_time = datetime(int(year), month_number, int(day), hour, minute)
        return date_time


