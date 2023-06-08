from bs4 import BeautifulSoup

from default import translator
from sites.base import BaseParser


class Spiegel(BaseParser):
    SITE_URL = "https://www.spiegel.de"

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
                posts = section.find_all("h2")[1:]
                for post in posts:
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
                self.num_sent_posts += 1
                to_send = translator.translate(to_translate, dest="ru").text
                to_send += f"\n\n{post_href}"

                self.print_send_post()
