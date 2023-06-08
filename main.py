import seacher
from default import color, check_sites_connection
from sites.china_daily import ChinaDaily
from sites.dziennik_wschodni import DziennikWschodni
from sites.khaleejtimes import KhaleejTimes
from sites.lefigaro import Lefigaro
from sites.sky_news import SkyNews

SITES = [
    ChinaDaily,
    DziennikWschodni,
    KhaleejTimes,
    Lefigaro,
    SkyNews,
]


def main(preview=True, old_keywords=None):
    keywords = None

    if preview:
        print(color("Устанавливается соединение с сайтами...", "purple"))
        check_sites_connection(SITES)

    if old_keywords is not None:
        keywords = input(
            f"Прошлые ключевые слова: {color(old_keywords, 'cyan')}.\n"
            f"Введите ключевые слова или нажмите {color('Enter', 'cyan')}, чтобы оставить прошлые.\n"
        )
        if keywords == "":
            return seacher.search(old_keywords)

    if not keywords:
        phrase1 = color("+", "cyan")
        phrase2 = color("ядерное+оружие", "cyan")
        keywords = input(
            "\nВведите через пробел ключевые слова для поиска.\n"
            f'Для поиска двух слов используйте "{phrase1}". '
            f'Например: "{phrase2}"\n'
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
