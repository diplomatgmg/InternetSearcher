import re
from datetime import datetime

from bs4 import BeautifulSoup

from default import translator
from sites.base import BaseParser


class UsaToday(BaseParser):
    SITE_URL = "https://usatoday.com"

    def start(self):
        self.get_categories_hrefs()
        self.get_subcategories_hrefs()
        self.get_posts_hrefs()
        self.send_posts()

    def get_categories_hrefs(self):
        page = self.check_connection(self.SITE_URL)

        if not page:
            return False

        soup = BeautifulSoup(page.content, "html.parser")
        categories = soup.find_all("a", class_="gnt_n_mn_l")

        for category in categories:
            category_href = category["href"]
            category_href = self.SITE_URL + category_href
            self.categories_hrefs.add(category_href)

    def get_subcategories_hrefs(self):
        for category_href in self.categories_hrefs:
            page = self.check_connection(category_href)

            if not page:
                return False

            soup = BeautifulSoup(page.content, "html.parser")

            subcategories = soup.find_all("a", class_="gnt_sn_a")
            self.subcategories_hrefs.add(category_href)

            for subcategory in subcategories:
                subcategory_href = subcategory["href"]

                if not subcategory_href.startswith("http"):
                    subcategory_href = self.SITE_URL + subcategory_href
                    self.subcategories_hrefs.add(subcategory_href)

    def get_posts_hrefs(self):
        for subcategory_href in self.subcategories_hrefs:
            page = self.check_connection(subcategory_href)

            if not page:
                return False

            soup = BeautifulSoup(page.content, "html.parser")

            posts = soup.find_all("a", class_="gnt_m_flm_a")

            if not posts:
                continue

            for post in posts:
                post_div_time = post.find(
                    "div", class_="gnt_m_flm_sbt gnt_sbt gnt_sbt__ms gnt_sbt__ts"
                )

                if not post_div_time:
                    continue

                post_raw_time = post_div_time["data-c-dt"]
                post_time = self.get_post_time(post_raw_time)

                if post_time < self.time_interval:
                    continue

                post_href = post["href"]

                if not post_href.startswith("https://"):
                    post_href = self.SITE_URL + post_href

                self.posts_hrefs.add(post_href)

    def send_posts(self):
        for post_href in self.posts_hrefs:
            page = self.check_connection(post_href)

            if not page:
                return False

            soup = BeautifulSoup(page.content, "html.parser")

            post_raw_time = soup.find("div", class_="gnt_ar_dt") or soup.find(
                "div", class_="gnt_sv_dt"
            )
            if not post_raw_time:
                post_raw_time = soup.find("story-timestamp")
                if not post_raw_time:
                    continue
                else:
                    post_raw_time = post_raw_time["publish-date"]
            else:
                post_raw_time = post_raw_time["aria-label"]

            post_time = self.get_post_time(post_raw_time)

            if post_time < self.time_interval:
                continue

            header = soup.find("h1", class_="display-2") or soup.find(
                "h1", class_="gnt_ar_hl"
            )

            if not header:
                continue

            header = header.text.strip()

            paragraphs = soup.find_all("p", class_="gnt_ar_b_p")

            if not paragraphs:
                continue

            content_text = " ".join(p.text.strip() for p in paragraphs)
            parse_text = (header + "  " + content_text).lower()

            # if any(keyword in parse_text.split() for keyword in self.keywords):

            subheader = paragraphs[0].text.strip()
            paragraph = paragraphs[1].text.strip()

            to_translate = f"{header}\n" f"\n" f"{subheader}\n" f"\n" f"{paragraph}"
            to_send = translator.translate(to_translate, dest="ru").text
            to_send += f"\n\n{post_href}"
            self.print_send_post()
            print(post_href)

    @staticmethod
    def get_post_time(post_raw_time: str) -> datetime:
        post_raw_time = post_raw_time.replace("a.m.", "AM").replace("p.m.", "PM")

        if post_match := re.search(
            r"\d{1,2}:\d{1,2} [AP]M ET \w+ \d{1,2}", post_raw_time
        ):
            post_str_time = str(datetime.now().year) + " " + post_match.group(0)
            post_time = datetime.strptime(post_str_time, "%Y %H:%M %p ET %B %d")

        elif post_match := re.match(r"\w+ \d{1,2}, \d{4}", post_raw_time):
            post_str_time = post_match.group(0)
            post_time = datetime.strptime(post_str_time, "%B %d, %Y")

        elif post_match := re.match(
            r"Published[:]? \d{1,2}:\d{1,2} [AP]M ET \w+ \d{1,2}, \d{4}", post_raw_time
        ):
            post_str_time = post_match.group(0)
            if ":" in post_str_time.split(maxsplit=1)[0]:
                post_str_time = post_str_time.replace(":", "", 1)
            post_time = datetime.strptime(
                post_str_time, "Published %H:%M %p ET %B %d, %Y"
            )

        elif post_match := re.match(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}", post_raw_time):
            post_str_time = post_match.group(0)
            post_time = datetime.strptime(post_str_time, "%Y-%m-%dT%H:%M")

        return post_time


def test():
    keywords = [chr(letter) for letter in range(ord("a"), ord("z") + 1)]
    time = 1 + 7
    obj = UsaToday(keywords, time)
    obj.start()


