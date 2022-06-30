from aiogram.utils.callback_data import CallbackData
from config import bot, dp, db
from filters import IsUser
from app import btndlv, cart
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, ChatActions
from hendlers.user.catalog import btnnaz
from aiogram.dispatcher import FSMContext
from datetime import datetime

btn_instr = "⚙️ ИНСТРУКЦИЯ"
pay = "💳 СПОСОБ ОПЛАТЫ"

projarkas = {"blue_rare": "Blue rare", "medium_rare": "Medium rare", "medium": "Medium", "medium_well": "Medium well", "well_done": "Well done"}
garnishs = {"pure": "Картофельное пюре", "free": "Картофель фри", "dolki": "Картофельные дольки", "kuku": "Початок кукурузы (150 гр.)", "salat": "Свежий салатик (150 гр.)"}
sauces = {"blu": "Соус блю чиз", "nacos": "Соус начос", "chili": "Сладкий чили", "bbq": "Соус BBQ", "meks": "Мексиканская сальса"}


kryl_cb = CallbackData('product', 'id', 'action')


def spice_markup(idx):
    markup = InlineKeyboardMarkup()
    not_spicy = InlineKeyboardButton('Не острые', callback_data=kryl_cb.new(id=idx, action='not_spicy'))
    medium = InlineKeyboardButton('Средние', callback_data=kryl_cb.new(id=idx, action='medium_spice'))
    spicy = InlineKeyboardButton('Острые', callback_data=kryl_cb.new(id=idx, action='spicy'))
    markup.add(not_spicy, medium, spicy)
    return markup


def amount_markup(idx):
    markup = InlineKeyboardMarkup()
    amount8 = InlineKeyboardButton('8 штук', callback_data=kryl_cb.new(id=idx, action='8'))
    amount16 = InlineKeyboardButton('16 штук', callback_data=kryl_cb.new(id=idx, action='16'))
    markup.add(amount8, amount16)
    return markup


projarka_cb = CallbackData('product', 'id', 'action')


def projarka_markup(idx):
    markup = InlineKeyboardMarkup(row_width=3)

    buttons = []
    for key, value in projarkas.items():
        btn = InlineKeyboardButton(value, callback_data=projarka_cb.new(id=idx, action=key))
        buttons.append(btn)

    markup.add(*buttons)

    return markup


garnish_cb = CallbackData('product', 'id', 'action')


def garnish(idx):
    markup = InlineKeyboardMarkup(row_width=1)
    buttons = []
    for key, value in garnishs.items():
        btn = InlineKeyboardButton(value, callback_data=garnish_cb.new(id=idx, action=key))
        buttons.append(btn)

    markup.add(*buttons)
    return markup


sous_cb = CallbackData('product', 'id', 'action')


def sous(idx):
    markup = InlineKeyboardMarkup(row_width=2)
    buttons = []
    for key, value in sauces.items():
        btn = InlineKeyboardButton(value, callback_data=sous_cb.new(id=idx, action=key))
        buttons.append(btn)

    markup.add(*buttons)
    return markup


product_cb = CallbackData('product', 'id', 'action')


def product_markup(idx='', price=0):
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton(f'Заказать за - {price}₽', callback_data=product_cb.new(id=idx, action='add')))
    return markup


category_cb = CallbackData('category', 'id', 'action')


def categories_markup():
    markup = InlineKeyboardMarkup()
    for idx, title in db.fetchall('SELECT * FROM categories'):
        markup.add(InlineKeyboardButton(title, callback_data=category_cb.new(id=idx, action='view_2')))

    return markup


def dyl_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('📖 Меню')
    markup.add(btn_instr, pay)
    markup.add(btnnaz, cart)
    return markup


def time_dlv():
    current_time = str(datetime.now().time())
    return current_time

print(time_dlv())
@dp.message_handler(IsUser(), text=btndlv)
async def dyl_start(message: types.Message):
    if time_dlv()[0] == '2' and time_dlv()[1] == '3' \
            or time_dlv()[0] == '0' \
            or time_dlv()[0] == '1' and time_dlv()[1] == '0':
        await message.answer("Доставка принимается с 11:00 до 23:00")
    else:
        is_allowed = db.fetchall('SELECT * FROM regime')
        if is_allowed[0][1] == 1:
            await message.answer("Минимальная сумма заказа 2000 рублей", reply_markup=dyl_markup())
            await message.answer("ВЫБЕРИТЕ РАЗДЕЛ", reply_markup=categories_markup())
        else:
            await message.answer("Приносим извинения, на данный момент доставка не доступна")


@dp.message_handler(IsUser(), text='📖 Меню')
async def menu(message: types.Message):
    await message.answer("ВЫБЕРИТЕ РАЗДЕЛ", reply_markup=categories_markup())


@dp.message_handler(IsUser(), text=pay)
async def pay_command(message: types.Message):
    await message.answer("https://telegra.ph/SPOSOB-OPLATY-06-17", reply_markup=dyl_markup())


@dp.message_handler(IsUser(), text=btn_instr)
async def instr_procces(message: types.Message):
    await message.answer("https://telegra.ph/Instrukciya-06-10-7", reply_markup=dyl_markup())


