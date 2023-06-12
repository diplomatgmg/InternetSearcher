from datetime import datetime

from bs4 import BeautifulSoup

from sites.base import BaseParser


class TheGuardian(BaseParser):
    SITE_URL = "https://www.theguardian.com"
    language = 'en'
    time_correction = +3

    def get_subcategories_hrefs(self):
        page = self.check_connection(self.SITE_URL)

        if not page:
            return False

        soup = BeautifulSoup(page.content, "html.parser")
        subcategories = soup.find_all(
            "a", {"class": "menu-item__title", "role": "menuitem"}
        )

        for subcategory in subcategories:
            subcategory_href = subcategory["href"]
            if subcategory_href.startswith("https://www.theguardian.com"):
                if not subcategory_href.startswith(
                        "https://www.theguardian.com/mobile"
                ):
                    self.subcategories_hrefs.add(subcategory_href)

    def check_page_delivery(self):
        for subcategory_href in self.subcategories_hrefs:
            page = self.check_connection(subcategory_href)

            if not page:
                return False

            soup = BeautifulSoup(page.content, "html.parser")
            posts = soup.find_all(
                "a", class_="u-faux-block-link__overlay js-headline-text"
            )

            for post in posts:
                post_href = post["href"]

                if not post_href.startswith("https://www.theguardian.com"):
                    continue

                page = self.check_connection(post_href)

                if not page:
                    return False

                soup = BeautifulSoup(page.content, "html.parser")
                post_raw_time = soup.find("span", class_="dcr-u0h1qy")

                if not post_raw_time:
                    continue

                post_raw_time = post_raw_time.text.strip()

                post_time = self.get_post_time(post_raw_time)

                if post_time < self.time_interval:
                    continue

                header = soup.find("h1")

                if not header:
                    continue

                header = header.text.strip()
                subheader = soup.find("div", {"data-gu-name": "standfirst"})

                if not subheader:
                    continue

                subheader = subheader.text.strip().replace("\n", " ")

                content_raw = soup.find(
                    "div",
                    id="maincontent",
                )

                if not content_raw:
                    continue

                content_text = " ".join(content_raw.text.replace("\n", " ").split())
                subheader = " ".join(subheader.split())
                parse_text = (header + " " + subheader + "  " + content_text).lower()

                if any(keyword in parse_text.split() for keyword in self.keywords):
                    paragraph = content_raw.find("p").text.strip()

                    if not paragraph:
                        continue

                    to_translate = (
                        f"{header}\n" f"\n" f"{subheader}\n" f"\n" f"{paragraph}"
                    )

                    self.send(to_translate, post_href)

    @staticmethod
    def get_post_time(post_raw_time):
        post_raw_time = post_raw_time.split(maxsplit=1)[1]
        post_raw_time = post_raw_time.replace(" BST", "").replace(" GMT", "")
        post_time = datetime.strptime(post_raw_time, "%d %b %Y %H.%M")

        return post_time


def test():
    keywords = [chr(letter) for letter in range(ord("a"), ord("z") + 1)]
    time = 1 + 3
    obj = TheGuardian(keywords, time)
    obj.start()
