import logging
import time

from environs import Env
import requests
import telegram


class LogsHandler(logging.Handler):
    def __init__(self):
        super().__init__()

        env = Env()
        env.read_env()
        tg_bot_token = env.str('TG_BOT_TOKEN')
        tg_chat_id = env.int('TG_USER_CHAT_ID')
        self.bot = telegram.Bot(token=tg_bot_token)
        self.chat_id = tg_chat_id

    def emit(self, record):
        log_entry = self.format(record)

        self.bot.send_message(
            chat_id=self.chat_id,
            text=log_entry
        )

        return log_entry


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger('devman-bot')
    logger.setLevel(logging.INFO)
    logger.addHandler(LogsHandler())

    env = Env()
    env.read_env()

    access_token = env.str('DEVMAN_ACCESS_TOKEN')
    logger.info('env variable DEVMAN_ACCESS_TOKEN has bean read')

    headers = {'Authorization': f'Token {access_token}'}
    params = {}

    while True:
        try:
            response = requests.get('https://dvmn.org/api/long_polling/', headers=headers, params=params)
            response.raise_for_status()
        except requests.exceptions.ReadTimeout:
            continue
        except requests.exceptions.ConnectionError:
            time.sleep(1)
            continue

        review = response.json()

        if review['status'] == 'found':
            last_attempt_timestamp = review['last_attempt_timestamp']
            params['timestamp'] = last_attempt_timestamp
            attempt = review['new_attempts'][0]
            lesson_title = attempt['lesson_title']
            is_negative = attempt['is_negative']
            if is_negative:
                verdict = 'К сожалению в работе нашлись ошибки'
            else:
                verdict = 'Преподавателю все понравилось, можно приступать в слелующему уроку!'

            logger.info(f'У вас проверили работу "{lesson_title}"\n\n{verdict}')
        elif review['status'] == 'timeout':
            timestamp_to_request = review['timestamp_to_request']
            params['timestamp'] = timestamp_to_request
        else:
            params = {}