@dp.callback_query_handler(IsUser(), category_cb.filter(action='view_2'))
async def category_callback_handler(query: types.CallbackQuery, callback_data: dict):
    products = db.fetchall('''SELECT * FROM products
    WHERE products.tag = (SELECT title FROM categories WHERE idx=?)''',
                           (callback_data['id'],))
    status = db.fetchall("SELECT * FROM status")
    # await query.answer('Все доступные товары.')
    await show_products(query.message, products, status)


@dp.callback_query_handler(IsUser(), product_cb.filter(action='add'))
async def add_product_callback_handler(query: types.CallbackQuery, callback_data: dict, state: FSMContext):
    product_id = callback_data['id']

    idx = ['d2c4042b83301352cfabe1f2e293e03d', 'd21e31622b1b461aec6692ed93e61e5b',
           '6c64de44bccc509c2c0c23cd6d2d0a0d', '988f7a785631056fb53022bca062b89d',
           '7e3db5c3c00bdb2ebd02e49214cc15f4', 'efc44a03ce222a21b93c66fa6fb489ca',
           '2097656498cb47e1ef11576e5d221ec2', '35106c4ba8cbc7d430e48a6247fd400a',
           '5f2ae5d354d1d8a4439d0171866c56b7', '33d35788f4deebe976552e9b4bd28913']  # исключения

    if product_id in idx:
        async with state.proxy() as data:
            data[product_id] = {}
            if product_id == idx[-2]:
                msg = 'Выберите количество крылышек'
                markup = amount_markup(product_id)
            elif product_id == idx[-1]:
                msg = 'Выберите гарнир'
                markup = garnish(product_id)
                data[product_id]['projarka'] = 'medium'
            else:
                msg = 'Выберите прожарку'
                markup = projarka_markup(product_id)

            await query.answer(msg)
            await query.message.edit_reply_markup(reply_markup=markup)
    else:
        db.query('INSERT INTO cart VALUES (?, ?, 1, null, null, null, null, null)',
                (query.message.chat.id, product_id))
        await query.answer('Товар добавлен в корзину!')
        await query.message.delete()


@dp.callback_query_handler(IsUser(), projarka_cb.filter(action=['blue_rare', 'medium_rare', 'medium', 'medium_well', 'well_done']))
async def projarka_handler(query: types.CallbackQuery, callback_data: dict, state: FSMContext):
    async with state.proxy() as data:
        data[callback_data['id']]['projarka'] = callback_data['action']

        await query.answer('Выберите гарнир')
        await query.message.edit_reply_markup(reply_markup=garnish(callback_data['id']))


@dp.callback_query_handler(IsUser(), garnish_cb.filter(action=['pure', 'free', 'dolki', 'kuku', 'salat']))
async def garnish_handler(query: types.CallbackQuery, callback_data: dict, state: FSMContext):
    async with state.proxy() as data:
        data[callback_data['id']]['garnish'] = callback_data['action']

    await query.answer('Выберите соус')
    await query.message.edit_reply_markup(reply_markup=sous(callback_data['id']))


@dp.callback_query_handler(IsUser(), sous_cb.filter(action=['blu', 'nacos', 'meks', 'bbq', 'chili']))
async def sauce_handler(query: types.CallbackQuery, callback_data: dict, state: FSMContext):
    async with state.proxy() as data:
        product_id = callback_data['id']
        db.query('INSERT INTO cart VALUES (?, ?, 1, ?, ?, ?, null, null)',
                (query.message.chat.id, product_id, data[product_id]['projarka'], data[product_id]['garnish'], callback_data['action']))
    await query.answer('Товар добавлен в корзину!')
    price = db.fetchone("SELECT price FROM products WHERE idx=?", (product_id,))
    await query.message.edit_reply_markup(reply_markup=product_markup(product_id, price[0]))


@dp.callback_query_handler(IsUser(), kryl_cb.filter(action=['8', '16']))
async def amount_handler(query: types.CallbackQuery, callback_data: dict, state: FSMContext):
    async with state.proxy() as data:
        data[callback_data['id']]['amount'] = callback_data['action']

    await query.answer('Выберите остроту')
    await query.message.edit_reply_markup(reply_markup=spice_markup(callback_data['id']))


@dp.callback_query_handler(IsUser(), kryl_cb.filter(action=['not_spicy', 'medium_spice', 'spicy']))
async def spice_handler(query: types.CallbackQuery, callback_data: dict, state: FSMContext):
    async with state.proxy() as data:
        product_id = callback_data['id']
        db.query('INSERT INTO cart VALUES (?, ?, 1, null, null, null, ?, ?)',
                 (query.message.chat.id, product_id, data[product_id]['amount'], callback_data['action']))

    await query.answer('Товар добавлен в корзину!')
    price = db.fetchone("SELECT price FROM products WHERE idx=?", (product_id,))
    await query.message.edit_reply_markup(reply_markup=product_markup(product_id, price[0]))


async def show_products(m, products, status):
    if len(products) == 0:
        await m.answer('Здесь ничего нет 😢')

        await bot.send_chat_action(m.chat.id, ChatActions.TYPING)
    else:
        for idx, title, body, image, price, _ in products:
            for id, stat in status:
                if idx in id and stat in 'start':
                    markup = product_markup(idx, price)
                    text = f'<b>{title}</b>\n\n{body}'
                    if image:
                        await m.answer_photo(photo=image,
                                             caption=text,
                                             reply_markup=markup)
                    else:
                        await m.answer(text=text, reply_markup=markup)
