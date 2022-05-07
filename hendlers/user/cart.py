import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import Message, ChatActions, ReplyKeyboardMarkup, CallbackQuery, ReplyKeyboardRemove, \
    InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ContentType
from aiogram.utils.callback_data import CallbackData
from app import cart, balance
from config import dp, db, bot
from filters import IsUser
from hendlers.admin.add import check_markup, back_message, all_right_message, back_markup, confirm_markup, \
    confirm_message
BRON_CHANNEL = "@main_channel2"

b54 = KeyboardButton("📞 Отправить свой номер", request_contact=True)
send_phone = ReplyKeyboardMarkup(resize_keyboard=True).add(b54)

product_cb = CallbackData('product', 'id', 'action')
TOKEN_PAYMENTS = "401643678:TEST:12623b8e-8aa4-4c46-beca-8231bd533772"


def product_markup(idx, count):
    global product_cb

    markup = InlineKeyboardMarkup()
    back_btn = InlineKeyboardButton('➖', callback_data=product_cb.new(id=idx, action='decrease'))
    count_btn = InlineKeyboardButton(count, callback_data=product_cb.new(id=idx, action='count'))
    next_btn = InlineKeyboardButton('➕️', callback_data=product_cb.new(id=idx, action='increase'))
    markup.row(back_btn, count_btn, next_btn)

    return markup


@dp.message_handler(IsUser(), text=cart)
async def process_cart(message: Message, state: FSMContext):
    cart_data = db.fetchall(
        'SELECT * FROM cart WHERE cid=?', (message.chat.id,))

    if len(cart_data) == 0:

        await message.answer('Ваша корзина пуста.')

    else:

        await bot.send_chat_action(message.chat.id, ChatActions.TYPING)
        async with state.proxy() as data:
            data['products'] = {}

        order_cost = 0

        for _, idx, count_in_cart in cart_data:

            product = db.fetchone('SELECT * FROM products WHERE idx=?', (idx,))

            if product is None:

                db.query('DELETE FROM cart WHERE idx=?', (idx,))

            else:
                _, title, body, image, price, _ = product
                order_cost += price

                async with state.proxy() as data:
                    data['products'][idx] = [title, price, count_in_cart]

                markup = product_markup(idx, count_in_cart)
                text = f'<b>{title}</b>\n\n{body}\n\nЦена: {price}₽.'

                await message.answer_photo(photo=image,
                                           caption=text,
                                           reply_markup=markup)

        if order_cost != 0:
            markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
            markup.add('📦 Оформить заказ')

            await message.answer('Перейти к оформлению?',
                                 reply_markup=markup)


@dp.callback_query_handler(IsUser(), product_cb.filter(action='count'))
@dp.callback_query_handler(IsUser(), product_cb.filter(action='increase'))
@dp.callback_query_handler(IsUser(), product_cb.filter(action='decrease'))
async def product_callback_handler(query: CallbackQuery, callback_data: dict, state: FSMContext):
    idx = callback_data['id']
    action = callback_data['action']

    if 'count' == action:

        async with state.proxy() as data:

            if 'products' not in data.keys():

                await process_cart(query.message, state)

            else:

                await query.answer('Количество - ' + data['products'][idx][2])

    else:

        async with state.proxy() as data:

            if 'products' not in data.keys():

                await process_cart(query.message, state)

            else:

                data['products'][idx][2] += 1 if 'increase' == action else -1
                count_in_cart = data['products'][idx][2]

                if count_in_cart == 0:

                    db.query('''DELETE FROM cart
                    WHERE cid = ? AND idx = ?''', (query.message.chat.id, idx))

                    await query.message.delete()
                else:

                    db.query('''UPDATE cart 
                    SET quantity = ? 
                    WHERE cid = ? AND idx = ?''', (count_in_cart, query.message.chat.id, idx))

                    await query.message.edit_reply_markup(product_markup(idx, count_in_cart))


class CheckoutState(StatesGroup):
    check_cart = State()
    name = State()
    address = State()
    phone_number = State()
    confirm = State()


successful_payment = '''
Ура! Платеж совершен успешно! Приятного аппетита!'''

MESSAGE = {
    'title': db.fetchone("""SELECT title FROM products"""),
    'description': db.fetchone("""SELECT body FROM products"""),
    'label': db.fetchone("""SELECT title FROM products"""),
    'photo_url': db.fetchone("""SELECT photo FROM products"""),
    'successfil_payments': successful_payment,
    'count': db.fetchone("""SELECT quantity FROM cart""")
}


@dp.message_handler(IsUser(), text='📦 Оформить заказ')
async def process_checkout(message: Message, state: FSMContext):
    await CheckoutState.check_cart.set()
    await checkout(message, state)


async def checkout(message, state):
    global MESSAGE
    answer = ''
    total_price = 0

    async with state.proxy() as data:
        for title, price, count_in_cart in data['products'].values():
            tp = count_in_cart * price
            answer += f'<b>{title}</b> * {count_in_cart}шт. = {tp}₽\n'
            total_price += tp

    # await message.answer(f'{answer}\nОбщая сумма заказа: {total_price}₽.',
    #                     reply_markup=check_markup())
    total_price *= 100
    PRICE = types.LabeledPrice(label=MESSAGE['label'][0], amount=total_price)
    await bot.send_invoice(message.chat.id,
                           title=MESSAGE['title'][0],
                           description=MESSAGE['description'][0],
                           provider_token=TOKEN_PAYMENTS,
                           currency='rub',
                           # need_email=True,
                           # need_phone_number=True,
                           # need_shipping_address=True,
                           photo_url=MESSAGE['photo_url'],
                           # photo_size=400,
                           # photo_width=400,
                           # photo_height=400,
                           is_flexible=False,  # True If you need to set up Shipping Fee
                           prices=[PRICE],
                           start_parameter='time-machine-example',
                           payload='some-invoice-payload-for-our-internal-use')


