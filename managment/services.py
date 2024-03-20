import time
from threading import Thread

from googletrans import Translator


def check_sites_connection(sites):
    threads = []
    for site in sites:
        obj = Thread(target=site.check_connection, kwargs={"printable": True})
        obj.start()
        threads.append(obj)

    for thread in threads:
        thread.join()


def bad_request_message(name_site):
    print(name_site, "- Потеряно соединение.")


def good_request_message(name_site):
    print(name_site, "- Соединение установлено.")


class Trans(Translator):
    def translate(self, *args, **kwargs):
        retries = 0
        while True:
            try:
                return super().translate(*args, **kwargs)
            except:
                if retries == 10:
                    input(
                        "Возникла ошибка при переводе...\n",
                    )

                retries += 1
                time.sleep(retries)


translator = Trans()
