import logging
import os
import time

import requests
import telegram
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    filename='main.log',
    format='%(asctime)s, %(levelname)s, %(name)s,'
           ' (%(filename)s).%(funcName)s(%(lineno)d), %(message)s'
)
logger = logging.getLogger('__name__')
load_dotenv()
PRAKTIKUM_TOKEN = os.getenv("PRAKTIKUM_TOKEN")
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
YA_API_URL = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'

STATUSES = {
        'rejected': 'К сожалению в работе нашлись ошибки.',
        'approved': 'Ревьюеру всё понравилось,'
                     ' можно приступать к следующему уроку.',
        'reviewing': 'Работа в процессе проверки',
}

def parse_homework_status(homework):
    logging.info('Определение этапа проверки')
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    homework_verdict = homework.get('verdict')
    if homework_name is None or homework_status is None:
        logging.error('Проверьте загружена ли домашка')
        return f'Ошибка, {homework_name} не работает правильно или отсутствует'
    for status, verdict in STATUSES.items():
        if homework_status == status:
            return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'
        elif verdict is None:
            logging.warning(f'Неизвестный статус домашки: {homework_status}')
            return f'Ошибка: {homework_status} не сопоставим с {verdict}'


def get_homework_statuses(current_timestamp):
    logging.info('Получение статуса домашки')
    url = YA_API_URL
    headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
    params = {'from_date': current_timestamp}
    try:
        homework_statuses = requests.get(url, params=params, headers=headers)
    except requests.exceptions.RequestException as e:
        logging.error('Ошибка получения статуса домашки'
                      f'с заголовком {headers} и параметрами {params} : {e}')
    return homework_statuses.json()


def send_message(message, bot_client):
    logging.info('Отправка сообщения ботом')
    return bot_client.send_message(chat_id=CHAT_ID, text=message)


def main():
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(
                    parse_homework_status(new_homework['homeworks'][0]), bot
                )
            current_timestamp = new_homework.get('current_date',
                                                 current_timestamp)
            time.sleep(300)

        except requests.exceptions.RequestException as e:
            logging.error(f'Бот столкнулся с ошибкой запроса: {e}')
            send_message(
                f'Бот столкнулся с ошибкой запроса: {e}', bot
                )


if __name__ == '__main__':
    main()
