import requests
import time
import os


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


def check_token():
    global tries, channel_id, token
    if tries == 0:
        try:
            with open('config_eng', 'r', encoding='utf-8') as file:
                file = file.readline().split(';')
                token = file[0].strip()
                channel_id = file[1].strip()
                tries = 1
        except:
            os.system('cls')

            while True:
                print(
                    '\nВы должны добавить API токен для вашего бота! '
                    'Не забудьте добавить его в администраторы канала!\n')
                token_write = input('Введите токен:\n')
                token_check = token_write.split(':')
                try:
                    if 7 < len(token_check[0]) < 13:
                        if 28 < len(token_check[1]) < 42:
                            break
                        else:
                            os.system('cls')
                            print('\nПроверьте корректность введенного токена!')
                    else:
                        os.system('cls')
                        print('\nПроверьте корректность введенного токена!')
                except:
                    os.system('cls')
                    print('\nПроверьте корректность введенного токена!')
            os.system('cls')

            while True:
                print('\nВы должны добавить ссылку на Ваш канал, куда будут приходить посты!')
                channel_write = input('\nСсылку на Ваш канал. Пример: https://t.me/example\n')
                if 'https://t.me/' in channel_write:
                    channel_write = '@' + channel_write.split('/')[-1]
                    break
                else:
                    os.system('cls')
                    print('\nПроверьте корректность Вашего канала!')
            with open('config_eng', 'w', encoding='utf-8') as file:
                file.write(f'{token_write};{channel_write}')
            tries = 1
            os.system('cls')
            input('\nПерезапустите программу!')
            exit()
