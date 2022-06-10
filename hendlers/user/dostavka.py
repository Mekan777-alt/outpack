from aiogram.utils.callback_data import CallbackData
from config import bot, dp, db
from filters import IsUser
from app import btndlv, cart
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, ChatActions
from hendlers.user.catalog import btnnaz
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext

btn_instr = "⚙️ ИНСТРУКЦИЯ"

projarkas = {"blue_rare": "Blue rare", "medium_rare": "Medium rare", "medium": "Medium", "medium_well": "Medium well", "well_done": "Well done"}
garnishs = {"pure": "Картофельное пюре", "free": "Картофель фри", "dolki": "Картофельные дольки", "kuku": "Початок кукурузы (150 гр.)", "salat": "Свежий салатик (150 гр.)"}
sauces = {"blu": "Соус блю чиз", "nacos": "Соус начос", "meks": "Соус мексиканская сальса", "bbq": "Соус BBQ", "chili": "Соус сладкий чили"}

kryl_cb = CallbackData('product', 'id', 'action')


class SteakAddingsState(StatesGroup):
    projarka = State()
    garnish = State()
    sauce = State()


class WingsAddingsState(StatesGroup):
    spice = State()
    amount = State()


def spice_markup(idx):
    global kryl_cb
    markup = InlineKeyboardMarkup()
    medium = InlineKeyboardButton('Средняя острота', callback_data=kryl_cb.new(id=idx, action='medium'))
    spicy = InlineKeyboardButton('Острые', callback_data=kryl_cb.new(id=idx, action='spicy'))
    markup.add(medium, spicy)
    return markup


def amount_markup(idx):
    global kryl_cb
    markup = InlineKeyboardMarkup()
    medium = InlineKeyboardButton('8 штук', callback_data=projarka_cb.new(id=idx, action='8'))
    spicy = InlineKeyboardButton('16 штук', callback_data=projarka_cb.new(id=idx, action='16'))
    markup.add(medium, spicy)
    return markup


projarka_cb = CallbackData('product', 'id', 'action')


def projarka_markup(idx):
    global projarka_cb

    markup = InlineKeyboardMarkup(row_width=3)
    buttons = []
    for key, value in projarkas.items():
        btn = InlineKeyboardButton(value, callback_data=projarka_cb.new(id=idx, action=key))
        buttons.append(btn)

    markup.add(*buttons)

    return markup


garnish_cb = CallbackData('product', 'id', 'action')


def garnish(idx):
    global garnish_cb

    markup = InlineKeyboardMarkup(row_width=1)
    buttons = []
    for key, value in garnishs.items():
        btn = InlineKeyboardButton(value, callback_data=garnish_cb.new(id=idx, action=key))
        buttons.append(btn)

    markup.add(*buttons)
    return markup


sous_cb = CallbackData('product', 'id', 'action')


def sous(idx):
    global sous_cb

    markup = InlineKeyboardMarkup(row_width=2)
    buttons = []
    for key, value in sauces.items():
        btn = InlineKeyboardButton(value, callback_data=sous_cb.new(id=idx, action=key))
        buttons.append(btn)

    markup.add(*buttons)
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
    await message.answer("Минимальная сумма заказа 1500 рублей", reply_markup=dyl_markup())
    await message.answer("ВЫБЕРИТЕ РАЗДЕЛ", reply_markup=categories_markup())


@dp.callback_query_handler(IsUser(), category_cb.filter(action='view'))
async def category_callback_handler(query: types.CallbackQuery, callback_data: dict):
    products = db.fetchall('''SELECT * FROM products
    WHERE products.tag = (SELECT title FROM categories WHERE idx=?)''',
                           (callback_data['id'],))

    # await query.answer('Все доступные товары.')
    await show_products(query.message, products)


@dp.callback_query_handler(IsUser(), product_cb.filter(action='add'))
async def add_product_callback_handler(query: types.CallbackQuery, callback_data: dict, state: FSMContext):
    product_id = callback_data['id']

    idx = ['d2c4042b83301352cfabe1f2e293e03d', 'd21e31622b1b461aec6692ed93e61e5b',
           '6c64de44bccc509c2c0c23cd6d2d0a0d', '988f7a785631056fb53022bca062b89d',
           '5f2ae5d354d1d8a4439d0171866c56b7']

    if product_id in idx:
        if product_id == idx[-1]:
            msg = 'Выберите остроту'
            markup = spice_markup(product_id)
            await WingsAddingsState.spice.set()
        else:
            msg = 'Выберите прожарку'
            markup = projarka_markup(product_id)
            await SteakAddingsState.projarka.set()

        await query.answer(msg)
        await query.message.edit_reply_markup(reply_markup=markup)
        async with state.proxy() as data:
            data['idx'] = product_id

    else:
        db.query('INSERT INTO cart VALUES (?, ?, 1, null, null, null, null, null)',
                (query.message.chat.id, product_id))
        await query.answer('Товар добавлен в корзину!')

        await query.message.delete()


@dp.callback_query_handler(IsUser(), projarka_cb.filter(action=['blue_rare', 'medium_rare', 'medium', 'medium_well', 'well_done']), state=SteakAddingsState.projarka)
async def projarka_handler(query: types.CallbackQuery, callback_data: dict, state: FSMContext):
    async with state.proxy() as data:
        data['projarka'] = callback_data['action']

    await query.answer('Выберите гарнир')
    await query.message.edit_reply_markup(reply_markup=garnish(callback_data['id']))
    await SteakAddingsState.next()


@dp.callback_query_handler(IsUser(), garnish_cb.filter(action=['pure', 'free', 'dolki', 'kuku', 'salat']), state=SteakAddingsState.garnish)
async def garnish_handler(query: types.CallbackQuery, callback_data: dict, state: FSMContext):
    async with state.proxy() as data:
        data['garnish'] = callback_data['action']

    await query.answer('Выберите соус')
    await query.message.edit_reply_markup(reply_markup=sous(callback_data['id']))
    await SteakAddingsState.next()


@dp.callback_query_handler(IsUser(), sous_cb.filter(action=['blu', 'nacos', 'meks', 'bbq', 'chili']), state=SteakAddingsState.sauce)
async def sauce_handler(query: types.CallbackQuery, callback_data: dict, state: FSMContext):
    async with state.proxy() as data:
        db.query('INSERT INTO cart VALUES (?, ?, 1, ?, ?, ?, null, null)',
                 (query.message.chat.id, data['idx'], data['projarka'], data['garnish'], callback_data['action']))

    await query.answer('Товар добавлен в корзину!')
    await query.message.delete()
    await state.finish()


@dp.callback_query_handler(IsUser(), kryl_cb.filter(action=['medium', 'spicy']), state=WingsAddingsState.spice)
async def spice_handler(query: types.CallbackQuery, callback_data: dict, state: FSMContext):
    async with state.proxy() as data:
        data['spice'] = callback_data['action']

    await query.answer('Выберите количество крылышек')
    await query.message.edit_reply_markup(reply_markup=amount_markup(callback_data['id']))
    await WingsAddingsState.next()


@dp.callback_query_handler(IsUser(), kryl_cb.filter(action=['8', '16']), state=WingsAddingsState.amount)
async def amount_handler(query: types.CallbackQuery, callback_data: dict, state: FSMContext):
    async with state.proxy() as data:
        db.query('INSERT INTO cart VALUES (?, ?, 1, null, null, null, ?, ?)',
                 (query.message.chat.id, data['idx'], data['spice'], callback_data['action']))

    await query.answer('Товар добавлен в корзину!')
    await query.message.delete()
    await state.finish()


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
