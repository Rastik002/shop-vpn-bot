#!/usr/bin/env python
# -*- coding: utf-8 -*- # строка нужна, чтобы не было ошибки Non-UTF-8 code starting with '\xd1' in file ...
from aiogram.utils import executor
from create_bot import dp
from handlers import user, admin
from misc.config import *

user.register_handlers_user(dp)

if __name__ == '__main__':
	executor.start_polling(dispatcher=dp, skip_updates=True)