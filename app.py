import logging
from config import dp, db, loop
import hendlers
from aiogram import executor
from aiogram import types
from aiogram.types import ReplyKeyboardMarkup
import filters
from filters import IsUser, IsAdmin
from aiogram.dispatcher import FSMContext

filters.setup(dp)

cart = '🛒 Перейти в Корзину'
balance = '💰 Баланс'
settings = '⚙️ Настройка каталога'
questions = '❓ Вопросы'
add_product = '➕ Добавить товар'
delete_product = '🗑️ Удалить товар'
btnMenu = "📖 МЕНЮ"
btnBrn = "📞 ЗАБРОНИРОВАТЬ"
btnTime = "🕗 РЕЖИМ РАБОТЫ"
btnbar = "🍾 БАР"
btndlv = "🎒 ДОСТАВКА"
orders = '🚚 Заказы'
sos = "? ПОМОЩЬ"


@dp.message_handler(IsUser(), commands="start", state="*")
async def cmd_start(message: types.Message, state: FSMContext):
    await state.finish()
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(btnMenu, btnbar, btnTime).add(btnBrn, btndlv, sos)
    await message.answer('ДОБРО ПОЖАЛОВАТЬ, {0.first_name}\n'
                         'Я Ваш личный бот, помощник.\n'
                         'Я помогу Вам ознакомиться с меню, режимом работы ресторана и '
                         'забронировать стол.'.format(
        message.from_user), reply_markup=markup)


@dp.message_handler(IsAdmin(), commands="start")
async def cmd_start(message: types.Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(settings)
    await message.answer('''ВКЛЮЧЕН РЕЖИМ АДМИНИСТРАТОРА''', reply_markup=markup)


async def on_startup(dp):
    logging.basicConfig(level=logging.INFO)
    db.create_tables()


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=False, on_startup=on_startup, loop=loop)
