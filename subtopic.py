from button import *
from func.func_subtopic import *
from func.func_user import check_admin
from func.func_topic import topic_by_id


    ######################
    ### Список подтем  ###
    ######################


@dp.callback_query_handler(cb_topic.filter())
@logger.catch
async def open_subtopics(call: types.CallbackQuery, callback_data: dict):
    topic = await topic_by_id(callback_data['topic_id'])
    logger.info(f'User "{call.from_user.id} - {call.from_user.username}" OPEN TOPIC "{topic.title}"')
    kb_subtopic = InlineKeyboardMarkup(row_width=2)
    subtopics = await get_subtopics(topic.id)
    if len(subtopics) > 0:
        for i in subtopics:
            kb_subtopic.insert(InlineKeyboardButton(text=f'{topic.index}.{i.index}. {i.title}', callback_data=cb_subtopic.new(sub_id=i.id)))
    if await check_admin(call.from_user.id):
        btn_new_subtopic = InlineKeyboardButton(
            text=emojize('Новая подтема:memo:'),
            callback_data=cb_subtopic_menu.new(topic_id=topic.id, type='new'))
        btn_index_subtopic = InlineKeyboardButton(
            text=emojize('Порядок подтем:up-down_arrow:'),
            callback_data=cb_subtopic_menu.new(topic_id=topic.id, type='index'))
        btn_edit_subtopic = InlineKeyboardButton(
            text=emojize('Изменить подтему:wrench:'),
            callback_data=cb_subtopic_menu.new(topic_id=topic.id, type='edit'))
        btn_delete_subtopic = InlineKeyboardButton(
            text=emojize('Удалить подтему:wastebasket:'),
            callback_data=cb_subtopic_menu.new(topic_id=topic.id, type='delete'))
        kb_subtopic.row(btn_new_subtopic, btn_index_subtopic).row(btn_edit_subtopic, btn_delete_subtopic)
    kb_subtopic.row(btn_back_topic)
    mes = emojize(f'Тема <b>"{topic.title}"</b>.\nВыберите подтему:')
    await call.message.edit_text(mes, reply_markup=kb_subtopic)
    await call.answer()


    #########################
    ### Добавить подтему  ###
    #########################


