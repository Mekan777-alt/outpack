import asyncio
import os
from aiogram import Dispatcher, Bot, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from data.database import Database

loop = asyncio.get_event_loop()
ADMINS = []#[5443287345]#[337708421]
TOKEN = "5286546614:AAEGjGi5elS1quZcfopurzE2-gYPYisubf4"
TOKEN_PAYMENTS = "401643678:TEST:ea70bc5e-ba80-4990-89ab-c097e808da98"
DELIVERY_CHAT = "-661196706"
SUPPORT_CHAT = "-760076942"
BRON_CHANNEL = "-1001774409771"

storage = MemoryStorage()

path = os.getcwd() + "/data/database.db"

try:
    from local_config import *
except ImportError:
    pass


bot = Bot(token=TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=storage, loop=loop)
db = Database(path)
