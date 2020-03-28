import os
import time

from dotenv import load_dotenv
import requests
import telegram


load_dotenv()
PRAKTIKUM_TOKEN = os.getenv("PRAKTIKUM_TOKEN")
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
bot = telegram.Bot(token=TELEGRAM_TOKEN)


def parse_homework_status(homework):
    homework_name = homework['homework_name']
    if homework['status'] == 'rejected':
        verdict = 'К сожалению, в работе нашлись ошибки.'
    else:
        verdict = 'Ревьюеру всё понравилось, можно приступать к следующему уроку.'
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    url = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
    headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
    params = {
        'from_date': 0,
    }
    try:
        homework_statuses = requests.get(
            url, timeout=30, params=params, headers=headers)
        homework_statuses.raise_for_status()
        return homework_statuses.json()
    except requests.HTTPError as err:
        code = err.response.status_code
        print(f'Ошибка: {code}')
    except requests.Timeout:
        print('Ошибка: Timeout')
    except requests.RequestException:
        print(f'Запрос не удался по адресу: {url}')
    return {}


def send_message(message):
    return bot.send_message(chat_id=CHAT_ID, text=message)


def main():
    current_timestamp = int(time.time())  # начальное значение timestamp
    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            homeworks = new_homework.get('homeworks', [])
            if homeworks:
                send_message(parse_homework_status(homeworks[0]))
            current_timestamp = new_homework.get(
                'current_date', int(time.time()))  # обновить timestamp
            time.sleep(1200)  # опрашивать раз в 20 минут
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f'Бот упал с ошибкой: {e}')
            time.sleep(5)


if __name__ == '__main__':
    main()
