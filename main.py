import asyncio
import requests
import telegram
import time

from environs import Env
from pprint import pprint


async def main():
    url = 'https://dvmn.org/api/long_polling'

    env = Env()
    env.read_env()

    telegram_bot_token = env('TELEGRAM_BOT_TOKEN')
    telegram_bot = telegram.Bot(token=telegram_bot_token)

    telegram_channel_id = env('TELEGRAM_CHANNEL')

    dvmn_token = env('DVMN_TOKEN')
    headers = {'Authorization': f'Token {dvmn_token}'}
    timestamp = ''
    params = {'timestamp': timestamp}

    while True:
        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            task_status_content = response.json()
            if task_status_content['status'] == 'timeout':
                timestamp = task_status_content['timestamp_to_request']
            if not task_status_content['status'] == 'timeout':
                lesson_title = (
                    task_status_content['new_attempts'][0]['lesson_title']
                )
                text = f'У вас проверили работу <<{lesson_title}>>\n'\
                       f'Преподавателю все понарвилось, можно приступить к '\
                       f'следующему уроку!'
                if task_status_content['new_attempts'][0]['is_negative']:
                    text = f'У вас проверили работу <<{lesson_title}>>\n'\
                           f'К сожалению, в работе есть ошибки.'
                async with telegram_bot:
                    await telegram_bot.send_message(
                        chat_id=telegram_channel_id, 
                        text=text
                    )
        except requests.exceptions.ReadTimeout as error:
            pass
        except requests.exceptions.ConnectionError as error:
            print(error)
            time.sleep(180)


if __name__ == '__main__':
    asyncio.run(main())
