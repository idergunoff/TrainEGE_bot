from button import *
from func.func_subtopic import *
from func.func_user import check_admin


    ######################
    ### Список подтем  ###
    ######################


@dp.message_handler(text='Темы')
@logger.catch
async def open_topics(msg: types.Message):
    logger.info(f'User "{msg.from_user.id} - {msg.from_user.username}" PUSH "btn_topic"')
    kb_topic = InlineKeyboardMarkup(row_width=2)
    topics = await get_topics()
    if len(topics) > 0:
        for i in topics:
            kb_topic.insert(InlineKeyboardButton(text=f'{i.index}. {i.title}', callback_data=cb_topic.new(topic_id=i.id)))
    if await check_admin(msg.from_user.id):
        kb_topic.row(btn_new_topic, btn_index_topic).row(btn_edit_topic, btn_delete_topic)
    mes = emojize('Выберите тему:')
    await bot.send_message(msg.from_user.id, mes, reply_markup=kb_topic)


    ######################
    ### Добавить тему  ###
    ######################


@dp.callback_query_handler(text='new_topic')
@logger.catch
async def new_topic(call: types.CallbackQuery):
    logger.info(f'User "{call.from_user.id} - {call.from_user.username}" PUSH "new_topic"')
    await TrainStates.NEW_TOPIC.set()
    await bot.send_message(call.from_user.id, 'Отправь название темы.')
    await call.answer()


@dp.message_handler(state=TrainStates.NEW_TOPIC)
@logger.catch
async def add_topic(msg: types.Message, state: FSMContext):
    if await check_topic(msg.text) > 0:
        logger.warning(f'USER "{msg.from_user.id} - {msg.from_user.username}" DB HAVE TOPIC {msg.text} ')
        mes = f'Тема <b>{msg.text}</b> уже существует. Отправь другое название.'
        await bot.send_message(msg.from_user.id, mes)
    else:
        await state.finish()
        await add_new_topic(msg.text)
        logger.success(f'USER "{msg.from_user.id} - {msg.from_user.username}" ADD TOPIC {msg.text}')
        mes = emojize(f'Тема <b>{msg.text}</b> добавлена.')
        await bot.send_message(msg.from_user.id, mes)
        await open_topics(msg=msg)


    ####################
    ### Порядок тем  ###
    ####################


@dp.callback_query_handler(text='index_topic')
@logger.catch
async def index_topic(call: types.CallbackQuery):
    logger.info(f'User "{call.from_user.id} - {call.from_user.username}" PUSH "btn_index_topic"')
    kb_topic = InlineKeyboardMarkup(row_width=2)
    topics = await get_topics()
    for i in topics:
        kb_topic.insert(InlineKeyboardButton(text=f'{i.index}. {i.title}', callback_data=cb_index_topic.new(topic_id=i.id)))
    kb_topic.row(btn_back_topic)
    mes = emojize('Выберите тему для изменения порядкого номера:')
    await call.message.edit_text(mes, reply_markup=kb_topic)
    await call.answer()


@dp.callback_query_handler(cb_index_topic.filter())
@logger.catch
async def choose_topic_index(call: types.CallbackQuery, callback_data: dict):
    topic_for_index = await topic_by_id(callback_data['topic_id'])
    logger.info(f'User "{call.from_user.id} - {call.from_user.username}" CHOOSE topic "{topic_for_index.title}" for index')
    topics = await get_topics()
    mes = emojize(f'Переместите тему <b>{topic_for_index.title}</b> выше или ниже\n')
    for i in topics:
        mes += emojize(f'\n<b>-- {str(i.index)}. {i.title} --</b>') if i.id == int(callback_data['topic_id']) else \
            emojize(f'\n{str(i.index)}. {i.title}')
    btn_up_topic = InlineKeyboardButton(emojize(':up_arrow:'), callback_data=cb_up_down_index.new(
        topic_id=callback_data['topic_id'], up_down='up'))
    btn_down_topic = InlineKeyboardButton(emojize(':down_arrow:'), callback_data=cb_up_down_index.new(
        topic_id=callback_data['topic_id'], up_down='down'))
    kb_index = InlineKeyboardMarkup(row_width=3)
    if topic_for_index.index > 1:
        kb_index.insert(btn_up_topic)
    max_index = await get_topic_max_index()
    if topic_for_index.index < max_index[0]:
        kb_index.insert(btn_down_topic)
    kb_index.insert(btn_back_topic)
    try:
        await call.message.edit_text(mes, reply_markup=kb_index)
    except MessageNotModified:
        pass
    await call.answer()


@dp.callback_query_handler(cb_up_down_index.filter())
@logger.catch
async def up_down_priority(call: types.CallbackQuery, callback_data: dict):
    topic_for_index = await topic_by_id(callback_data['topic_id'])
    if callback_data['up_down'] == 'up':
        logger.info(f'User "{call.from_user.id} - {call.from_user.username}" PUSH up category "{topic_for_index.title}"')
        await up_down_topic(callback_data['topic_id'], 'up')
    elif callback_data['up_down'] == 'down':
        logger.info(f'User "{call.from_user.id} - {call.from_user.username}" PUSH down category "{topic_for_index.title}"')
        await up_down_topic(callback_data['topic_id'], 'down')
    await choose_topic_index(call=call, callback_data=callback_data)


    ###########################
    ### Назад к списку тем  ###
    ###########################


