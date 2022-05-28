import asyncio
from aiogram import Dispatcher, Bot, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from data.database import Database

loop = asyncio.get_event_loop()
ADMINS = []#[337708421]#, 664265553]
TOKEN = "5333099893:AAEuHBJ3W5iq4X4oth-EyFfjpa8TM-iaKBo"
storage = MemoryStorage()
bot = Bot(token=TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=storage, loop=loop)
db = Database('/Users/mekanmededov/Desktop/outpack_telebot/data/database.db')

