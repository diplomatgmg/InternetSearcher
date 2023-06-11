import logging

import seacher


def start_with_logger(parser_class, keywords: list, time_interval: int):
    try:
        parser_class(keywords, time_interval).start()
    except:
        print(
            f"Ошибка при работе с [{parser_class.__class__.__name__}]. "
            f"Логи сохранены в файл под названием errors.log",
        )
        logging.basicConfig(
            level=logging.ERROR,
            filename=f"errors.log",
            filemode="w",
            format="%(asctime)s %(levelname)s %(message)s",
        )

        logging.error(
            f"Ошибка при работе с [{parser_class.__class__.__name__}]. Keywords: {seacher.global_keywords}",
            exc_info=True,
        )





