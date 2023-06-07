from datetime import timedelta, datetime

from bs4 import BeautifulSoup

from default import translator, color
from sites.base import BaseParser


class DziennikWschodni(BaseParser):
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

    def start(self):
        self.get_pages()
        self.get_posts()
        self.send_posts()

    def get_pages(self):
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

    def get_posts(self):
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

                if post_time <= self.time_interval:
                    break

                post_href = self.get_main_page() + post.find("a", href=True)["href"]
                self.posts_hrefs.add(post_href)

    def send_posts(self):
        for post_href in self.posts_hrefs:
            page = self.check_connection(post_href)

            if not page:
                return False

            soup = BeautifulSoup(page.content, "html.parser")

            header = soup.find("h1", class_="single-news__title").text.strip()
            content_raw = soup.find("div", class_="single-news__main-content")
            content = " ".join(content_raw.text.split())
            parse_text = (header + " " + content).lower()

            if any(keyword in parse_text for keyword in self.keywords):
                subheader = soup.find("p", class_="single-news__lead").text.strip()

                div_paragraph = soup.find("div", class_="single-news__text-content")

                first_paragraph = div_paragraph.find("p")

                if not first_paragraph:
                    first_paragraph = div_paragraph.find("div")

                first_paragraph = first_paragraph.text.strip()

                to_translate = (
                    f"{header}\n" f"\n" f"{subheader}\n" f"\n" f"{first_paragraph}"
                )

                self.num_sent_posts += 1

                to_send = translator.translate(to_translate, dest="ru").text

                to_send += f"\n\n{post_href}"

                print(
                    f"{color('Новость подходит!', 'green')} {color(f'[{self.__class__.__name__}]', 'cyan', 'bold')}"
                )


                # TODO
                # send_telegram(to_send)