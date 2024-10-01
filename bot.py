import logging
import requests
import os
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)

API_TOKEN = os.getenv('TELEGRAM_BOT_API_TOKEN')
CURRENCY_API_URL = os.getenv('CURRENCY_API_URL')
CURRENCY_API_KEY = os.getenv('CURRENCY_API_KEY')

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

def get_usd_rate():
    try:
        params = {
            'access_key': CURRENCY_API_KEY,
            'currencies': 'RUB',
            'source': 'USD',
            'format': 1
        }
        response = requests.get(CURRENCY_API_URL, params=params)
        data = response.json()

        if data.get('success', False) and 'quotes' in data:
            return data['quotes']['USDRUB']
        else:
            logging.error(f"Unexpected API response: {data}")
            return None
    except requests.RequestException as e:
        logging.error(f"Error fetching exchange rate: {e}")
        return None

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Добрый день. Как вас зовут?")

@dp.message_handler(lambda message: not message.text.startswith('/'))
async def handle_name(message: types.Message):
    name = message.text
    usd_rate = get_usd_rate()

    if usd_rate is not None:
        response = f'Рад знакомству, {name}! Курс доллара сегодня {usd_rate:.2f} руб.'
    else:
        response = f'Рад знакомству, {name}, но не удалось получить курс доллара.'

    await message.reply(response)

@dp.errors_handler()
async def error_handler(update, error):
    logging.exception(f"An error occurred: {error}")
    return True

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)