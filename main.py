import logging
import requests
import telegram
import time

from environs import Env


class TelegramLogsHandler(logging.Handler):

    def __init__(self, tg_bot, chat_id):
        super().__init__()
        self.chat_id = chat_id
        self.tg_bot = tg_bot

    def emit(self, record):
        log_entry = self.format(record)
        self.tg_bot.send_message(self.chat_id, text=log_entry)


def send_request_to_dvmn(dvmn_token, timestamp):
    url = 'https://dvmn.org/api/long_polling'
    headers = {'Authorization': f'Token {dvmn_token}'}
    params = {'timestamp': timestamp}
    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()
    return response.json()


def main():

    env = Env()
    env.read_env()

    timestamp = ''
    dvmn_token = env('DVMN_TOKEN')

    telegram_bot_token = env('TELEGRAM_BOT_TOKEN')
    telegram_bot = telegram.Bot(token=telegram_bot_token)
    telegram_channel_id = env('TELEGRAM_CHANNEL')

    logging.basicConfig(format="%(process)d %(levelname)s %(message)s")
    logger = logging.getLogger('Logger')
    logger.setLevel(logging.INFO)
    logger.addHandler(TelegramLogsHandler(telegram_bot, telegram_channel_id))

    logger.info('Bot is started...')
    while True:
        try:
            task_status_content = send_request_to_dvmn(dvmn_token, timestamp)
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
                telegram_bot.send_message(
                    chat_id=telegram_channel_id,
                    text=text
                )
        except requests.exceptions.ReadTimeout:
            pass
        except requests.exceptions.ConnectionError as error:
            logger.error(error)
            time.sleep(180)


if __name__ == '__main__':
    main()
