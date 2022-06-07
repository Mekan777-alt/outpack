from hashlib import md5
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils.callback_data import CallbackData
from config import dp, db, bot
from aiogram import types
from filters import IsAdmin
from app import add_product, delete_product, settings
from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, ContentType, CallbackQuery, InlineKeyboardButton, \
    InlineKeyboardMarkup, ChatActions

"""ADD PRODUCTS"""
cancel_message = '🚫 Отменить'
back_message = '👈 Назад'
back = '👈 Назад'
all_right_message = '✅ Все верно'
confirm_message = '✅ Подтвердить заказ'


def confirm_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add(confirm_message)
    markup.add(back_message)

    return markup


def back_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add(back_message)

    return markup


def check_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.row(back_message, all_right_message)

    return markup


def submit_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.row(cancel_message, all_right_message)

    return markup

"""remove"""

category_cb = CallbackData('category', 'id', 'action')
product_cb = CallbackData('product', 'id', 'action')

delete_category = '🗑️ Удалить категорию'


@dp.message_handler(IsAdmin(), text=settings)
async def process_settings(message: types.Message):

    markup = InlineKeyboardMarkup()

    for idx, title in db.fetchall('SELECT * FROM categories'):

        markup.add(InlineKeyboardButton(
            title, callback_data=category_cb.new(id=idx, action='view')))

    markup.add(InlineKeyboardButton(
        '+ Добавить категорию', callback_data='add_category'))

    await message.answer('Настройка категорий:', reply_markup=markup)


@dp.callback_query_handler(IsAdmin(), category_cb.filter(action='view'))
async def category_callback_handler(query: CallbackQuery, callback_data: dict, state: FSMContext):

    category_idx = callback_data['id']

    products = db.fetchall('''SELECT * FROM products product
    WHERE product.tag = (SELECT title FROM categories WHERE idx=?)''',
                           (category_idx,))

    await query.message.delete()
    await query.answer('Все добавленные товары в эту категорию.')
    await state.update_data(category_index=category_idx)
    await show_products(query.message, products, category_idx)


# category

class CategoryState(StatesGroup):
    title = State()


@dp.callback_query_handler(IsAdmin(), text='add_category')
async def add_category_callback_handler(query: CallbackQuery):
    await query.message.delete()
    await query.message.answer('Название категории?')
    await CategoryState.title.set()


@dp.message_handler(IsAdmin(), state=CategoryState.title)
async def set_category_title_handler(message: types.Message, state: FSMContext):

    category = message.text
    idx = md5(category.encode('utf-8')).hexdigest()
    db.query('INSERT INTO categories VALUES (?, ?)', (idx, category))

    await state.finish()
    await process_settings(message)


@dp.message_handler(IsAdmin(), text=delete_category)
async def delete_category_handler(message: types.Message, state: FSMContext):

    async with state.proxy() as data:

        if 'category_index' in data.keys():

            idx = data['category_index']

            db.query(
                'DELETE FROM products WHERE tag IN (SELECT title FROM categories WHERE idx=?)', (idx,))
            db.query('DELETE FROM categories WHERE idx=?', (idx,))

            await message.answer('Готово!', reply_markup=ReplyKeyboardRemove())
            await process_settings(message)

"""add product"""


@dp.message_handler(IsAdmin(), text=back)
async def vack_menu(message: types.Message):
    markup = ReplyKeyboardRemove()
    await message.answer("Переход на настройки категории", reply_markup=markup)
    await process_settings(message)


class ProductState(StatesGroup):
    title = State()
    body = State()
    image = State()
    price = State()
    confirm = State()


@dp.message_handler(IsAdmin(), text=add_product)
async def product_state_process(message: types.Message):
    await ProductState.title.set()

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(cancel_message)
    await message.answer("Название:", reply_markup=markup)


@dp.message_handler(IsAdmin(), text=cancel_message, state=ProductState.title)
async def process_cancel(message: types.Message, state: FSMContext):

    await message.answer('Ок, отменено!', reply_markup=ReplyKeyboardRemove())
    await state.finish()

    await process_settings(message)


@dp.message_handler(IsAdmin(), text=back_message, state=ProductState.title)
async def product_state_back(message: types.Message, state: FSMContext):
    await product_state_process(message)


@dp.message_handler(IsAdmin(), state=ProductState.title)
async def product_title(message: types.Message, state: FSMContext):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add(back_message)
    async with state.proxy() as data:
        data['title'] = message.text
    await ProductState.next()
    await message.answer("Описание:", reply_markup=back_markup())


@dp.message_handler(IsAdmin(), text=back_message, state=ProductState.body)
async def process_back_title(message: types.Message, state: FSMContext):
    await ProductState.title.set()
    async with state.proxy() as data:
        await message.answer(f"Изменить название <b>{data['title']}</b>?", reply_markup=back_markup())


