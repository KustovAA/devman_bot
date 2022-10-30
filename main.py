import logging
import time

from environs import Env
import requests
import telegram

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    env = Env()
    env.read_env()

    tg_bot_token = env.str('TG_BOT_TOKEN')
    logging.info('env variable TG_BOT_TOKEN has bean read')
    tg_chat_id = env.int('TG_USER_CHAT_ID')
    logging.info('env variable TG_USER_CHAT_ID has bean read')
    access_token = env.str('DEVMAN_ACCESS_TOKEN')
    logging.info('env variable DEVMAN_ACCESS_TOKEN has bean read')

    bot = telegram.Bot(token=tg_bot_token)

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

            bot.send_message(
                chat_id=tg_chat_id,
                text=f'У вас проверили работу "{lesson_title}"\n\n{verdict}'
            )
        elif review['status'] == 'timeout':
            timestamp_to_request = review['timestamp_to_request']
            params['timestamp'] = timestamp_to_request
        else:
            params = {}

