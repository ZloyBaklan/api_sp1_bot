import logging
import os
import re
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

VERDICT = {
    'rejected': 'К сожалению в работе нашлись ошибки.',
    'approved': 'Ревьюеру всё понравилось,'
                ' можно приступать к следующему уроку.',
    'reviewing': 'Работа в процессе проверки',
}


def parse_homework_status(homework):
    logging.info('Определение этапа проверки')
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    lesson_name = homework.get('lesson_name')
    reviewer_comment = homework.get('reviewer_comment')
    if homework_name is None or homework_status is None:
        logging.error('Проверьте загружена ли домашка')
        return f'Ошибка, {homework_name} не работает правильно или отсутствует'
    if homework_status in VERDICT:
        return (f'Привет, это по поводу твоей работы:\n {lesson_name}\n '
                f'"{homework_name}"!\n\n{VERDICT[homework_status]}\n\n'
                f'Комментарий: {reviewer_comment}')
    logging.warning(f'Неизвестный статус домашки: {homework_status}')
    return f'Ошибка:{homework_status} не опознан(отсутствует вариант вердикта)'


def get_homework_statuses(current_timestamp):
    logging.info('Получение статуса домашки')
    url = YA_API_URL
    headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
    params = {'from_date': current_timestamp}
    try:
        homework_statuses = requests.get(url, params=params, headers=headers)
    except requests.exceptions.RequestException as e:
        '''Цензура на символы в выводе заголовка с ТОКЕНОМ'''
        headers_view = re.compile('(b|1|B|d|C|c|2|4|x|X|3|5|Y|6|7|8|9|p|P)')
        headers = headers_view.sub('*', str(headers))
        logging.error('Ошибка получения статуса домашки'
                      f'с заголовком {headers} и параметрами {params} : {e}')
        return {}
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
            time.sleep(1200)

        except requests.exceptions.RequestException as e:
            logging.error(f'Бот столкнулся с ошибкой запроса: {e}')
            send_message(
                f'Бот столкнулся с ошибкой запроса: {e}', bot
            )


if __name__ == '__main__':
    main()
