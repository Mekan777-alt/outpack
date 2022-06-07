from aiogram.utils.callback_data import CallbackData
from config import bot, dp, db
from filters import IsUser
from app import btndlv, cart
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, ChatActions
from hendlers.user.catalog import btnnaz

btn_instr = "⚙️ ИНСТРУКЦИЯ"

kryl_cb = CallbackData('product', 'id', 'action')


def kryl(idx):
    global kryl_cb
    markup = InlineKeyboardMarkup()
    medium = InlineKeyboardButton('Средняя острата', callback_data=projarka_cb.new(id=idx, action='sred'))
    hard = InlineKeyboardButton('Острые', callback_data=projarka_cb.new(id=idx, action='ostr'))
    markup.add(medium, hard)
    return markup


projarka_cb = CallbackData('product', 'id', 'action')


def projacka_markup(idx):
    global projarka_cb

    markup = InlineKeyboardMarkup()
    blue = InlineKeyboardButton('Blue rare', callback_data=projarka_cb.new(id=idx, action='blue_rare'))
    medium_rare = InlineKeyboardButton('Medium rare', callback_data=projarka_cb.new(id=idx, action='medium_rare'))
    medium = InlineKeyboardButton('Medium', callback_data=projarka_cb.new(id=idx, action='medium'))
    medium_well = InlineKeyboardButton('Medium well', callback_data=projarka_cb.new(id=idx, action='medium_well'))
    well_done = InlineKeyboardButton('Well done', callback_data=projarka_cb.new(id=idx, action='well_done'))
    markup.row(blue, medium_rare, medium)
    markup.add(medium_well, well_done)
    return markup


product_cb_2 = CallbackData('product', 'id', 'action')


def product_markup_2(idx, count):
    global product_cb_2

    markup = InlineKeyboardMarkup()
    back_btn = InlineKeyboardButton('➖', callback_data=product_cb_2.new(id=idx, action='decrease'))
    count_btn = InlineKeyboardButton(count, callback_data=product_cb_2.new(id=idx, action='count'))
    next_btn = InlineKeyboardButton('➕️', callback_data=product_cb_2.new(id=idx, action='increase'))

    markup.row(back_btn, count_btn, next_btn)

    return markup


product_cb = CallbackData('product', 'id', 'action')


def product_markup(idx='', price=0):
    global product_cb

    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton(f'Заказать за - {price}₽', callback_data=product_cb.new(id=idx, action='add')))
    return markup


category_cb = CallbackData('category', 'id', 'action')


def categories_markup():
    global category_cb

    markup = InlineKeyboardMarkup()
    for idx, title in db.fetchall('SELECT * FROM categories'):
        markup.add(InlineKeyboardButton(title, callback_data=category_cb.new(id=idx, action='view')))

    return markup


def dyl_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(btn_instr, btnnaz).add(cart)
    return markup


@dp.message_handler(IsUser(), text=btndlv)
async def dyl_start(message: types.Message):
    await message.answer("Минимальная сумма заказа состовляет 1500 рублей", reply_markup=dyl_markup())
    await message.answer("ВЫБЕРИТЕ РАЗДЕЛ", reply_markup=categories_markup())


@dp.callback_query_handler(IsUser(), category_cb.filter(action='view'))
async def category_callback_handler(query: types.CallbackQuery, callback_data: dict):
    products = db.fetchall('''SELECT * FROM products
    WHERE products.tag = (SELECT title FROM categories WHERE idx=?)''',
                           (callback_data['id'],))

    # await query.answer('Все доступные товары.')
    await show_products(query.message, products)


@dp.callback_query_handler(IsUser(), product_cb.filter(action='add'))
async def add_product_callback_handler(query: types.CallbackQuery, callback_data: dict):
    idx = ['d2c4042b83301352cfabe1f2e293e03d', 'd21e31622b1b461aec6692ed93e61e5b',
           '6c64de44bccc509c2c0c23cd6d2d0a0d', '988f7a785631056fb53022bca062b89d']
    if callback_data['id'] in idx:
        await query.message.edit_reply_markup(reply_markup=projacka_markup(callback_data['id']))
    elif callback_data['id'] in '5f2ae5d354d1d8a4439d0171866c56b7':
        await query.message.edit_reply_markup(reply_markup=kryl(callback_data['id']))
    else:
        db.query('INSERT INTO cart VALUES (?, ?, 1)',
                (query.message.chat.id, callback_data['id']))
        await query.answer('Товар добавлен в корзину!')

        await query.message.delete()


@dp.callback_query_handler(IsUser(), projarka_cb.filter(action='sred'))
@dp.callback_query_handler(IsUser(), projarka_cb.filter(action='ostr'))
@dp.callback_query_handler(IsUser(), projarka_cb.filter(action='blue_rare'))
@dp.callback_query_handler(IsUser(), projarka_cb.filter(action='medium_rare'))
@dp.callback_query_handler(IsUser(), projarka_cb.filter(action='medium'))
@dp.callback_query_handler(IsUser(), projarka_cb.filter(action='medium_well'))
@dp.callback_query_handler(IsUser(), projarka_cb.filter(action='well_done'))
async def projarka(query: types.CallbackQuery, callback_data: dict):
    db.query('INSERT INTO wallet VALUES (?, ?)',
             (callback_data['id'], callback_data['action']))

    db.query('INSERT INTO cart VALUES (?, ?, 1)',
             (query.message.chat.id, callback_data['id']))
    await query.answer('Товар добавлен в корзину!')

    await query.message.delete()


async def show_products(m, products):
    if len(products) == 0:

        await m.answer('Здесь ничего нет 😢')
    else:

        await bot.send_chat_action(m.chat.id, ChatActions.TYPING)

        for idx, title, body, image, price, _ in products:
            markup = product_markup(idx, price)
            text = f'<b>{title}</b>\n\n{body}'

            await m.answer_photo(photo=image,
                                 caption=text,
                                 reply_markup=markup)
