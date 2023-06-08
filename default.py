import time

import httpcore
from googletrans import Translator


class Color:
    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    ORANGE = "\033[94m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    RESET = "\033[0m"

    def color(self, message, *colours):
        result = ""

        for colour in colours:
            result += getattr(self, colour.upper())

        return f"{result}{message}{self.RESET}"


def check_sites_connection(sites):
    for site in sites:
        site.check_connection(printable=True)


def bad_request_message(name_site):
    print(
        color(name_site, "red", "bold"),
        color("- Потеряно соединение. Обратитесь к программисту.", "green"),
    )


def good_request_message(name_site):
    print(
        color(name_site, "purple", "bold"),
        color("- Соединение установлено.", "green"),
    )


class Trans(Translator):
    def translate(self, *args, **kwargs):
        retries = 0
        while True:
            try:
                return super().translate(*args, **kwargs)
            except httpcore.ReadError:
                if retries == 10:
                    input(
                        color(
                            "Возникла ошибка при переводе. Для выхода нажмите Enter.",
                            "red",
                        )
                    )
                    raise httpcore.ReadError("Возникла ошибка при переводе.")

                retries += 1
                time.sleep(2)


translator = Trans()

color = Color().color
