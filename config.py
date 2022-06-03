import asyncio
from aiogram import Dispatcher, Bot, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from data.database import Database

loop = asyncio.get_event_loop()
ADMINS = []#[5443287345]#[337708421]
TOKEN = ""
TOKEN_PAYMENTS = ""
BRON_CHANNEL = ""
storage = MemoryStorage()
bot = Bot(token=TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=storage, loop=loop)
db = Database('/Users/mekanmededov/Desktop/outpack_telebot/data/database.db')

