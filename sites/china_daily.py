import datetime
import re

from bs4 import BeautifulSoup

from default import color
from default import translator
from sites.base import BaseParser


class ChinaDaily(BaseParser):
    SITE_URL = "https://www.chinadaily.com.cn/"

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

                if post_time <= self.time_interval:
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

            try:
                header = soup.find("div", class_="lft_art").find("h1")
                paragraphs = soup.find("div", id="Content").find_all("p")
            except AttributeError:
                continue

            if not header or not paragraphs:
                continue

            header_text = header.text.strip()
            content_text = " ".join(paragraph.text.strip() for paragraph in paragraphs)

            parse_text = (header_text + " " + content_text).lower()

            if any(keyword in parse_text for keyword in self.keywords):
                if len(paragraphs) > 1:
                    first_paragraph = paragraphs[0].text.strip()
                    second_paragraph = paragraphs[1].text.strip()
                else:
                    first_paragraph, second_paragraph = (
                        paragraphs[0].text.strip().split(".", maxsplit=1)
                    )

                to_translate = (
                    f"{header_text}\n"
                    f"\n"
                    f"{first_paragraph}\n"
                    f"\n"
                    f"{second_paragraph}"
                )

                self.num_sent_posts += 1

                to_send = translator.translate(to_translate, dest="ru").text

                to_send += f"\n\n{post_href}"

                print(
                    f"{color('Новость подходит!', 'green')} {color(f'[{self.__class__.__name__}]', 'cyan', 'bold')}"
                )

                # TODO


# send_telegram(to_send)
