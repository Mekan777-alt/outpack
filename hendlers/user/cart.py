from datetime import datetime
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import Message, ChatActions, ReplyKeyboardMarkup, CallbackQuery, \
    InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ContentType
from app import cart, btnbar, btnMenu, btnTime, btnBrn, btndlv, sos
from config import dp, db, bot, DELIVERY_CHAT, TOKEN_PAYMENTS
from filters import IsUser
from hendlers.admin.add import check_markup, back_message, all_right_message, back_markup, confirm_markup, \
    confirm_message, back
from hendlers.user.dostavka import dyl_start, projarkas, garnishs, sauces
from aiogram.utils.callback_data import CallbackData

b54 = KeyboardButton("📞 Отправить свой номер", request_contact=True)
send_phone = ReplyKeyboardMarkup(resize_keyboard=True).add(b54)

dostavka = "🎒 ДОСТАВКА"
samovyvoz = "🚗 САМОВЫВОЗ"

product_cb_2 = CallbackData('product', 'id', 'action')


def steak_text(projarka, garnish, sauce):
    text = f"<b>Прожарка</b>: {projarkas.get(projarka)}\n" \
           f"<b>Гарнир</b>: {garnishs.get(garnish)}\n" \
           f"<b>Соус</b>: {sauces.get(sauce)}"

    return text


def wings_text(spice, amount):
    if spice == 'not_spicy':
        spice = 'не острые'
    elif spice == 'medium_spice':
        spice = 'средние'
    elif spice == 'spicy':
        spice = 'острые'

    text = f"<b>Острота</b>: {spice}\n" \
           f"<b>Количество</b>: {amount} штук"

    return text


def product_markup_2(idx, count):
    global product_cb_2

    markup = InlineKeyboardMarkup()
    back_btn = InlineKeyboardButton('➖', callback_data=product_cb_2.new(id=idx, action='decrease'))
    count_btn = InlineKeyboardButton(count, callback_data=product_cb_2.new(id=idx, action='count'))
    next_btn = InlineKeyboardButton('➕️', callback_data=product_cb_2.new(id=idx, action='increase'))

    markup.row(back_btn, count_btn, next_btn)

    return markup


@dp.message_handler(IsUser(), text=cart)
async def process_cart(message: types.Message, state: FSMContext):
    cart_data = db.fetchall(
        'SELECT * FROM cart WHERE cid=?', (message.chat.id,))
    if len(cart_data) == 0:
        await message.answer('Ваша корзина пуста.')
    else:
        await bot.send_chat_action(message.chat.id, ChatActions.TYPING)
        async with state.proxy() as data:
            data['products'] = {}
        order_cost = 0

        for _, idx, count_in_cart, projarka, garnish, sauce, amount, spice in cart_data:
            product = db.fetchone('SELECT * FROM products WHERE idx=?', (idx,))
            if product is None:
                db.query('DELETE FROM cart WHERE idx=?', (idx,))
            else:
                _, title, body, image, price, _ = product

                markup = product_markup_2(idx, count_in_cart)
                text = f'<b>{title}</b>\n'
                info = ""

                if projarka:
                    info = steak_text(projarka, garnish, sauce)

                elif spice:
                    info = wings_text(spice, amount)

                    price = price.split("/")

                    if amount == "8":
                        price = int(price[0])
                    elif amount == "16":
                        price = int(price[1])

                text += info

                text += f"\n\n\nЦена: {price}₽."

                if image:
                    await message.answer_photo(photo=image,
                                               caption=text,
                                               reply_markup=markup)
                else:
                    await message.answer(text=text, reply_markup=markup)

                order_cost += price
                async with state.proxy() as data:
                    if data['products'].get(idx):
                        idx += "2"

                    data['products'][idx] = [title, price, count_in_cart, info]

        if order_cost != 0:
            markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
            markup.add('📦 Оформить заказ', "🗑 Очистить корзину").add(back)

            await message.answer('Отличный выбор, теперь эти блюда в корзине.\n'
                                 'Нажмите на кнопки оформить заказ или назад',
                                 reply_markup=markup)


@dp.message_handler(IsUser(), text=back)
async def back_menu(message: types.Message):
    await dyl_start(message)


