from func.func_subtopic import *
from func.func_user import check_admin
from func.func_subtopic import subtopic_by_id
from func.func_question import *


    #######################
    ### Список вопросов ###
    #######################


@dp.callback_query_handler(cb_subtopic.filter())
@logger.catch
async def open_questions(call: types.CallbackQuery, callback_data: dict):
    subtopic = await subtopic_by_id(callback_data['sub_id'])
    logger.info(f'User "{call.from_user.id} - {call.from_user.username}" OPEN SUBTOPIC "{subtopic.title}"')
    kb_question = InlineKeyboardMarkup(row_width=5)
    if await check_admin(call.from_user.id):
        await create_kb_admin_question(kb_question, subtopic)
    await create_kb_question(kb_question, subtopic)
    mes = emojize(f'Подтема <b>"{subtopic.title}"</b> раздела <b>"{subtopic.topic.title}"</b>.')
    await call.message.edit_text(mes, reply_markup=kb_question)
    await call.answer()


    #########################
    ### Загрузка вопросов ###
    #########################


@dp.callback_query_handler(cb_new_question.filter())
@logger.catch
async def new_question(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    await state.update_data(sub_id=callback_data['sub_id'])
    logger.info(f'User "{call.from_user.id} - {call.from_user.username}" PUSH "new_question"')
    await TrainStates.NEW_QUESTION_PICT.set()
    await bot.send_message(call.from_user.id, 'Отправь изображениес с задачей.')


@dp.message_handler(state=TrainStates.NEW_QUESTION_PICT, content_types=['photo'])
@logger.catch
async def new_question_pict(msg: types.Message, state: FSMContext):
    file_id = msg.photo[-1].file_id
    await state.update_data(link=file_id)
    logger.info(f'User "{msg.from_user.id} - {msg.from_user.username}" SEND "pict_question"')
    await TrainStates.NEW_QUESTION_ANSWER.set()
    await bot.send_message(msg.from_user.id, 'Отправь правильный ответ.')


@dp.message_handler(state=TrainStates.NEW_QUESTION_ANSWER)
@logger.catch
async def new_questions_answer(msg: types.Message, state: FSMContext):
    user_data = await state.get_data()
    logger.info(f'User "{msg.from_user.id} - {msg.from_user.username}" SEND "answer_question"')
    await add_question(user_data['sub_id'], user_data['link'], msg.text)
    await state.finish()
    await bot.send_message(msg.from_user.id, 'Вопрос загружен.')
    subtopic = await subtopic_by_id(user_data['sub_id'])
    kb_question = InlineKeyboardMarkup(row_width=5)
    if await check_admin(msg.from_user.id):
        await create_kb_admin_question(kb_question, subtopic)
    await create_kb_question(kb_question, subtopic)
    mes = emojize(f'Подтема <b>"{subtopic.title}"</b> раздела <b>"{subtopic.topic.title}"</b>.')
    await bot.send_message(msg.from_user.id, mes, reply_markup=kb_question)


    #########################
    ### Просмотр вопросов ###
    #########################


@dp.callback_query_handler(cb_question.filter())
@logger.catch
async def open_current_question(call: types.CallbackQuery, callback_data: dict):
    quest = await question_by_id(callback_data['quest_id'])
    kb_quest = await create_kb_current_quest(quest)
    await bot.send_photo(
            call.from_user.id,
            quest.link,
            caption=f'Вопрос <b>{quest.subtopic.topic.index}.{quest.subtopic.index}.{quest.index}</b> Правильный ответ: <b>{quest.answer}</b>',
            reply_markup=kb_quest
            )
    await call.answer()


@dp.callback_query_handler(cb_question_pict.filter())
@logger.catch
async def next_prev_question(call: types.CallbackQuery, callback_data: dict):
    quest = await question_by_id(callback_data['quest_id'])
    kb_quest = await create_kb_current_quest(quest)
    photo = InputMedia(
            type='photo',
            media=quest.link,
            caption=f'Вопрос <b>{quest.subtopic.topic.index}.{quest.subtopic.index}.{quest.index}</b> Правильный ответ: <b>{quest.answer}</b>')
    await call.message.edit_media(photo, reply_markup=kb_quest)


    ###############################
    ### Назад к списку вопросов ###
    ###############################


@dp.callback_query_handler(cb_back_question.filter())
@logger.catch
async def back_questions(call: types.CallbackQuery, callback_data: dict):
    subtopic = await subtopic_by_id(callback_data['sub_id'])
    logger.info(f'User "{call.from_user.id} - {call.from_user.username}" BACK SUBTOPIC "{subtopic.title}"')
    kb_question = InlineKeyboardMarkup(row_width=5)
    if await check_admin(call.from_user.id):
        await create_kb_admin_question(kb_question, subtopic)
    await create_kb_question(kb_question, subtopic)
    mes = emojize(f'Подтема <b>"{subtopic.title}"</b> раздела <b>"{subtopic.topic.title}"</b>.')
    await bot.send_message(call.from_user.id, mes, reply_markup=kb_question)
    await call.answer()


    #########################
    ### Удаление вопросов ###
    #########################


@dp.callback_query_handler(cb_del_quest.filter())
@logger.catch
async def delete_question(call: types.CallbackQuery, callback_data: dict):
    quest = await question_by_id(callback_data['quest_id'])
    subtopic = await subtopic_by_id(quest.subtopic.id)
    await delete_question_db(callback_data['quest_id'])
    await bot.send_message(call.from_user.id, 'Вопрос удалён')
    logger.success(f'User "{call.from_user.id} - {call.from_user.username}" delete question')
    kb_question = InlineKeyboardMarkup(row_width=5)
    if await check_admin(call.from_user.id):
        await create_kb_admin_question(kb_question, subtopic)
    await create_kb_question(kb_question, subtopic)
    mes = emojize(f'Подтема <b>"{subtopic.title}"</b> раздела <b>"{subtopic.topic.title}"</b>.')
    await bot.send_message(call.from_user.id, mes, reply_markup=kb_question)
    await call.answer()



    ##########################
    ### Изменение вопросов ###
    ##########################


@dp.callback_query_handler(cb_edit_pict_quest.filter())
@logger.catch
async def edit_pict_question(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    logger.info(f'User "{call.from_user.id} - {call.from_user.username}" push edit pict question')
    await state.update_data(quest_id=callback_data['quest_id'])
    await TrainStates.EDIT_PICT_QUEST.set()
    await call.message.edit_caption('Отправь новое изображение для данного вопроса')
    await call.answer()


@dp.message_handler(state=TrainStates.EDIT_PICT_QUEST, content_types=['photo'])
@logger.catch
async def edit_pict_question(msg: types.Message, state: FSMContext):
    file_id = msg.photo[-1].file_id
    logger.info(f'User "{msg.from_user.id} - {msg.from_user.username}" SEND new pict question"')
    user_data = await state.get_data()
    await state.finish()
    await update_pict_question(user_data['quest_id'], file_id)
    quest = await question_by_id(user_data['quest_id'])
    kb_quest = await create_kb_current_quest(quest)
    await bot.send_photo(
            msg.from_user.id,
            quest.link,
            caption=f'Вопрос <b>{quest.subtopic.topic.index}.{quest.subtopic.index}.{quest.index}</b> Правильный ответ: <b>{quest.answer}</b>',
            reply_markup=kb_quest
            )


@dp.callback_query_handler(cb_edit_answer_quest.filter())
@logger.catch
async def edit_answer_question(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    quest = await question_by_id(callback_data['quest_id'])
    old_answer = quest.answer
    logger.info(f'User "{call.from_user.id} - {call.from_user.username}" push edit answer question')
    await state.update_data(quest_id=callback_data['quest_id'])
    await TrainStates.EDIT_ANSWER_QUEST.set()
    await call.message.edit_caption(f'Старый ответ: <b>{old_answer}</b>\nОтправь новый правильный ответ для данного вопроса')
    await call.answer()


@dp.message_handler(state=TrainStates.EDIT_ANSWER_QUEST)
@logger.catch
async def edit_answer_question(msg: types.Message, state: FSMContext):
    logger.info(f'User "{msg.from_user.id} - {msg.from_user.username}" SEND new answer question"')
    user_data = await state.get_data()
    await state.finish()
    await update_answer_question(user_data['quest_id'], msg.text)
    quest = await question_by_id(user_data['quest_id'])
    kb_quest = await create_kb_current_quest(quest)
    await bot.send_photo(
            msg.from_user.id,
            quest.link,
            caption=f'Вопрос <b>{quest.subtopic.topic.index}.{quest.subtopic.index}.{quest.index}</b> Правильный ответ: <b>{quest.answer}</b>',
            reply_markup=kb_quest
            )
