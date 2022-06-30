from config import dp, bot
from aiogram import types
from filters import IsUser
from app import btnTime


@dp.message_handler(IsUser(), text=btnTime)
async def time(message: types.Message):
    await message.answer("Ромэйн Meat\n"
                         "\n"
                         "Режим работы:\n" 
                         "ПН-ВС\n" 
                         "С 11:00 до 00:00\n"
                         "\n"
                         "Адрес: Дзержинского, 6 Б\n"
                         "\n"
                         "☎️ Тел:  +7 (843) 266-11-11\n")
    await bot.send_location(message.from_user.id, latitude=55.79548980051069, longitude=49.11299946446939)