@dp.callback_query_handler(IsUser(), product_cb_2.filter(action=['count', 'increase', 'decrease']))
async def product_callback_handler(query: CallbackQuery, callback_data: dict, state: FSMContext):
    idx = callback_data['id']
    action = callback_data['action']
    if 'count' == action:
        async with state.proxy() as data:
            if 'products' not in data.keys():
                await process_cart(query.message, state)
            else:
                await query.answer(f'Количество - {data["products"][idx][2]}')
    else:
        async with state.proxy() as data:
            if 'products' not in data.keys():
                await process_cart(query.message, state)
            else:
                data['products'][idx][2] += 1 if 'increase' == action else -1
                count_in_cart = data['products'][idx][2]
                if count_in_cart <= 0:
                    db.query('''DELETE FROM cart
                    WHERE cid = ? AND idx = ?''', (query.message.chat.id, idx))
                    await query.message.delete()
                else:
                    db.query('''UPDATE cart
                        SET quantity = ?
                    WHERE cid = ? AND idx = ?''', (count_in_cart, query.message.chat.id, idx))
                    await query.message.edit_reply_markup(product_markup_2(idx, count_in_cart))


class CheckoutState(StatesGroup):
    check_cart = State()
    dylevery = State()
    name = State()
    address = State()
    phone_number = State()
    confirm = State()


successful_payment = '''
Ура! Платеж совершен успешно! Приятного аппетита!'''

MESSAGE = {
    'title': db.fetchone("""SELECT title FROM products WHERE idx IN (SELECT idx FROM cart)"""),
    'description': db.fetchone("""SELECT body FROM products WHERE idx IN (SELECT idx FROM cart)"""),
    'label': db.fetchone("""SELECT title FROM products"""),
    'photo_url': db.fetchone("""SELECT photo FROM products WHERE idx IN(SELECT idx FROM cart)"""),
    'successful_payments': successful_payment,
    'count': db.fetchone("""SELECT quantity FROM cart"""),
    'price': 'СЧЕТ НА ОПЛАТУ'
}


