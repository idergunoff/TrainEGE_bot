from aiogram import Bot, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram import types
from aiogram.utils.exceptions import MessageCantBeDeleted, BadRequest, MessageNotModified
from aiogram.utils import exceptions
from loguru import logger

from model import *
import datetime

TOKEN = '5579063326:AAHLjyssE2Bi8AqPX8qb6qUZR3_-Keonr1Q'


session = Session()

logger.add("file_{time}.log", format="{time} - {level} - {message}", level="TRACE", rotation="7 day")


bot = Bot(token=TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())