@dp.pre_checkout_query_handler(lambda query: True)
async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@dp.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT)
async def process_successful_payment(message: types.Message, state: FSMContext):
    global MESSAGE
    print('successful_payment:')
    pmnt = message.successful_payment.to_python()
    for key, val in pmnt.items():
        print(f'{key} = {val}')

    await bot.send_message(
        message.chat.id,
        MESSAGE['successful_payment'])


@dp.message_handler(IsUser(), lambda message: message.text not in [all_right_message, back_message],
                    state=CheckoutState.check_cart)
async def process_check_cart_invalid(message: Message):
    await message.reply('Такого варианта не было.')


@dp.message_handler(IsUser(), text=back_message, state=CheckoutState.check_cart)
async def process_check_cart_back(message: Message, state: FSMContext):
    await state.finish()
    await process_cart(message, state)


@dp.message_handler(IsUser(), text=all_right_message, state=CheckoutState.check_cart)
async def process_check_cart_all_right(message: Message, state: FSMContext):
    await CheckoutState.next()
    await message.answer('Укажите свое имя.',
                         reply_markup=back_markup())


@dp.message_handler(IsUser(), text=back_message, state=CheckoutState.name)
async def process_name_back(message: Message, state: FSMContext):
    await CheckoutState.check_cart.set()
    await checkout(message, state)


@dp.message_handler(IsUser(), state=CheckoutState.name)
async def process_name(message: Message, state: FSMContext):
    async with state.proxy() as data:

        data['name'] = message.text

        if 'address' in data.keys():

            await confirm(message)
            await CheckoutState.confirm.set()

        else:

            await CheckoutState.next()
            await message.answer('Укажите свой адрес места жительства.',
                                 reply_markup=back_markup())


@dp.message_handler(IsUser(), text=back_message, state=CheckoutState.address)
async def process_address_back(message: Message, state: FSMContext):
    async with state.proxy() as data:
        await message.answer('Изменить имя с <b>' + data['name'] + '</b>?',
                             reply_markup=back_markup())

    await CheckoutState.name.set()


@dp.message_handler(IsUser(), state=CheckoutState.address)
async def process_address(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['address'] = message.text

        # await confirm(message)
        await CheckoutState.next()
        await message.answer("Так, теперь мне нужен твой номер телефона.\n"
                             "Исключительно в деловых целях 🙂", reply_markup=send_phone)


@dp.message_handler(IsUser(), content_types=ContentType.CONTACT, state=CheckoutState.phone_number)
async def phone_number(message: Message, state: FSMContext):
    async with state.proxy() as data:
        if message.contact is not None:
            data['phone_number'] = message.contact["phone_number"]
        elif message.contact is None:
            data['phone_number'] = message.text
        await confirm(message)


async def confirm(message):
    await message.answer('Убедитесь, что все правильно оформлено и подтвердите заказ.',
                         reply_markup=confirm_markup())


@dp.message_handler(IsUser(), lambda message: message.text not in [confirm_message, back_message],
                    state=CheckoutState.confirm)
async def process_confirm_invalid(message: Message):
    await message.reply('Такого варианта не было.')


@dp.message_handler(IsUser(), text=back_message, state=CheckoutState.confirm)
async def process_confirm(message: Message, state: FSMContext):
    await CheckoutState.address.set()

    async with state.proxy() as data:
        await message.answer('Изменить адрес с <b>' + data['address'] + '</b>?',
                             reply_markup=back_markup())


@dp.message_handler(IsUser(), text=confirm_message, state=CheckoutState.confirm)
async def process_confirm(message: Message, state: FSMContext):
    global MESSAGE
    enough_money = True  # enough money on the balance sheet
    markup = ReplyKeyboardRemove()
    if enough_money:

        logging.info('Deal was made.')

        async with state.proxy() as data:

            cid = message.chat.id
            products = [idx + '=' + str(quantity)
                        for idx, quantity in db.fetchall('''SELECT idx, quantity FROM cart
            WHERE cid=?''', (cid,))]  # idx=quantity

            db.query('INSERT INTO orders VALUES (?, ?, ?, ?, ?)',
                     (cid, data['name'], data['address'], data['phone_number'], ' '.join(products)))

            # db.query('DELETE FROM cart WHERE cid=?', (cid,))

            await message.answer(
                'Ок! Ваш заказ уже в пути 🚀\nИмя: <b>' + data['name'] + '</b>\nАдрес: <b>' + data['address'] + '</b>',
                reply_markup=markup)
            await bot.send_message(BRON_CHANNEL, f"Доставка №1\n"
                                                 f"\n"
                                                 f"Блюдо: {MESSAGE['title'][0]}\n"
                                                 f"Количество: {MESSAGE['count']}\n"
                                                 f"Адрес доставки: {data['address']}\n"
                                                 f"Номер телефона: {data['phone_number']}:")
    else:

        await message.answer('У вас недостаточно денег на счете. Пополните баланс!',
                             reply_markup=markup)

    await state.finish()


@dp.message_handler(IsUser(), text=balance)
async def process_balance(message: Message, state: FSMContext):
    await message.answer('Ваш кошелек пуст! Чтобы его пополнить нужно...')