@dp.message_handler(IsAdmin(), state=ProductState.body)
async def product_body(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['body'] = message.text
    await ProductState.next()

    markup = back_markup()
    markup.add("Без фото")
    await message.answer("Фото: ", reply_markup=markup)


@dp.message_handler(IsAdmin(), content_types=ContentType.PHOTO, state=ProductState.image)
async def product_photo(message: types.Message, state: FSMContext):
    file_id = message.photo[-1].file_id
    file_in = await bot.get_file(file_id)
    download_file = (await bot.download_file(file_in.file_path)).read()
    async with state.proxy() as data:
        data['image'] = download_file
    await ProductState.next()
    await message.answer("Цена: ", reply_markup=back_markup())


@dp.message_handler(IsAdmin(), content_types=ContentType.TEXT, state=ProductState.image)
async def product_price(message: types.Message, state: FSMContext):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add(back_message)
    async with state.proxy() as data:
        if message.text == back_message:
            await ProductState.body.set()
            await message.answer(f"Изменить описание с <b>{data['body']}</b>?", reply_markup=back_markup())
        elif message.text == 'Без фото':
            data['image'] = None
            await ProductState.next()
            await message.answer("Цена: ", reply_markup=back_markup())


@dp.message_handler(IsAdmin(), lambda message: not message.text.isdigit(), state=ProductState.price)
async def process_price_invalid(message: types.Message, state: FSMContext):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add(back_message)
    if message.text == back_message:
        await ProductState.image.set()
        async with state.proxy() as data:
            await message.answer("Другое изображение?", reply_markup=markup)
    else:
        await message.answer('Укажите цену в виде числа!')


@dp.message_handler(IsAdmin(), lambda message: message.text.isdigit(), state=ProductState.price)
async def process_price(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['price'] = message.text
        title = data['title']
        body = data['body']
        photo = data['image']
        price = data['price']
        await ProductState.next()
        text = f'<b>{title}</b>\n\n{body}\n\nЦена: {price} рублей.'

        markup = check_markup()
        if photo:
            await message.answer_photo(photo=photo,
                                       caption=text,
                                       reply_markup=markup)
        else:
            await message.answer(text=text, reply_markup=markup)


@dp.message_handler(IsAdmin(), lambda message: message.text not in [back_message, all_right_message], state=ProductState.confirm)
async def process_confirm_invalid(message: types.Message, state: FSMContext):
    await message.answer('Такого варианта не было.')


@dp.message_handler(IsAdmin(), text=back_message, state=ProductState.confirm)
async def process_confirm_back(message: types.Message, state: FSMContext):
    await ProductState.price.set()
    async with state.proxy() as data:
        await message.answer(f"Изменить цену с <b>{data['price']}</b>?", reply_markup=back_markup())


@dp.message_handler(IsAdmin(), text=all_right_message, state=ProductState.confirm)
async def process_confirm(message: types.Message, state: FSMContext):
    async with state.proxy() as data:

        title = data['title']
        body = data['body']
        image = data['image']
        price = data['price']

        tag = db.fetchone(
            'SELECT title FROM categories WHERE idx=?', (data['category_index'],))[0]
        idx = md5(' '.join([title, body, price, tag]
                           ).encode('utf-8')).hexdigest()

        db.query('INSERT INTO products VALUES (?, ?, ?, ?, ?, ?)',
                 (idx, title, body, image, int(price), tag))

    await state.finish()
    await message.answer('Готово!', reply_markup=ReplyKeyboardRemove())
    await process_settings(message)


@dp.callback_query_handler(IsAdmin(), product_cb.filter(action='delete'))
async def delete_product_callback_handler(query: CallbackQuery, callback_data: dict):

    product_idx = callback_data['id']
    db.query('DELETE FROM products WHERE idx=?', (product_idx,))
    await query.answer('Удалено!')
    await query.message.delete()


async def show_products(m, products, category_idx):

    await bot.send_chat_action(m.chat.id, ChatActions.TYPING)

    for idx, title, body, image, price, tag in products:

        text = f'<b>{title}</b>\n\n{body}\n\nЦена: {price} рублей.'

        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(
            '🗑️ Удалить', callback_data=product_cb.new(id=idx, action='delete')))

        if image:
            await m.answer_photo(photo=image,
                                 caption=text,
                                 reply_markup=markup)
        else:
            await m.answer(text=text, reply_markup=markup)

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(add_product)
    markup.add(delete_category)
    markup.add(back)

    await m.answer('Хотите что-нибудь добавить или удалить?', reply_markup=markup)