@dp.message_handler(IsUser(), text="🗑 Очистить корзину")
async def delete_cart(message: types.Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(btnMenu, btnbar, btnTime).add(btnBrn, btndlv, sos)
    db.query("""DELETE FROM cart WHERE cid=?""", (message.chat.id,))
    await message.answer("Готово", reply_markup=markup)


@dp.message_handler(IsUser(), text='📦 Оформить заказ')
async def process_checkout(message: Message, state: FSMContext):
    async with state.proxy() as data:
        total_price = 0
        for title, price, count_in_cart, info in data['products'].values():
            tp = count_in_cart * price
            total_price += tp
        if total_price < 2000:
            await message.answer(f"Закажите ещё на {2000 - total_price} рублей чтобы совершить заказ")
        else:
            await CheckoutState.check_cart.set()
            await checkout(message, state)


async def checkout(message, state):
    global MESSAGE
    answer = ''
    total_price = 0

    async with state.proxy() as data:
        for title, price, count_in_cart, info in data['products'].values():
            if count_in_cart > 0:
                tp = count_in_cart * price
                answer += f'<b>{title}</b> * {count_in_cart}шт. = {tp}₽\n'
                total_price += tp
    await message.answer(f'{answer}\nОбщая сумма заказа: {total_price}₽.',
                         reply_markup=check_markup())


@dp.pre_checkout_query_handler()
async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    print('order_info')
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@dp.message_handler(IsUser(), lambda message: message.text not in [all_right_message, back_message],
                    state=CheckoutState.check_cart)
async def process_check_cart_invalid(message: Message):
    await message.reply('Такого варианта не было.')


@dp.message_handler(IsUser(), text=back_message, state=CheckoutState.check_cart)
async def process_check_cart_back(message: types.Message, state: FSMContext):
    await state.finish()
    await process_cart(message, state)


@dp.message_handler(IsUser(), text=all_right_message, state=CheckoutState.check_cart)
async def chek_dyl(message: types.Message, state: FSMContext):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(dostavka, samovyvoz).add(back_message)
    await CheckoutState.next()
    await message.answer("Укажите вариант доставки\n"
                         "ДОСТАВКА ОСУЩЕСТВЛЯЕТСЯ ТОЛЬКО ПО г.КАЗАНЬ", reply_markup=markup)


@dp.message_handler(IsUser(), text=back_message, state=CheckoutState.dylevery)
async def process_check_cart_back(message: types.Message, state: FSMContext):
    await process_checkout(message, state)


@dp.message_handler(IsUser(), text=dostavka, state=CheckoutState.dylevery)
async def dylevery(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['dylevery'] = message.text
        await CheckoutState.next()
        await message.answer('Укажите свое имя.',
                             reply_markup=back_markup())
        # await confirm(message, state)


@dp.message_handler(IsUser(), text=samovyvoz, state=CheckoutState.dylevery)
async def dylevery(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['dylevery'] = message.text
        await CheckoutState.next()
        await message.answer('Укажите свое имя.',
                             reply_markup=back_markup())
        # await confirm(message, state)


@dp.message_handler(IsUser(), text=back_message, state=CheckoutState.address)
async def process_address_back(message: Message, state: FSMContext):
    async with state.proxy() as data:
        await message.answer('Изменить имя с <b>' + data['name'] + '</b>?',
                             reply_markup=back_markup())

    await CheckoutState.name.set()


@dp.message_handler(IsUser(), text=back_message, state=CheckoutState.name)
async def process_name_back(message: Message, state: FSMContext):
    await CheckoutState.check_cart.set()
    await checkout(message, state)


@dp.message_handler(IsUser(), state=CheckoutState.name)
async def process_name(message: Message, state: FSMContext):
    async with state.proxy() as data:

        data['name'] = message.text

        if data['dylevery'] == samovyvoz:
            await CheckoutState.phone_number.set()
            await message.answer("Так, теперь мне нужен Ваш номер телефона.\n"
                                 "Исключительно в деловых целях 🙂", reply_markup=send_phone)
        # if 'address' in data.keys():
        #
        #     await confirm(message, state)
        #     await CheckoutState.confirm.set()

        else:
            await message.answer('Укажите адрес доставки:\n'
                                 '1. Название улицы\n'
                                 '2. Номер подъезда\n'
                                 '3. Этаж\n'
                                 '4. Квартира/офис\n'
                                 '5. Код домофона', reply_markup=back_markup())
            await CheckoutState.next()


@dp.message_handler(IsUser(), text=back_message, state=CheckoutState.confirm)
async def process_confirm(message: Message, state: FSMContext):
    async with state.proxy() as data:
        if data['dylevery'] == dostavka:
            await CheckoutState.address.set()
            await message.answer('Изменить адрес с <b>' + data['address'] + '</b>?',
                                 reply_markup=back_markup())
        else:
            await CheckoutState.name.set()
            await message.answer('Изменить имя с <b>' + data['name'] + '</b>?',
                                 reply_markup=back_markup())


@dp.message_handler(IsUser(), state=CheckoutState.address)
async def process_address(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['address'] = message.text

        # await confirm(message)
        await CheckoutState.next()
        await message.answer("Так, теперь мне нужен Ваш номер телефона.\n"
                             "Исключительно в деловых целях 🙂", reply_markup=send_phone)


# @dp.message_handler(IsUser(), text=back_message, state=CheckoutState.confirm)
# async def check_phone(message: types.Message, state: FSMContext):
#     async with state.proxy() as data:
#         await message.answer('Изменить номер телефона с <b>' + data['phone_number'] + '</b>',
#                              reply_markup=back_markup())
#     await CheckoutState.phone_number.set()


@dp.message_handler(IsUser(), state=CheckoutState.phone_number)
async def process_phone_number(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['phone_number'] = message.text

    await CheckoutState.next()
    await confirm(message, state, message.text)


@dp.message_handler(IsUser(), content_types=ContentType.CONTACT, state=CheckoutState.phone_number)
async def handle_contact(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['phone_number'] = message.contact['phone_number']

    await CheckoutState.next()
    await confirm(message, state, message.contact['phone_number'])


async def confirm(message, state, phone_number):
    async with state.proxy() as data:
        total_price = 0
        an = ''
        for title, price, count_in_cart, info in data['products'].values():
            tp = count_in_cart * price
            an += f'<b>{title}</b> - {count_in_cart}шт\n{info}\n\n'
            total_price += tp

        address = ""

        if data['dylevery'] == dostavka:
            variant = "Доставка"
            address = f"Адрес доставки: {data['address']}\n"
        else:
            variant = "Самовывоз"

        text = f"Убедитесь, что все правильно оформлено и подтвердите заказ.\n\n" \
               f"<b>Данные заказа</b>\n" \
               f"Способ получения: {variant}\n" \
               f"{address}" \
               f"Получатель: {data['name']}\n" \
               f"Номер телефона получателя: {phone_number}\n" \
               f"Общая стоимость: {total_price} рублей\n\n" \
               f"Ваш заказ:\n{an}"

        if data['dylevery'] == samovyvoz:
            text += "Хостес вам перезвонит для подтверждения заказа"

        await message.answer(text, reply_markup=confirm_markup())


@dp.message_handler(IsUser(), lambda message: message.text not in [confirm_message, back_message],
                    state=CheckoutState.confirm)
async def process_confirm_invalid(message: Message):
    await message.reply('Такого варианта не было.')


@dp.message_handler(IsUser(), text=confirm_message, state=CheckoutState.confirm)
async def process_confirm(message: Message, state: FSMContext):
    global MESSAGE
    total_price = 0
    async with state.proxy() as data:
        for title, price, count_in_cart, info in data['products'].values():
            tp = count_in_cart * price
            total_price += tp
        total_price *= 100
        PRICE = types.LabeledPrice(label=MESSAGE['price'], amount=total_price)
        await bot.send_invoice(message.chat.id,
                               title=MESSAGE['price'],
                               description="Оплата",
                               provider_token=TOKEN_PAYMENTS,
                               currency='rub',
                               is_flexible=False,  # True If you need to set up Shipping Fee
                               prices=[PRICE],
                               need_phone_number=False,
                               need_shipping_address=False,
                               start_parameter='time-machine-example',
                               payload='some-invoice-payload-for-our-internal-use')

        cid = message.chat.id
        products = [idx + '=' + str(quantity)
                    for idx, quantity in db.fetchall('''SELECT idx, quantity FROM cart
            WHERE cid=?''', (cid,))]  # idx=quantity
        if data['dylevery'] == samovyvoz:
            db.query("INSERT INTO orders VALUES (?, ?, 'False,', ?, ?)",
                     (cid, data['name'], data['phone_number'], ' '.join(products)))
        else:
            db.query('INSERT INTO orders VALUES (?, ?, ?, ?, ?)',
                     (cid, data['name'], data['address'], data['phone_number'], ' '.join(products)))

            # db.query('DELETE FROM cart WHERE cid=?', (cid,))

        await CheckoutState.next()


@dp.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT)
async def process_successful_payment(message: types.Message, state: FSMContext):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(btnMenu, btnbar, btnTime).add(btnBrn, btndlv, sos)
    pmnt = message.successful_payment.to_python()
    for key, val in pmnt.items():
        print(f'{key} = {val}')
    await bot.send_message(
        message.chat.id, MESSAGE['successful_payments'], reply_markup=markup)
    async with state.proxy() as data:
        total_price = 0
        an = ''

        for title, price, count_in_cart, info in data['products'].values():
            tp = count_in_cart * price
            an += f'<b>{title}</b> - {count_in_cart}шт = {tp}рублей\n{info}\n\n'
            total_price += tp
        now = datetime.now()

        address = ""

        if data['dylevery'] == dostavka:
            variant = "Доставка"
            address = f"Адрес доставки: {data['address']}\n"
        else:
            variant = "Самовывоз"

        await bot.send_message(DELIVERY_CHAT, f"<b>{variant}</b>\n\n"
                                             f"Имя получателя: {data['name']}\n"
                                             f"Время: {now.hour}:{now.minute}\n"
                                             f"Дата: {now.date().strftime('%d-%m-%y')}\n"
                                             f"Способ получения: {data['dylevery']}\n"
                                             f"{address}"
                                             f"Номер телефона: {data['phone_number']}\n"
                                             f"Общая стоимость: {total_price} рублей\n"
                                             f"\n"
                                             f"Блюдо: \n"
                                             f"{an}")
        db.query("""DELETE FROM cart WHERE cid=?""", (message.chat.id,))

    await state.finish()
