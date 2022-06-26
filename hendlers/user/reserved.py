from datetime import timedelta, date, datetime
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from config import dp, bot, BRON_CHANNEL, db
from aiogram import types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ContentType
from filters import IsUser
from app import btnBrn, btnMenu, btnbar, btnTime, btndlv, sos
from aiogram.types import ContentType

b51 = KeyboardButton("❌ НЕТ")
b52 = KeyboardButton("✅ ВЕРНО")
btn_done = "✅ ВЕРНО"
btn_tm = "❌ НЕТ"
otmBtn = ReplyKeyboardMarkup(resize_keyboard=True).add(b52).add(b51)

b53 = "❌ ОТМЕНИТЬ"

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


# def json_serial(obj):
#     """JSON serializer for objects not serializable by default json code"""
#
#     if isinstance(obj):
#         return obj.isoformat()
#     raise TypeError("Type %s not serializable" % type(obj))


def date_day():
    markup = ReplyKeyboardMarkup()
    first_date = date.today() + timedelta(days=1)
    duration = timedelta(days=14)
    for d in range(duration.days + 1):
        day = first_date + timedelta(days=d)
        day_in = day.strftime("%d-%m-%y")
        markup.add(day_in)
    return markup


"""People"""


def people():
    markup = ReplyKeyboardMarkup()
    for i in range(1, 11):
        i = str(i)
        markup.add(i)
    return markup


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
    is_allowed = db.fetchall('SELECT * FROM regime')

    if is_allowed[0][0] == 1:
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row(b53)
        await FSMbron.name.set()
        await message.answer('👤 На чье имя бронируем стол?', reply_markup=markup)
    else:
        await message.answer('Приносим извинения, на данный момент брони не принимаются.')


@dp.message_handler(IsUser(), state=FSMbron.name)
async def load_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if message.text != "❌ ОТМЕНИТЬ":
            data['name'] = message.text
            await FSMbron.next()
            await message.reply('📅 На какую дату?', reply_markup=date_day())
        else:
            markup = ReplyKeyboardMarkup(resize_keyboard=True)
            markup.row(btnMenu, btnbar, btnTime).add(btnBrn, btndlv, sos)
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
        await message.reply('👪 На какое количество гостей?', reply_markup=people())


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
        if message.contact is not None:
            data['phone_number'] = message.contact["phone_number"]
            await FSMbron.next()
            await message.reply(f"Отлично!\n"
                                f"Будем ждать, {data['time']} в {data['people']}\n"
                                f"на имя {data['name']}", reply_markup=otmBtn)


@dp.message_handler(IsUser(), state=FSMbron.phone_number)
async def procces_phone(message: types.Message, state: FSMContext):
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
        markup.row(btnMenu, btnbar, btnTime).add(btnBrn, btndlv, sos)

        await bot.send_message(BRON_CHANNEL, f"Бронь\n"
                                             f"Ф.И.О: {data['name']}\n"
                                             f"Время: {data['people']}\n"
                                             f"Дата: {data['time']}\n"
                                             f"Кол-во гостей: {data['date']}\n"
                                             f"Номер телефона: {data['phone_number']}")
        await message.reply("Бронь принята\n"
                            "Ожидайте подтверждения", reply_markup=markup)
    await state.finish()


@dp.message_handler(IsUser(), text=btn_tm)
async def otm(message: types.Message, state: FSMContext):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(btnMenu, btnbar, btnTime).add(btnBrn, btndlv)
    await bot.send_message(message.from_user.id, "Бронь отменена", reply_markup=markup)
    await state.finish()
