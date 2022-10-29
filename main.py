from environs import Env
import requests

import telegram

if __name__ == '__main__':
    env = Env()
    env.read_env()

    tg_bot_token = env.str('TG_BOT_TOKEN')
    tg_chat_id = env.int('TG_USER_CHAT_ID')
    access_token = env.str('DEVMAN_ACCESS_TOKEN')

    bot = telegram.Bot(token=tg_bot_token)

    headers = {'Authorization': f'Token {access_token}'}
    params = {}

    while True:
        try:
            response = requests.get('https://dvmn.org/api/long_polling/', headers=headers, params=params)
            response.raise_for_status()
        except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError):
            continue

        data = response.json()

        if data['status'] == 'found':
            last_attempt_timestamp = data['last_attempt_timestamp']
            params['timestamp'] = last_attempt_timestamp
            attempt = data['new_attempts'][0]
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
        elif data['status'] == 'timeout':
            timestamp_to_request = data['timestamp_to_request']
            params['timestamp'] = timestamp_to_request
        else:
            params = {}

