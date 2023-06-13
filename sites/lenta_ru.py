import re
from datetime import datetime

from bs4 import BeautifulSoup

from sites.base import BaseParser


class LentaRu(BaseParser):
    SITE_URL = "https://lenta.ru"
    language = 'ru'
    interval = 0.2

    def get_posts_hrefs(self):
        page = self.check_connection()

        if not page:
            return False

        today = datetime.now()
        year = today.year
        month = str(today.month)
        day = today.day

        if len(month) == 1:
            month = '0' + month

        for offset in range(4):
            temp_day = day - offset

            if len(str(temp_day)) == 1:
                temp_day = '0' + str(temp_day)

            archive_href = f"https://lenta.ru/{year}/{month}/{temp_day}/"
            next_page_href: None | str | bool = None

            while True:
                if next_page_href is False:
                    return
                elif next_page_href is None:
                    page = self.check_connection(archive_href)
                elif next_page_href:
                    page = self.check_connection(next_page_href)

                if not page:
                    return False

                soup = BeautifulSoup(page.content, "html.parser")
                posts = soup.find_all('a', class_='card-full-other') + soup.find_all('a', class_='card-full-news')

                for post in posts:
                    post_raw_time = post.find('time').text.strip()

                    post_time = self.convert_time(post_raw_time)

                    if post_time < self.time_interval:
                        continue

                    post_raw_href = post['href']

                    if post_raw_href.startswith('/news'):
                        post_href = self.SITE_URL + post_raw_href
                        self.posts_hrefs.add(post_href)

                next_page = soup.find_all('a', class_='loadmore')[-1]

                if '_disabled' in next_page['class']:
                    next_page_href = False
                else:
                    next_page_href = self.SITE_URL + next_page['href']

    def check_page_delivery(self):
        for post_href in self.posts_hrefs:
            page = self.check_connection(post_href)

            if not page:
                return False

            soup = BeautifulSoup(page.content, "html.parser")

            header = soup.find('h1', class_='topic-body__titles')

            if not header:
                continue

            header = header.text.strip()

            subheader = soup.find('div', class_='topic-body__title-yandex')

            if not subheader:
                continue

            subheader = subheader.text.strip()

            paragraphs = soup.find_all('p', class_='topic-body__content-text')

            if not paragraphs:
                continue

            content_text = " ".join(p.text.strip() for p in paragraphs)
            parse_text = (header + "  " + subheader + ' ' + content_text).lower()

            if any(keyword in parse_text.split() for keyword in self.keywords):
                paragraph = paragraphs[0].text.strip()
                to_translate = f"{header}\n" f"\n" f"{subheader}\n" f"\n" f"{paragraph}"

                self.send(to_translate, post_href, need_translate=False)

    @staticmethod
    def convert_time(str_time: str):
        today = datetime.now()
        year = today.year
        month = today.month
        day = today.day

        regex = r'^(\d{2}):(\d{2})$'
        match_time = re.search(regex, str_time)

        if match_time:
            hour = int(match_time.group(1))
            minute = int(match_time.group(2))
            post_time = datetime(year, month, day, hour, minute)

        regex = r'^\d{2}:\d{2}, \d{1,2} (\w+) \d{4}'
        match_time = re.search(regex, str_time)

        if match_time:
            month_dict = {
                'января': 'Jan',
                'февраля': 'Feb',
                'марта': 'Mar',
                'апреля': 'Apr',
                'мая': 'May',
                'июня': 'Jun',
                'июля': 'Jul',
                'августа': 'Aug',
                'сентября': 'Sep',
                'октября': 'Oct',
                'ноября': 'Nov',
                'декабря': 'Dec'
            }
            month_ru = match_time.group(1)
            month_en = month_dict[month_ru]
            str_time = str_time.replace(month_ru, month_en)
            post_time = datetime.strptime(str_time, '%H:%M, %d %b %Y')

        return post_time


def test():
    keywords = [chr(letter) for letter in range(ord("а"), ord("я") + 1)]
    time = 1
    obj = LentaRu(keywords, time)
    obj.start()