@dp.callback_query_handler(cb_subtopic_menu.filter())
@logger.catch
async def new_subtopic(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    await state.update_data(topic_id=callback_data['topic_id'])
    topic = await topic_by_id(callback_data['topic_id'])
    if callback_data['type'] == 'new':
        logger.info(f'User "{call.from_user.id} - {call.from_user.username}" PUSH "new_subtopic"')
        await TrainStates.NEW_SUBTOPIC.set()
        await bot.send_message(call.from_user.id, 'Отправь название подтемы.')
    elif callback_data['type'] == 'index':
        logger.info(f'User "{call.from_user.id} - {call.from_user.username}" PUSH "index_subtopic"')
        await TrainStates.INDEX_SUBTOPIC.set()
        kb_subtopic = InlineKeyboardMarkup(row_width=2)
        subtopics = await get_subtopics(callback_data['topic_id'])
        for i in subtopics:
            kb_subtopic.insert(InlineKeyboardButton(
                text=f'{topic.index}.{i.index}. {i.title}',
                callback_data=cb_index_subtopic.new(sub_id=i.id)))
        kb_subtopic.insert(InlineKeyboardButton(
                text=emojize(':BACK_arrow:Назад'),
                callback_data=cb_back_subtopic.new(topic_id=topic.id)))
        mes = emojize('Выберите подтему для изменения порядкого номера:')
        await call.message.edit_text(mes, reply_markup=kb_subtopic)
        await call.answer()
    elif callback_data['type'] == 'edit':
        logger.info(f'User "{call.from_user.id} - {call.from_user.username}" PUSH "btn_edit_subtopic"')
        await TrainStates.CHOOSE_EDIT_SUBTOPIC.set()
        kb_subtopic = InlineKeyboardMarkup(row_width=2)
        subtopics = await get_subtopics(topic.id)
        for i in subtopics:
            kb_subtopic.insert(InlineKeyboardButton(
                text=f'{topic.index}.{i.index}. {i.title}',
                callback_data=cb_edit_subtopic.new(sub_id=i.id)))
        kb_subtopic.insert(InlineKeyboardButton(
            text=emojize(':BACK_arrow:Назад'),
            callback_data=cb_back_subtopic.new(topic_id=topic.id)))
        mes = emojize('Выберите подтему для редактирования:')
        await call.message.edit_text(mes, reply_markup=kb_subtopic)
    elif callback_data['type'] == 'delete':
        logger.info(f'User "{call.from_user.id} - {call.from_user.username}" PUSH "btn_delete_subtopic"')
        await TrainStates.CHOOSE_DELETE_SUBTOPIC.set()
        kb_subtopic = InlineKeyboardMarkup(row_width=2)
        subtopics = await get_subtopics(topic.id)
        for i in subtopics:
            kb_subtopic.insert(
                InlineKeyboardButton(text=f'{topic.index}.{i.index}. {i.title}',
                callback_data=cb_delete_subtopic.new(sub_id=i.id)))
        kb_subtopic.insert(InlineKeyboardButton(
            text=emojize(':BACK_arrow:Назад'),
            callback_data=cb_back_subtopic.new(topic_id=topic.id)))
        mes = emojize('Выберите подтему для удаления:')
        await call.message.edit_text(mes, reply_markup=kb_subtopic)
    await call.answer()


@dp.message_handler(state=TrainStates.NEW_SUBTOPIC)
@logger.catch
async def add_subtopic(msg: types.Message, state: FSMContext):
    user_data = await state.get_data()
    topic_id = user_data['topic_id']
    topic = await topic_by_id(topic_id)
    if await check_subtopic(msg.text, topic_id) > 0:
        logger.warning(f'USER "{msg.from_user.id} - {msg.from_user.username}" DB HAVE SUBTOPIC {msg.text} ')
        mes = f'Подтема <b>{msg.text}</b> уже существует в разделе <b>"{topic.title}"</b>. Отправь другое название.'
        await bot.send_message(msg.from_user.id, mes)
    else:
        await state.finish()
        await add_new_subtopic(msg.text, topic_id)
        logger.success(f'USER "{msg.from_user.id} - {msg.from_user.username}" ADD SUBTOPIC {msg.text}')
        mes = emojize(f'Подтема <b>{msg.text}</b> добавлена в раздел <b>"{topic.title}"</b>.')
        await bot.send_message(msg.from_user.id, mes)
        kb_subtopic = InlineKeyboardMarkup(row_width=2)
        subtopics = await get_subtopics(topic.id)
        if len(subtopics) > 0:
            for i in subtopics:
                kb_subtopic.insert(InlineKeyboardButton(text=f'{topic.index}.{i.index}. {i.title}',
                                                        callback_data=cb_subtopic.new(sub_id=i.id)))
        if await check_admin(msg.from_user.id):
            btn_new_subtopic = InlineKeyboardButton(
                text=emojize('Новая подтема:memo:'),
                callback_data=cb_subtopic_menu.new(topic_id=topic.id, type='new'))
            btn_index_subtopic = InlineKeyboardButton(
                text=emojize('Порядок подтем:up-down_arrow:'),
                callback_data=cb_subtopic_menu.new(topic_id=topic.id, type='index'))
            btn_edit_subtopic = InlineKeyboardButton(
                text=emojize('Изменить подтему:wrench:'),
                callback_data=cb_subtopic_menu.new(topic_id=topic.id, type='edit'))
            btn_delete_subtopic = InlineKeyboardButton(
                text=emojize('Удалить подтему:wastebasket:'),
                callback_data=cb_subtopic_menu.new(topic_id=topic.id, type='delete'))
            kb_subtopic.row(btn_new_subtopic, btn_index_subtopic).row(btn_edit_subtopic, btn_delete_subtopic)
        kb_subtopic.row(btn_back_topic)
        mes = emojize(f'Тема <b>"{topic.title}"</b>.\nВыберите подтему:')
        await bot.send_message(msg.from_user.id, mes, reply_markup=kb_subtopic)


    #######################
    ### Порядок подтем  ###
    #######################


@dp.callback_query_handler(cb_index_subtopic.filter(), state=TrainStates.INDEX_SUBTOPIC)
@logger.catch
async def choose_subtopic_index(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    user_data = await state.get_data()
    topic_id = user_data['topic_id']
    topic = await topic_by_id(topic_id)
    subtopic_for_index = await subtopic_by_id(callback_data['sub_id'])
    logger.info(f'User "{call.from_user.id} - {call.from_user.username}" CHOOSE subtopic "{subtopic_for_index.title}" for index')
    subtopics = await get_subtopics(topic_id)
    mes = emojize(f'Переместите подтему <b>{subtopic_for_index.title}</b> выше или ниже\n')
    for i in subtopics:
        mes += emojize(f'\n<b>-- {topic.index}.{str(i.index)}. {i.title} --</b>') if i.id == int(callback_data['sub_id']) else \
            emojize(f'\n{topic.index}.{str(i.index)}. {i.title}')
    btn_up_subtopic = InlineKeyboardButton(emojize(':up_arrow:'), callback_data=cb_up_down_index_subtopic.new(
        sub_id=callback_data['sub_id'], up_down='up'))
    btn_down_subtopic = InlineKeyboardButton(emojize(':down_arrow:'), callback_data=cb_up_down_index_subtopic.new(
        sub_id=callback_data['sub_id'], up_down='down'))
    kb_index = InlineKeyboardMarkup(row_width=3)
    if subtopic_for_index.index > 1:
        kb_index.insert(btn_up_subtopic)
    max_index = await get_subtopic_max_index(topic_id)
    if subtopic_for_index.index < max_index[0]:
        kb_index.insert(btn_down_subtopic)
    kb_index.insert(InlineKeyboardButton(
                text=emojize(':BACK_arrow:Назад'),
                callback_data=cb_back_subtopic.new(topic_id=topic.id)))
    try:
        await call.message.edit_text(mes, reply_markup=kb_index)
    except MessageNotModified:
        pass
    await call.answer()


@dp.callback_query_handler(cb_up_down_index_subtopic.filter(), state=TrainStates.INDEX_SUBTOPIC)
@logger.catch
async def up_down_index_subtopic(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    subtopic_for_index = await subtopic_by_id(callback_data['sub_id'])
    if callback_data['up_down'] == 'up':
        logger.info(f'User "{call.from_user.id} - {call.from_user.username}" PUSH up index "{subtopic_for_index.title}"')
        await up_down_subtopic(callback_data['sub_id'], 'up')
    elif callback_data['up_down'] == 'down':
        logger.info(f'User "{call.from_user.id} - {call.from_user.username}" PUSH down index "{subtopic_for_index.title}"')
        await up_down_subtopic(callback_data['sub_id'], 'down')
    await choose_subtopic_index(call=call, callback_data=callback_data, state=state)


    ##############################
    ### Назад к списку подтем  ###
    ##############################


@dp.callback_query_handler(cb_back_subtopic.filter(), state=[
    TrainStates.INDEX_SUBTOPIC,
    TrainStates.CHOOSE_EDIT_SUBTOPIC,
    TrainStates.CHOOSE_DELETE_SUBTOPIC
])
@logger.catch
async def back_subtopic(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    logger.info(f'User "{call.from_user.id} - {call.from_user.username}" PUSH "back_subtopic"')
    await state.finish()
    topic = await topic_by_id(callback_data['topic_id'])
    logger.info(f'User "{call.from_user.id} - {call.from_user.username}" OPEN TOPIC "{topic.title}"')
    kb_subtopic = InlineKeyboardMarkup(row_width=2)
    subtopics = await get_subtopics(topic.id)
    if len(subtopics) > 0:
        for i in subtopics:
            kb_subtopic.insert(InlineKeyboardButton(text=f'{topic.index}.{i.index}. {i.title}',
                                                    callback_data=cb_subtopic.new(sub_id=i.id)))
    if await check_admin(call.from_user.id):
        btn_new_subtopic = InlineKeyboardButton(
            text=emojize('Новая подтема:memo:'),
            callback_data=cb_subtopic_menu.new(topic_id=topic.id, type='new'))
        btn_index_subtopic = InlineKeyboardButton(
            text=emojize('Порядок подтем:up-down_arrow:'),
            callback_data=cb_subtopic_menu.new(topic_id=topic.id, type='index'))
        btn_edit_subtopic = InlineKeyboardButton(
            text=emojize('Изменить подтему:wrench:'),
            callback_data=cb_subtopic_menu.new(topic_id=topic.id, type='edit'))
        btn_delete_subtopic = InlineKeyboardButton(
            text=emojize('Удалить подтему:wastebasket:'),
            callback_data=cb_subtopic_menu.new(topic_id=topic.id, type='delete'))
        kb_subtopic.row(btn_new_subtopic, btn_index_subtopic).row(btn_edit_subtopic, btn_delete_subtopic)
    kb_subtopic.row(btn_back_topic)
    mes = emojize(f'Тема <b>"{topic.title}"</b>.\nВыберите подтему:')
    await call.message.edit_text(mes, reply_markup=kb_subtopic)
    await call.answer()


    #########################
    ### Изменить подтему  ###
    #########################


@dp.callback_query_handler(cb_edit_subtopic.filter(), state=TrainStates.CHOOSE_EDIT_SUBTOPIC)
@logger.catch
async def edit_subtopic(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    subtopic = await subtopic_by_id(callback_data['sub_id'])
    logger.info(f'User "{call.from_user.id} - {call.from_user.username}" CHOOSE {subtopic.title} for edit')
    await TrainStates.EDIT_SUBTOPIC.set()
    await state.update_data(sub_id=callback_data['sub_id'])
    await call.message.edit_text(f'Отправь новое название для подтемы <b>{subtopic.title}</b>.')
    await call.answer()


@dp.message_handler(state=TrainStates.EDIT_SUBTOPIC)
@logger.catch
async def edit_subtopic_db(msg: types.Message, state: FSMContext):
    user_data = await state.get_data()
    subtopic = await subtopic_by_id(user_data['sub_id'])
    if await check_subtopic(msg.text, subtopic.topic_id) > 0:
        logger.warning(f'USER "{msg.from_user.id} - {msg.from_user.username}" DB HAVE SUBTOPIC {msg.text} EDIT')
        mes = f'Подтема <b>{msg.text}</b> уже существует в разделе <b>"{subtopic.topic.title}"</b>. Отправь другое название.'
        await bot.send_message(msg.from_user.id, mes)
    else:
        await state.finish()
        await update_subtopic(msg.text, user_data['sub_id'])
        logger.success(f'USER "{msg.from_user.id} - {msg.from_user.username}" UPDATE subtopic {msg.text}')
        mes = emojize(f'Подтема изменена на <b>{msg.text}</b>.')
        await bot.send_message(msg.from_user.id, mes)
        topic = await topic_by_id(subtopic.topic_id)
        kb_subtopic = InlineKeyboardMarkup(row_width=2)
        subtopics = await get_subtopics(topic.id)
        if len(subtopics) > 0:
            for i in subtopics:
                kb_subtopic.insert(InlineKeyboardButton(text=f'{topic.index}.{i.index}. {i.title}',
                                                        callback_data=cb_subtopic.new(sub_id=i.id)))
        if await check_admin(msg.from_user.id):
            btn_new_subtopic = InlineKeyboardButton(
                text=emojize('Новая подтема:memo:'),
                callback_data=cb_subtopic_menu.new(topic_id=topic.id, type='new'))
            btn_index_subtopic = InlineKeyboardButton(
                text=emojize('Порядок подтем:up-down_arrow:'),
                callback_data=cb_subtopic_menu.new(topic_id=topic.id, type='index'))
            btn_edit_subtopic = InlineKeyboardButton(
                text=emojize('Изменить подтему:wrench:'),
                callback_data=cb_subtopic_menu.new(topic_id=topic.id, type='edit'))
            btn_delete_subtopic = InlineKeyboardButton(
                text=emojize('Удалить подтему:wastebasket:'),
                callback_data=cb_subtopic_menu.new(topic_id=topic.id, type='delete'))
            kb_subtopic.row(btn_new_subtopic, btn_index_subtopic).row(btn_edit_subtopic, btn_delete_subtopic)
        kb_subtopic.row(btn_back_topic)
        mes = emojize(f'Тема <b>"{topic.title}"</b>.\nВыберите подтему:')
        await bot.send_message(msg.from_user.id, mes, reply_markup=kb_subtopic)


    ########################
    ### удалить подтему  ###
    ########################


@dp.callback_query_handler(cb_delete_subtopic.filter(), state=TrainStates.CHOOSE_DELETE_SUBTOPIC)
@logger.catch
async def delete_subtopic_db(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    await state.finish()
    subtopic = await subtopic_by_id(callback_data['sub_id'])
    subtopic_title = subtopic.title
    topic_id = subtopic.topic_id
    count_quest = await count_questions(callback_data['sub_id'])
    if count_quest > 0:
        mes = f'Невозможно удалить подтему <b>{subtopic_title}</b> пока она содержит вопросы, сначала удалите все вопросы.'
        logger.error(f'User "{call.from_user.id} - {call.from_user.username}" SUBTOPIC NOT EMPTY')
    else:
        await delete_subtopic(callback_data['sub_id'])
        mes = f'Подтема <b>{subtopic_title}</b> удалена.'
        logger.success(f'User "{call.from_user.id} - {call.from_user.username}" SUBTOPIC {subtopic_title} DELETE')
    await bot.send_message(call.from_user.id, mes)
    kb_subtopic = InlineKeyboardMarkup(row_width=2)
    topic = await topic_by_id(topic_id)
    subtopics = await get_subtopics(topic_id)
    if len(subtopics) > 0:
        for i in subtopics:
            kb_subtopic.insert(InlineKeyboardButton(text=f'{topic.index}.{i.index}. {i.title}',
                                                    callback_data=cb_subtopic.new(sub_id=i.id)))
    if await check_admin(call.from_user.id):
        btn_new_subtopic = InlineKeyboardButton(
            text=emojize('Новая подтема:memo:'),
            callback_data=cb_subtopic_menu.new(topic_id=topic.id, type='new'))
        btn_index_subtopic = InlineKeyboardButton(
            text=emojize('Порядок подтем:up-down_arrow:'),
            callback_data=cb_subtopic_menu.new(topic_id=topic.id, type='index'))
        btn_edit_subtopic = InlineKeyboardButton(
            text=emojize('Изменить подтему:wrench:'),
            callback_data=cb_subtopic_menu.new(topic_id=topic.id, type='edit'))
        btn_delete_subtopic = InlineKeyboardButton(
            text=emojize('Удалить подтему:wastebasket:'),
            callback_data=cb_subtopic_menu.new(topic_id=topic.id, type='delete'))
        kb_subtopic.row(btn_new_subtopic, btn_index_subtopic).row(btn_edit_subtopic, btn_delete_subtopic)
    kb_subtopic.row(btn_back_topic)
    mes = emojize(f'Тема <b>"{topic.title}"</b>.\nВыберите подтему:')
    await bot.send_message(call.from_user.id, mes, reply_markup=kb_subtopic)
