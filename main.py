import seacher
from default import color
from sites.china_daily import ChinaDaily
from sites.dziennik_wschodni import DziennikWschodni

SITES = [
    ChinaDaily(),
    DziennikWschodni(),
]


def check_sites_connection():
    for site in SITES:
        site.check_connection(printable=True)


def main(preview=True, old_keywords=None):
    keywords = None

    if preview:
        print(color("Устанавливается соединение с сайтами...", "purple"))
        check_sites_connection()

    if old_keywords is not None:
        keywords = input(
            f"Прошлые ключевые слова: {color(old_keywords, 'cyan')}.\n"
            f"Введите ключевые слова или нажмите {color('Enter', 'cyan')}, чтобы оставить прошлые.\n"
        )
        if keywords == "":
            return seacher.search(old_keywords)

    if not keywords:
        keywords = input(
            "\nВведите через пробел ключевые слова для поиска.\n"
            "Для поиска двух слов используйте '+'. "
            "Например: 'путин+сказал'\n"
        )

    keywords = combine_words(keywords)

    return seacher.search(keywords)


def combine_words(words: str):
    result = []

    for word in words.split():
        word = " ".join(word.split("="))
        result.append(word)

    return result


if __name__ == "__main__":
    main()
