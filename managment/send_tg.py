import time

import requests

token = '5503977230:AAGGMyU2e1Tm4MINenX2qfxRCSWvbeEWz90'
channel_id = '@fnsj28tof'
tries = 0


def send_telegram(txt: str):
    url = "https://api.telegram.org/bot"
    url += token
    method = url + "/sendMessage"
    r = requests.post(method, data={
        "chat_id": channel_id,
        "text": txt
    })

    if r.status_code != 200:
        seconds = 40
        while seconds > 0:
            time.sleep(1)
            seconds -= 1
        else:
            time.sleep(1)
            requests.post(method, data={
                "chat_id": channel_id,
                "text": txt
            })


