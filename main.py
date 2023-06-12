from managment import seacher
from managment import settings
from managment.openai_gpt import get_openai_api_key
from managment.services import check_sites_connection
from sites.all_sites import SITES


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
    is_test = settings.is_test
    if is_test:
        print('Включен режим отладки\n')

    key = get_openai_api_key(settings.is_test)
    if not key:
        exit()

    main()
