from config import dp, bot
from aiogram import types
from filters import IsUser
from app import btnTime


@dp.message_handler(IsUser(), text=btnTime)
async def time(message: types.Message):
    await message.answer("Адрес:\n"
                         "Держинского 6 Б\n"
                         "\n"
                         "☎️ 2661111\n"
                         "\n"
                         "Ромэйн Meat\n"
                         "Дзержинского, 6Б, Казань\n"
                         "+7 (843) 266‒11‒11\n")
    await bot.send_location(message.from_user.id, latitude=55.79548980051069, longitude=49.11299946446939)
