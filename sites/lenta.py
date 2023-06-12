from bs4 import BeautifulSoup

from sites.base import BaseParser



class LentaRu(BaseParser):
    SITE_URL = "https://lenta.ru"
    language = 'ru'


    def start(self):
        self.get_categories_hrefs()


    def get_categories_hrefs(self):
        page = self.check_connection()

        if not page:
            return False

        soup = BeautifulSoup(page.content, "html.parser")
        nav_bar = soup.find('ul', class_='menu__nav-list')
        categories = nav_bar.find_all('a', class_='menu__nav-link')

        for category in categories:
            print(category.text.strip())




def test():
    keywords = [chr(letter) for letter in range(ord("а"), ord("я") + 1)]
    time = 1
    obj = LentaRu(keywords, time)
    obj.start()

test()
