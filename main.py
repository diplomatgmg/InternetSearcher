import os

import seacher


def clear_screen():
    os.system("cls")


def get_sites_list():
    return f"Здесь пока пусто\n"


def main(preview=True):
    if preview:
        sites_list = get_sites_list()
        print(f"Список сайтов:\n" f"{sites_list}")

        clear_screen()

    keywords = input("Введите через пробел ключевые слова для поиска:\n")

    keywords = "".join(
        letter.lower() for letter in keywords if letter.isalpha() or letter.isspace()
    ).split()

    seacher.search(keywords)


if __name__ == "__main__":
    main()
