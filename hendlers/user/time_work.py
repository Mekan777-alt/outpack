from config import dp, bot
from aiogram import types
from filters import IsUser
from app import btnTime, btnBrn, btndlv, btnbar, btnMenu, sos
from aiogram.types import ReplyKeyboardMarkup


@dp.message_handler(IsUser(), text=btnTime)
async def time(message: types.Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(btnMenu, btnbar, btnTime)
    markup.add(btnBrn, btndlv, sos)
    await message.answer("Общество с ограниченной ответственностью\n"
                         "ООО «ДИВИНУМ»\n"
                         "Контакты:\n"
                         "Фактический адрес:\n"
                         "420111 , РТ ,г.Казань , ул.Дзержинского  , здание 6Б, помещение 1027\n"
                         "Электронная почта: olga310374@mail.ru\n"
                         "Телефон: (843) 266-11-11\n"
                         "Реквизиты:\n"
                         "ОГРН 1201600009005\n"
                         "ИНН 1655432684\n"
                         "КПП 165501001\n"
                         "Юридический адрес:\n"
                         "420111 , РТ ,г.Казань , ул.Дзержинского , здание 6Б, помещение 1027",
                         reply_markup=markup)
    await message.answer("Адрес:\n"
                         "Держинского 6 Б\n"
                         "\n"
                         "☎️ 2661111\n"
                         "\n"
                         "Ромэйн Meat\n"
                         "Дзержинского, 6Б, Казань\n"
                         "+7 (843) 266‒11‒11\n")
    await bot.send_location(message.from_user.id, latitude=55.79548980051069, longitude=49.11299946446939)
