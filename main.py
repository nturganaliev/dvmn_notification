import asyncio
import requests
import telegram

from environs import Env
from pprint import pprint


async def main():
    url = 'https://dvmn.org/api/long_polling'

    env = Env()
    env.read_env()

    token_telegram_bot = env('TOKEN_TELEGRAM_BOT')
    try:
        telegram_bot = telegram.Bot(token=token_telegram_bot)
    
    telegram_channel_id = env('TELEGRAM_CHANNEL')

    token_dvmn = env('TOKEN_DVMN')
    headers = {'Authorization': f'Token {token_dvmn}'}

    while True:
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            content = response.json()
            if content['status'] == 'timeout':
                timestamp = content['timestamp_to_request']
                params = {'timestamp': timestamp}
                response = requests.get(
                   url, params=params, headers=headers
                )
                content = response.json()
            if not content['status'] == 'timeout':
                lesson_title = content['new_attempts'][0]['lesson_title']
                text = f'У вас проверили работу <<{lesson_title}>>\n'\
                       f'Преподавателю все понарвилось, можно приступить к '\
                       f'следующему уроку!'
                if content['new_attempts'][0]['is_negative']:
                    text = f'У вас проверили работу <<{lesson_title}>>\n'\
                           f'К сожалению, в работе есть ошибки.'
                async with telegram_bot:
                    await telegram_bot.send_message(
                        chat_id=telegram_channel_id, 
                        text=text
                    )
        except requests.exceptions.ReadTimeout as error:
            print(error)
        except requests.exceptions.ConnectionError as error:
            print(error)
        except telegram.error.BadRequest as bad_request:
            print(bad_request)
        except telegram.error.Unauthorized as unauthorized:
            print(f"{unauthorized}, check your TELEGRAM_BOT_TOKEN")


if __name__ == '__main__':
    asyncio.run(main())
