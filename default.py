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


translator = Translator()
color = Color().color
