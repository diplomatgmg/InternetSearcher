from datetime import datetime, timedelta

from bs4 import BeautifulSoup

from sites.base import BaseParser


class DziennikWschodni(BaseParser):
    SITE_URL = "https://www.dziennikwschodni.pl"
    language = 'pl'
    time_correction = +1

    def __init__(self, *args, **kwargs):
        super().__init__(*args, *kwargs)
        self.SITE_URL = self.get_site_url()
        self.pages_hrefs = {self.SITE_URL}

    @staticmethod
    def get_main_page():
        return "https://www.dziennikwschodni.pl"

    @staticmethod
    def get_site_url():
        last_days = (datetime.now() - timedelta(hours=96)).strftime("%d-%m-%Y")
        today = datetime.now().strftime("%d-%m-%Y")
        url = f"https://www.dziennikwschodni.pl/data.html?date_begin={last_days}&date_end={today}&kategoria=&search="
        return url

    def get_pages_hrefs(self):
        current_page = self.SITE_URL

        while True:
            page = self.check_connection(current_page)

            if not page:
                return False

            soup = BeautifulSoup(page.content, "html.parser")
            next_page_obj = soup.find(
                "a", class_="pagination__item pagination__item--right"
            )

            if not next_page_obj:
                break

            next_page = self.SITE_URL.split("/data.html")[0] + next_page_obj["href"]
            current_page = next_page
            self.pages_hrefs.add(current_page)

    def get_posts_hrefs(self):
        for page_href in self.pages_hrefs:
            page = self.check_connection(page_href)

            if not page:
                return False

            soup = BeautifulSoup(page.content, "html.parser")
            posts = soup.find_all("tr")

            for post in posts:
                date_obj, time_obj, post_href_obj = post.find_all("td")
                datetime_obj = f"{date_obj.text.strip()} {time_obj.text.strip()}"

                post_time = datetime.strptime(datetime_obj, "%d.%m.%Y %H:%M")

                if post_time < self.time_interval:
                    continue

                post_href = self.get_main_page() + post.find("a", href=True)["href"]
                self.posts_hrefs.add(post_href)

    def check_page_delivery(self):
        print('Dziennik Wshodni -', len(self.posts_hrefs), 'posts')
        for post_href in self.posts_hrefs:
            page = self.check_connection(post_href)

            if not page:
                return False

            soup = BeautifulSoup(page.content, "html.parser")

            header = soup.find("h1", class_="single-news__title").text.strip()
            content_raw = soup.find("div", class_="single-news__main-content")
            content = " ".join(content_raw.text.split())
            parse_text = (header + " " + content).lower()

            if any(keyword in parse_text.split() for keyword in self.keywords):
                subheader = soup.find("p", class_="single-news__lead").text.strip()

                div_paragraph = soup.find("div", class_="single-news__text-content")
                first_paragraph = div_paragraph.find("p")

                if not first_paragraph:
                    first_paragraph = div_paragraph.find("div")
                    if not first_paragraph:
                        continue

                first_paragraph = first_paragraph.text.strip()
                to_translate = (
                    f"{header}\n" f"\n" f"{subheader}\n" f"\n" f"{first_paragraph}"
                )

                self.send(to_translate, post_href)


def test():
    keywords = [chr(letter) for letter in range(ord("a"), ord("z") + 1)]
    time = 1 + 1
    obj = DziennikWschodni(keywords, time)
    obj.start()
