from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from misc.config import *
from misc.database import *
from misc.marketapi import Lolz

storage = MemoryStorage()
bot = Bot(token)
dp = Dispatcher(bot, storage=storage)
lzt = Lolz(lolz_token)
connect()