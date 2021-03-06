import os
import time

import requests
import telegram
from dotenv import load_dotenv
import logging

logging.basicConfig(
    level=logging.INFO,
    filename='main.log',
    format='%(asctime)s, %(levelname)s, %(name)s, %(message)s'
)
logger = logging.getLogger('__name__')
logging.debug('Отладочная информация')
logging.info('Дополнительная информация')
logging.warning('Работает, но что-то не так')
logging.error('Ошибка')
logging.critical('Критическая ошибка')

load_dotenv()


PRAKTIKUM_TOKEN = os.getenv("PRAKTIKUM_TOKEN")
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')


def parse_homework_status(homework):
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    if homework_status == 'rejected':
        verdict = 'К сожалению в работе нашлись ошибки.'
    elif homework_status == 'approved':
        verdict = 'Ревьюеру всё понравилось, можно приступать к следующему ' \
                  'уроку.'
    elif homework_status == 'reviewing':
        verdict = 'Работа в процессе проверки'
    elif homework_name is None or homework_status is None:
        logging.error('Проверьте загружена ли домашка')
        return f'Ошибка, {homework_name} не работает правильно или отсутствует'
    else:
        verdict = ''
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    url = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
    headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
    params = {'from_date': current_timestamp}
    homework_statuses = requests.get(url, params=params, headers=headers)
    return homework_statuses.json()


def send_message(message, bot_client):
    bot_client = telegram.Bot(token=TELEGRAM_TOKEN)
    return bot_client.send_message(chat_id=CHAT_ID, text=message)


def main():
    current_timestamp = int(time.time())

    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(
                    parse_homework_status(new_homework.get('homeworks')[0])
                )
            current_timestamp = new_homework.get('current_date',
                                                 current_timestamp)
            time.sleep(300)

        except Exception as e:
            print(f'Бот столкнулся с ошибкой: {e}')
            time.sleep(5)


if __name__ == '__main__':
    main()
