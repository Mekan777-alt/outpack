from aiogram.utils.callback_data import CallbackData
from config import bot, dp, db
from filters import IsUser
from app import btndlv, cart
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, ChatActions
from hendlers.user.catalog import btnnaz

btn_instr = "⚙️ ИНСТРУКЦИЯ"



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

    await query.answer('Все доступные товары.')
    await show_products(query.message, products)


@dp.callback_query_handler(IsUser(), product_cb.filter(action='add'))
async def add_product_callback_handler(query: types.CallbackQuery, callback_data: dict):
    db.query('INSERT INTO cart VALUES (?, ?, 1)',
             (query.message.chat.id, callback_data['id']))

    await query.answer('Товар добавлен в корзину!')
    #await query.message.edit_reply_markup(reply_markup=product_markup_2(callback_data['id'], 1))
    await query.message.delete()


async def show_products(m, products):
    if len(products) == 0:

        await m.answer('Здесь ничего нет 😢')
    else:

        await bot.send_chat_action(m.chat.id, ChatActions.TYPING)

        for idx, title, body, image, price, _ in products:
            markup = product_markup(idx, price)
            text = f'<b>{title}</b>\n\n{body}'
            if image:
                await m.answer_photo(photo=image,
                                     caption=text,
                                     reply_markup=markup)
            else:
                await m.answer(text=text, reply_markup=markup)
