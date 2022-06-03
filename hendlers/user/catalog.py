from config import dp, bot
from aiogram import types
from aiogram.types import ReplyKeyboardMarkup
from filters import IsUser
from app import btnMenu, btnbar, btnTime, btnBrn, btndlv, cart

"""btn_bar"""
btnvin_po_bakal = "🍾 АПЕРЕТИВ"
btnvin_bel = "🥂 БЕЛЫЕ ВИНА"
btnvin_kras = "🍷 КРАСНЫЕ ВИНА"
btnviski = "🥃 ВИСКИ, РОМ, КОНЬЯК"
btnvodka = "🍸 ВОДКА, ДЖИН, ТЕКИЛА"
btnpivo = "🍺 ПИВО"
btnbez = "☕ БЕЗ АЛКОГОЛЬНЫЕ НАПИТКИ"
"""btn_menu"""
btnkitchen = "🍱 ХОЛОДНЫЕ И ГОРЯЧИЕ ЗАКУСКИ"
btndes = "🍮 ДЕСЕРТЫ"
btnbzn = "🥗 САЛАТЫ"
btnsup = "🍲 СУПЫ"
btnkids = "👶 ДЕТСКОЕ МЕНЮ"
btngor = "🥙 ГОРЯЧИЕ БЛЮДА"
btngril = "🥩 GRILL-СТЕЙКИ"
btnsous = "🍽 СОУСА И ГАРНИРЫ"
btnnaz = "🔙 НАЗАД"


@dp.message_handler(IsUser(), text=btnMenu)
async def catalog(message: types.Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(btnkitchen, btnbzn, btngril).add(btngor, btnsup, btnkids).add(btnsous, btndes, btnnaz)
    await message.answer("ВЫБЕРИТЕ РАЗДЕЛ", reply_markup=markup)


@dp.message_handler(IsUser(), text=btnbar)
async def catalog(message: types.Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(btnvin_po_bakal, btnvin_bel, btnvin_kras).add(btnviski, btnvodka, btnpivo).add(btnbez, btnnaz)
    await message.answer("ВЫБЕРИТЕ РАЗДЕЛ", reply_markup=markup)
"""handler menu"""


@dp.message_handler(IsUser(), text=btnkitchen)
async def btn_kitchen(message: types.Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(btnkitchen, btnbzn, btngril).add(btngor, btnsup, btnkids).add(btnsous, btndes, btnnaz)
    await message.answer("https://telegra.ph/Menyu-04-20-2", reply_markup=markup)


@dp.message_handler(IsUser(), text=btnbzn)
async def btn_bzn(message: types.Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(btnkitchen, btnbzn, btngril).add(btngor, btnsup, btnkids).add(btnsous, btndes, btnnaz)
    await message.answer("https://telegra.ph/Menyu-04-20-3", reply_markup=markup)


@dp.message_handler(IsUser(), text=btngril)
async def btn_gril(message: types.Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(btnkitchen, btnbzn, btngril).add(btngor, btnsup, btnkids).add(btnsous, btndes, btnnaz)
    await message.answer("https://telegra.ph/MENYU-04-20-4", reply_markup=markup)


@dp.message_handler(IsUser(), text=btngor)
async def btn_gor(message: types.Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(btnkitchen, btnbzn, btngril).add(btngor, btnsup, btnkids).add(btnsous, btndes, btnnaz)
    await message.answer("https://telegra.ph/MENYU-04-20-5", reply_markup=markup)


@dp.message_handler(IsUser(), text=btnsup)
async def btn_sup(message: types.Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(btnkitchen, btnbzn, btngril).add(btngor, btnsup, btnkids).add(btnsous, btndes, btnnaz)
    await message.answer("https://telegra.ph/MENYU-04-20-6", reply_markup=markup)


@dp.message_handler(IsUser(), text=btnkids)
async def btn_kids(message: types.Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(btnkitchen, btnbzn, btngril).add(btngor, btnsup, btnkids).add(btnsous, btndes, btnnaz)
    await message.answer("https://telegra.ph/MENYU-04-20-7", reply_markup=markup)


@dp.message_handler(IsUser(), text=btnsous)
async def btn_sous(message: types.Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(btnkitchen, btnbzn, btngril).add(btngor, btnsup, btnkids).add(btnsous, btndes, btnnaz)
    await message.answer("https://telegra.ph/MENYU-04-20-8", reply_markup=markup)


@dp.message_handler(IsUser(), text=btndes)
async def btn_des(message: types.Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(btnkitchen, btnbzn, btngril).add(btngor, btnsup, btnkids).add(btnsous, btndes, btnnaz)
    await message.answer("https://telegra.ph/MENYU-04-20-9", reply_markup=markup)


@dp.message_handler(IsUser(), text=btnnaz)
async def btn_naz(message: types.Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(btnMenu, btnbar, btnTime).add(btnBrn, btndlv)
    await message.answer("ПЕРЕХОД НА ГЛАВНОЕ МЕНЮ", reply_markup=markup)


"""handler_bar"""


@dp.message_handler(IsUser(), text=btnvin_po_bakal)
async def btnvin_pobok(message: types.Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(btnvin_po_bakal, btnvin_bel, btnvin_kras).add(btnviski, btnvodka, btnpivo).add(btnbez, btnnaz)
    await message.answer("https://telegra.ph/BAR-04-20-3", reply_markup=markup)


@dp.message_handler(IsUser(), text=btnvin_bel)
async def btn_bel(message: types.Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(btnvin_po_bakal, btnvin_bel, btnvin_kras).add(btnviski, btnvodka, btnpivo).add(btnbez, btnnaz)
    await message.answer("https://telegra.ph/BAR-04-20-2", reply_markup=markup)


@dp.message_handler(IsUser(), text=btnvin_kras)
async def btn_kras(message: types.Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(btnvin_po_bakal, btnvin_bel, btnvin_kras).add(btnviski, btnvodka, btnpivo).add(btnbez, btnnaz)
    await message.answer("https://telegra.ph/BAR-04-20-4", reply_markup=markup)


@dp.message_handler(IsUser(), text=btnviski)
async def btn_viski(message: types.Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(btnvin_po_bakal, btnvin_bel, btnvin_kras).add(btnviski, btnvodka, btnpivo).add(btnbez, btnnaz)
    await message.answer("https://telegra.ph/BAR-04-20-5", reply_markup=markup)


@dp.message_handler(IsUser(), text=btnvodka)
async def btn_vodka(message: types.Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(btnvin_po_bakal, btnvin_bel, btnvin_kras).add(btnviski, btnvodka, btnpivo).add(btnbez, btnnaz)
    await message.answer("https://telegra.ph/BAR-04-20-6", reply_markup=markup)


@dp.message_handler(IsUser(), text=btnpivo)
async def btn_pivo(message: types.Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(btnvin_po_bakal, btnvin_bel, btnvin_kras).add(btnviski, btnvodka, btnpivo).add(btnbez, btnnaz)
    await message.answer("https://telegra.ph/BAR-04-20-7", reply_markup=markup)


@dp.message_handler(IsUser(), text=btnbez)
async def btn_bez(message: types.Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(btnvin_po_bakal, btnvin_bel, btnvin_kras).add(btnviski, btnvodka, btnpivo).add(btnbez, btnnaz)
    await message.answer("https://telegra.ph/BAR-04-20-8", reply_markup=markup)


