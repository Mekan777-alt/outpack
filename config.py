import asyncio
import os
from aiogram import Dispatcher, Bot, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from data.database import Database

loop = asyncio.get_event_loop()
ADMINS = []#[5443287345]#[337708421]
TOKEN = "5153177753:AAGN27mmyBzn_nDbc3Wqx7TJwYIG2UQdBMs"
TOKEN_PAYMENTS = "401643678:TEST:2a495ef0-26a1-4053-b3d5-c149e1f682ce"
BRON_CHANNEL = "@main_test12"
storage = MemoryStorage()
bot = Bot(token=TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=storage, loop=loop)
db = Database(os.getcwd() + "\\data\\database.db")

try:
    from local_config import *
except ImportError:
    pass
