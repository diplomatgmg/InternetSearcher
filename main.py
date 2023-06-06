import os

import seacher


def clear_screen():
    os.system("cls")


def get_sites_list():
    return f"Здесь пока пусто\n"


def main(preview=True, old_keywords=None):
    keywords = None

    if preview:
        sites_list = get_sites_list()
        print(f"Список сайтов:\n" f"{sites_list}")

        clear_screen()

    if old_keywords is not None:
        keywords = input(
            f"Прошлые ключевые слова: {old_keywords}.\n"
            f"Введите ключевые слова или нажмите Enter, чтобы оставить прошлые.\n"
        )
        if keywords == '':
            return seacher.search(old_keywords)

    if not keywords:
        keywords = input("Введите через пробел ключевые слова для поиска:\n")

    keywords = "".join(
        letter.lower() for letter in keywords if letter.isalpha() or letter.isspace()
    ).split()

    return seacher.search(keywords)


if __name__ == "__main__":
    main()
