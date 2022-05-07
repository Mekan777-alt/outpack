from aiogram import types
from aiogram.dispatcher.filters import BoundFilter
from config import ADMINS


class IsUser(BoundFilter):

    async def check(self, message: types.Message):
        return message.from_user.id not in ADMINS
