import logging
import time

from environs import Env
import requests
import telegram


class LogsHandler(logging.Handler):
    def __init__(self, token, chat_id):
        super().__init__()
        self.bot = telegram.Bot(token=token)
        self.chat_id = chat_id

    def emit(self, record):
        log_entry = self.format(record)

        self.bot.send_message(
            chat_id=self.chat_id,
            text=log_entry
        )

        return log_entry


if __name__ == '__main__':
    env = Env()
    env.read_env()

    tg_bot_token = env.str('TG_BOT_TOKEN')
    tg_chat_id = env.int('TG_USER_CHAT_ID')
    access_token = env.str('DEVMAN_ACCESS_TOKEN')

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger('devman-bot')
    logger.setLevel(logging.INFO)
    logger.addHandler(LogsHandler(tg_bot_token, tg_chat_id))

    logger.info('bot restarted')

    headers = {'Authorization': f'Token {access_token}'}
    params = {}

    while True:
        try:
            0 / 0
            try:
                response = requests.get('https://dvmn.org/api/long_polling/', headers=headers, params=params)
                response.raise_for_status()
            except requests.exceptions.ReadTimeout as err:
                logger.exception(err, exc_info=True)
                continue
            except requests.exceptions.ConnectionError as err:
                logger.error(err, exc_info=True)
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
        except Exception as err:
            logger.exception(err, exc_info=True)
