from aiogram.dispatcher.filters.state import StatesGroup, State
from config import bot, dp, db, BRON_CHANNEL
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove
from hendlers.admin.add import submit_markup, all_right_message, cancel_message
from aiogram.types import Message
from filters import IsUser
from hendlers.user.reserved import send_phone
from aiogram.types import ContentType
from hendlers.user.catalog import btnnaz
from app import sos, btnMenu, btnbar, btnTime, btnBrn, btndlv

message_to = "✉ Написать сообщение"
phone = "📞 Позвонить"
back_message = '👈 Назад'


class SosState(StatesGroup):
    question = State()
    phone_number = State()
    submit = State()


@dp.message_handler(IsUser(), text=sos)
async def command_start(message: Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(message_to, phone)
    markup.add(btnnaz)
    await message.answer("Как хотите с нами связаться", reply_markup=markup)


@dp.message_handler(IsUser(), text=phone)
async def command_phone(message: Message):
    await message.answer("Свяжитесь пожалуйста с нами по номеру телефона\n"
                         "+7 (843) 266‒11‒11")


@dp.message_handler(IsUser(), text=message_to)
async def command_message(message: Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(back_message)
    await SosState.question.set()
    await message.answer('В чем суть проблемы? Опишите как можно детальнее и администратор обязательно вам ответит.',
                         reply_markup=markup)


@dp.message_handler(IsUser(), state=SosState.question)
async def procces_phone(message: Message, state: FSMContext):
    async with state.proxy() as data:
        if message.text != back_message:
            data['question'] = message.text
            await message.answer("Введите номер телефона пожалуйста.", reply_markup=send_phone)
            await SosState.next()
        else:
            markup = ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(btnMenu, btnbar, btnTime)
            markup.add(btnBrn, btndlv, sos)
            await message.answer('Отменено!', reply_markup=markup)
            await state.finish()


@dp.message_handler(IsUser(), state=SosState.phone_number)
async def process_question(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['phone_number'] = message.text

    await message.answer('Убедитесь, что все верно.', reply_markup=submit_markup())
    await SosState.next()


@dp.message_handler(content_types=ContentType.CONTACT, state=SosState.phone_number)
async def process_question(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['phone_number'] = message.contact['phone_number']

    await message.answer('Убедитесь, что все верно.', reply_markup=submit_markup())
    await SosState.next()


@dp.message_handler(lambda message: message.text not in [cancel_message, all_right_message], state=SosState.submit)
async def process_price_invalid(message: Message):
    await message.answer('Такого варианта не было.')


@dp.message_handler(text=cancel_message, state=SosState.submit)
async def process_cancel(message: Message, state: FSMContext):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(btnMenu, btnbar, btnTime)
    markup.add(btnBrn, btndlv, sos)
    await message.answer('Отменено!', reply_markup=markup)
    await state.finish()


@dp.message_handler(text=all_right_message, state=SosState.submit)
async def process_submit(message: Message, state: FSMContext):
    cid = message.chat.id
    async with state.proxy() as data:
        db.query('INSERT INTO questions VALUES (?, ?)',
                 (cid, data['question']))
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(btnMenu, btnbar, btnTime)
        markup.add(btnBrn, btndlv, sos)
        await message.answer('Отправлено!', reply_markup=markup)
        await bot.send_message(BRON_CHANNEL, "SOS\n"
                                             "\n"
                                             f"Вопрос: {data['question']}\n"
                                             f"Номер телефона отправителя: {data['phone_number']}")

    await state.finish()
