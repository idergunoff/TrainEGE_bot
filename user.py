from button import *
from func.func_user import *


@dp.message_handler(commands=['start'])
@logger.catch
async def start(msg: types.Message):
    logger.info(f'Push "/start" - user "{msg.from_user.id} - {msg.from_user.username}"')
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
    if await check_admin(msg.from_user.id):
        kb = kb_start_admin
    elif await check_user_year(msg.from_user.id):
        kb = kb_start_reg
    else:
        kb = kb_start_unreg
    await bot.send_message(msg.from_user.id, mes, reply_markup=kb)


@dp.message_handler(text=emojize('Регистрация:crystal_ball:'))
@logger.catch
async def start_registration(msg: types.Message):
    logger.info(f'User "{msg.from_user.id} - {msg.from_user.username}" START REGISTRATON')
    await TrainStates.REG_SURNAME.set()
    await bot.send_message(msg.from_user.id, 'Отправьте вашу фамилию')


@dp.message_handler(state=TrainStates.REG_SURNAME)
@logger.catch
async def registration_surname(msg: types.Message, state: FSMContext):
    logger.info(f'User "{msg.from_user.id} - {msg.from_user.username}" SEND REGISTRATON SURNAME')
    await TrainStates.REG_NAME.set()
    await state.update_data(surname=msg.text)
    await bot.send_message(msg.from_user.id, 'Отправьте ваше имя')


@dp.message_handler(state=TrainStates.REG_NAME)
@logger.catch
async def registration_name(msg: types.Message, state: FSMContext):
    logger.info(f'User "{msg.from_user.id} - {msg.from_user.username}" SEND REGISTRATON NAME')
    await TrainStates.REG_YEAR.set()
    await state.update_data(name=msg.text)
    await bot.send_message(msg.from_user.id, 'Отправьте год экзамена')


@dp.message_handler(state=TrainStates.REG_YEAR)
@logger.catch
async def registration_year(msg: types.Message, state: FSMContext):
    logger.info(f'User "{msg.from_user.id} - {msg.from_user.username}" SEND REGISTRATON YEAR')
    user_data = await state.get_data()
    await state.finish()
    if await check_user_reg(user_data['name'], user_data['surname'], msg.text):
        logger.warning(f'User "{msg.from_user.id} - {msg.from_user.username}" ERROR REG EXIST')
        message = f'Аккаунт <b>{user_data["surname"]} {user_data["name"]}, {msg.text}</b> уже существует. ' \
                  f'Если это не ваш аккаунт, пройдите регистрацию заново, добавив какую-либо пометку к имени или фамилии, например, год рождения.'
        kb = kb_start_reg if await check_admin(msg.from_user.id) or await check_user_year(msg.from_user.id) else kb_start_unreg
        await bot.send_message(msg.from_user.id, message, reply_markup=kb)
        return
    await user_registration(msg.from_user.id, user_data['name'], user_data['surname'], msg.text)
    logger.success(f'User "{msg.from_user.id} - {msg.from_user.username}" REG SUCCESS')
    kb = kb_start_reg if await check_admin(msg.from_user.id) or await check_user_year(msg.from_user.id) else kb_start_unreg
    await bot.send_message(
        msg.from_user.id,
        'Успешная регистрация. Ожидайте подтверждения регистрации от администратора для получения доступа к вопросам.',
        reply_markup=kb)
    kb_verify = InlineKeyboardMarkup(row_width=2)
    btn_yes = InlineKeyboardButton('Да', callback_data=cb_verify.new(t_id=msg.from_user.id, yesno='yes'))
    btn_no = InlineKeyboardButton('Нет', callback_data=cb_verify.new(t_id=msg.from_user.id, yesno='no'))
    kb_verify.row(btn_yes, btn_no)
    message = f'Новый пользователь - <b>{user_data["surname"]} {user_data["name"]}, {msg.text}</b>. Предоставить доступ к заданиям для данного пользователя?'
    for admin in await get_admins():
        await bot.send_message(admin.t_id, message, reply_markup=kb_verify)


@dp.callback_query_handler(cb_verify.filter())
@logger.catch
async def user_verify(call: types.CallbackQuery, callback_data: dict):
    user = await user_by_id(callback_data['t_id'])
    if callback_data['yesno'] == 'yes':
        await verify_user_db(callback_data['t_id'])
        message = 'Вам предоставлен доступ к вопросам'
        message_admin = f'Пользователю <b>{user.surname} {user.name}, {user.year}</b> предоставлен доступ к вопросам.'
        logger.info(f'User "{call.from_user.id} - {call.from_user.username}" VERIFY YES')
    else:
        message = 'Вам отказано в доступе к вопросам'
        message_admin = f'Пользователю <b>{user.surname} {user.name}, {user.year}</b> отказано в доступе к вопросам.'
        logger.info(f'User "{call.from_user.id} - {call.from_user.username}" VERIFY NO')
    await bot.send_message(callback_data['t_id'], message, reply_markup=kb_start_reg)
    for admin in await get_admins():
        await bot.send_message(admin.t_id, message_admin)
    await call.message.delete()
