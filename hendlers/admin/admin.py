from aiogram.types import ReplyKeyboardMarkup
from app import settings_regime, start_stop
from config import dp
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

login = 'romein'
password = '123'


class Admin(StatesGroup):
    login = State()
    password = State()


@dp.message_handler(commands='admin', state=None)
async def commands_admin(message: types.Message):
    await Admin.login.set()
    await message.answer("Логин:")


@dp.message_handler(text=login, state=Admin.login)
async def check_login(message: types.Message, state: FSMContext):
    if message.text in login:
        await Admin.next()
        await message.answer("Пароль:")


@dp.message_handler(lambda message: message.text is not login, state=Admin.login)
async def log_pass_invalid(message: types.Message):
    await message.answer("Неверный логин")


@dp.message_handler(text=password, state=Admin.password)
async def check_password(message: types.Message, state: FSMContext):
    if message.text in password:
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(settings_regime)
        # markup.add(settings_catalogue)
        markup.add(start_stop)
        await message.answer('''ВКЛЮЧЕН РЕЖИМ АДМИНИСТРАТОРА''', reply_markup=markup)
    await state.finish()


@dp.message_handler(lambda message: message.text is not password, state=Admin.password)
async def log_pass_invalid(message: types.Message):
    await message.answer("Неверный пароль")
