import seacher
from default import check_sites_connection
from openai_gpt import get_openai_api_key
from sites.china_daily import ChinaDaily
from sites.dziennik_wschodni import DziennikWschodni
from sites.khaleejtimes import KhaleejTimes
from sites.lefigaro import Lefigaro
from sites.sky_news import SkyNews
from sites.spiegel import Spiegel
from sites.theguadrian import TheGuardian
from sites.usa_today import UsaToday

SITES = {
    ChinaDaily,
    DziennikWschodni,
    KhaleejTimes,
    Lefigaro,
    SkyNews,
    Spiegel,
    TheGuardian,
    UsaToday,
}


def main(preview=True, old_keywords=None):
    keywords = None
    if preview:
        print("Устанавливается соединение с сайтами...")
        check_sites_connection(SITES)

    if old_keywords is not None:
        keywords = input(
            f"\nПрошлые ключевые слова: {old_keywords}.\n"
            f"Введите ключевые слова или нажмите 'Enter', чтобы оставить прошлые.\n"
        )
        if keywords == "":
            return seacher.search(old_keywords)

    if not keywords:
        keywords = input(
            "\nВведите через пробел ключевые слова для поиска.\n"
            f'Для поиска двух слов используйте "+". '
            f'Например: "ядерное+оружие"\n'
        )

    keywords = combine_words(keywords)

    return seacher.search(keywords)


def combine_words(words: str):
    result = []

    for word in words.split():
        word = " ".join(word.split("+"))
        result.append(word)

    return result


if __name__ == "__main__":
    key = get_openai_api_key()
    if not key:
        exit()

    main()
