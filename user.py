from button import *
from func.func_user import *


@dp.message_handler(commands=['start'])
@logger.catch
async def start(msg: types.Message):
    if not await check_user(msg.from_user.id):
        name_list = []
        if msg.from_user.first_name:
            name_list.append(msg.from_user.first_name)
        if msg.from_user.last_name:
            name_list.append(msg.from_user.last_name)
        user_name = ' '.join(name_list)
        await add_user(msg.from_user.id, user_name)
        logger.success(f'Add new user - {user_name}; {msg.from_user.id}')
    mes = emojize(msg.from_user.first_name + ", добро пожаловать в бот \n<b>Подготовка к ЕГЭ</b>! \n:waving_hand:")
    kb = kb_start_reg if await check_admin(msg.from_user.id) or await check_user_year(msg.from_user.id) else kb_start_unreg
    await bot.send_message(msg.from_user.id, mes, reply_markup=kb)
    logger.info(f'Push "/start" - user "{msg.from_user.id} - {msg.from_user.username}"')