from datetime import timedelta, date
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from config import dp, bot
from aiogram import types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ContentType
from filters import IsUser
from app import btnBrn, btnMenu, btnbar, btnTime, btnkor

BRON_CHANNEL = "@main_channel2"
b51 = KeyboardButton("❌ НЕТ")
b52 = KeyboardButton("✅ ВЕРНО")
btn_done = "✅ ВЕРНО"
btn_tm = "❌ НЕТ"
otmBtn = ReplyKeyboardMarkup(resize_keyboard=True).add(b52).add(b51)

b53 = "❌ ОТМЕНИТЬ"
today = date.today()
"""Bron stolov"""
b1 = KeyboardButton("10:00")
b2 = KeyboardButton("10:30")
b3 = KeyboardButton("11:00")
b4 = KeyboardButton("11:30")
b5 = KeyboardButton("12:00")
b6 = KeyboardButton("12:30")
b7 = KeyboardButton("13:00")
b8 = KeyboardButton("13:30")
b9 = KeyboardButton("14:00")
b10 = KeyboardButton("14:30")
b11 = KeyboardButton("15:00")
b12 = KeyboardButton("15:30")
b13 = KeyboardButton("16:00")
b14 = KeyboardButton("16:30")
b15 = KeyboardButton("17:00")
b16 = KeyboardButton("17:30")
b17 = KeyboardButton("18:00")
b18 = KeyboardButton("18:30")
b19 = KeyboardButton("19:00")
b20 = KeyboardButton("19:30")
b21 = KeyboardButton("20:00")
b22 = KeyboardButton("20:30")
b23 = KeyboardButton("21:00")
b24 = KeyboardButton("21:30")
b25 = KeyboardButton("22:00")
timeBtn = ReplyKeyboardMarkup().add(b1).add(b2).add(b3).add(b4).add(b5).add(b6).add(b7).add(b8).add(b9).add(b10)
timeBtn.add(b11).add(b12).add(b13).add(b14).add(b15).add(b16).add(b17).add(b18).add(b19).add(b20).add(b21) \
    .add(b22).add(b23).add(b24).add(b25)
"""date button"""
b26 = KeyboardButton(f"{today + timedelta(days=0)}")
b27 = KeyboardButton(f"{today + timedelta(days=1)}")
b28 = KeyboardButton(f"{today + timedelta(days=2)}")
b29 = KeyboardButton(f"{today + timedelta(days=3)}")
b30 = KeyboardButton(f"{today + timedelta(days=4)}")
b31 = KeyboardButton(f"{today + timedelta(days=5)}")
b32 = KeyboardButton(f"{today + timedelta(days=6)}")
b33 = KeyboardButton(f"{today + timedelta(days=7)}")
b34 = KeyboardButton(f"{today + timedelta(days=8)}")
b35 = KeyboardButton(f"{today + timedelta(days=9)}")
b36 = KeyboardButton(f"{today + timedelta(days=10)}")
b37 = KeyboardButton(f"{today + timedelta(days=11)}")
b38 = KeyboardButton(f"{today + timedelta(days=12)}")
b39 = KeyboardButton(f"{today + timedelta(days=13)}")
b40 = KeyboardButton(f"{today + timedelta(days=14)}")
dataBtn = ReplyKeyboardMarkup().add(b26).add(b27).add(b28).add(b29).add(b30).add(b31).add(b32).add(b33).add(b34).add(
    b35)
dataBtn.add(b36).add(b37).add(b38).add(b39).add(b40)
"""People"""
b41 = KeyboardButton("1")
b42 = KeyboardButton("2")
b43 = KeyboardButton("3")
b44 = KeyboardButton("4")
b45 = KeyboardButton("5")
b46 = KeyboardButton("6")
b47 = KeyboardButton("7")
b48 = KeyboardButton("8")
b49 = KeyboardButton("9")
b50 = KeyboardButton("10")
pepBtn = ReplyKeyboardMarkup().add(b41).add(b42).add(b43).add(b44).add(b45).add(b46).add(b47).add(b48).add(b49).add(b50)
b54 = KeyboardButton("📞 Отправить свой номер", request_contact=True)
send_phone = ReplyKeyboardMarkup(resize_keyboard=True).add(b54)


class FSMbron(StatesGroup):
    name = State()
    time = State()
    date = State()
    people = State()
    phone_number = State()


@dp.message_handler(IsUser(), text=btnBrn, state=None)
async def cmd_start(message: types.Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(b53)
    await FSMbron.name.set()
    await message.answer('👤 На чье имя бронируем стол?', reply_markup=markup)


@dp.message_handler(IsUser(), state=FSMbron.name)
async def load_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if message.text != "❌ ОТМЕНИТЬ":
            data['name'] = message.text
            await FSMbron.next()
            await message.reply('📅 На какую дату?', reply_markup=dataBtn)
        else:
            markup = ReplyKeyboardMarkup(resize_keyboard=True)
            markup.row(btnMenu, btnbar, btnTime).add(btnBrn, btnkor)
            await bot.send_message(message.from_user.id, "ПЕРЕХОД НА ГЛАВНОЕ МЕНЮ", reply_markup=markup)
            await state.finish()


@dp.message_handler(IsUser(), state=FSMbron.date)
async def load_date(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['date'] = message.text
        await FSMbron.next()
        await message.reply('🕗 Выберите время бронирования: ', reply_markup=timeBtn)


@dp.message_handler(IsUser(), state=FSMbron.time)
async def load_time(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['time'] = message.text
        await FSMbron.next()
        await message.reply('👪 На какое количество гостей?', reply_markup=pepBtn)


@dp.message_handler(IsUser(), state=FSMbron.people)
async def load_people(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['people'] = message.text
        await FSMbron.next()
        await message.reply('Введите номер телефона пожалуйста.\n'
                            'Хостес перезвонит Вам для подтверждения брони.', reply_markup=send_phone)


@dp.message_handler(IsUser(), content_types=ContentType.CONTACT, state=FSMbron.phone_number)
async def load_phone_number(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['phone_number'] = message.contact["phone_number"]
        await FSMbron.next()
        await message.reply(f"Отлично!\n"
                                f"Будем ждать, {data['time']} в {data['people']}\n"
                                f"на имя {data['name']}", reply_markup=otmBtn)


@dp.message_handler(IsUser(), state=FSMbron.phone_number)
async def load_phone(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['phone_number'] = message.text
        await FSMbron.next()
        await message.reply(f"Отлично!\n"
                            f"Будем ждать, {data['time']} в {data['people']}\n"
                            f"на имя {data['name']}", reply_markup=otmBtn)


@dp.message_handler(IsUser(), text=btn_done)
async def cencel_message(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row(btnMenu, btnbar, btnTime).add(btnBrn, btnkor)
        await message.reply("Бронь принята\n"
                            "Ожидайте подтверждения", reply_markup=markup)
        await bot.send_message(BRON_CHANNEL, f"Бронь\n"
                                             f"Ф.И.О: {data['name']}\n"
                                             f"Время: {data['people']}\n"
                                             f"Дата: {data['time']}\n"
                                             f"Кол-во гостей: {data['date']}\n"
                                             f"Номер телефона: {data['phone_number']}")
    await state.finish()


@dp.message_handler(IsUser(), text=btn_tm)
async def otm(message: types.Message, state: FSMContext):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(btnMenu, btnbar, btnTime).add(btnBrn, btnkor)
    await bot.send_message(message.from_user.id, "Бронь отменена", reply_markup=markup)
    await state.finish()