@dp.callback_query_handler(text='back_topic')
@logger.catch
async def back_topic(call: types.CallbackQuery):
    logger.info(f'User "{call.from_user.id} - {call.from_user.username}" PUSH "back_topic"')
    kb_topic = InlineKeyboardMarkup(row_width=2)
    topics = await get_topics()
    if len(topics) > 0:
        for i in topics:
            kb_topic.insert(
                InlineKeyboardButton(text=f'{i.index}. {i.title}', callback_data=cb_topic.new(topic_id=i.id)))
    if await check_admin(call.from_user.id):
        kb_topic.row(btn_new_topic, btn_index_topic).row(btn_edit_topic, btn_delete_topic)
    mes = emojize('Выберите тему:')
    await call.message.edit_text(mes, reply_markup=kb_topic)
    await call.answer()


    ######################
    ### Изменить тему  ###
    ######################


@dp.callback_query_handler(text='edit_topic')
@logger.catch
async def choose_edit_topic(call: types.CallbackQuery):
    logger.info(f'User "{call.from_user.id} - {call.from_user.username}" PUSH "btn_edit_topic"')
    kb_topic = InlineKeyboardMarkup(row_width=2)
    topics = await get_topics()
    for i in topics:
        kb_topic.insert(InlineKeyboardButton(text=f'{i.index}. {i.title}', callback_data=cb_edit_topic.new(topic_id=i.id)))
    kb_topic.row(btn_back_topic)
    mes = emojize('Выберите тему для редактирования:')
    await call.message.edit_text(mes, reply_markup=kb_topic)


@dp.callback_query_handler(cb_edit_topic.filter())
@logger.catch
async def edit_topic(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    topic = await topic_by_id(callback_data['topic_id'])
    logger.info(f'User "{call.from_user.id} - {call.from_user.username}" CHOOSE {topic.title} for edit')
    await TrainStates.EDIT_TOPIC.set()
    await state.update_data(topic_id=callback_data['topic_id'])
    await call.message.edit_text(f'Отправь новое название для темы <b>{topic.title}</b>.')
    await call.answer()


@dp.message_handler(state=TrainStates.EDIT_TOPIC)
@logger.catch
async def edit_topic_db(msg: types.Message, state: FSMContext):
    if await check_topic(msg.text) > 0:
        logger.warning(f'USER "{msg.from_user.id} - {msg.from_user.username}" DB HAVE TOPIC {msg.text} EDIT')
        mes = f'Тема <b>{msg.text}</b> уже существует. Отправь другое название.'
        await bot.send_message(msg.from_user.id, mes)
    else:
        topic_data = await state.get_data()
        await state.finish()
        await update_topic(msg.text, topic_data['topic_id'])
        logger.success(f'USER "{msg.from_user.id} - {msg.from_user.username}" UPDATE topic {msg.text}')
        mes = emojize(f'Тема изменена на <b>{msg.text}</b>.')
        await bot.send_message(msg.from_user.id, mes)
        await open_topics(msg=msg)


    #####################
    ### удалить тему  ###
    #####################


@dp.callback_query_handler(text='delete_topic')
@logger.catch
async def choose_topic_delete(call: types.CallbackQuery):
    logger.info(f'User "{call.from_user.id} - {call.from_user.username}" PUSH "btn_delete_topic"')
    kb_topic = InlineKeyboardMarkup(row_width=2)
    topics = await get_topics()
    for i in topics:
        kb_topic.insert(InlineKeyboardButton(text=f'{i.index}. {i.title}', callback_data=cb_delete_topic.new(topic_id=i.id)))
    kb_topic.row(btn_back_topic)
    mes = emojize('Выберите тему для удаления:')
    await call.message.edit_text(mes, reply_markup=kb_topic)


@dp.callback_query_handler(cb_delete_topic.filter())
@logger.catch
async def delete_topic_db(call: types.CallbackQuery, callback_data: dict):
    topic = await topic_by_id(callback_data['topic_id'])
    topic_title = topic.title
    count_subt = await count_subtopic(callback_data['topic_id'])
    if count_subt > 0:
        mes = f'Невозможно удалить тему <b>{topic_title}</b> пока она содержит подтемы, сначала удалите все подтемы.'
        logger.error(f'User "{call.from_user.id} - {call.from_user.username}" TOPIC NOT EMPTY')
    else:
        await delete_topic(callback_data['topic_id'])
        mes = f'Тема <b>{topic_title}</b> удалена.'
        logger.success(f'User "{call.from_user.id} - {call.from_user.username}" TOPIC {topic_title} DELETE')
    await bot.send_message(call.from_user.id, mes)
    await back_topic(call=call)
