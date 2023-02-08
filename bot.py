from aiogram.utils import executor
from config import *
from topic import *
from subtopic import *
from question import *
from exam import *
from user import *


async def shutdown(dispatcher: Dispatcher):
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()


if __name__ == '__main__':
    executor.start_polling(dp, on_shutdown=shutdown)