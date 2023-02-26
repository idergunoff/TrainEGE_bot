from func.func_question import get_questions
from func.func_stat import *


@dp.message_handler(text=emojize('Статистика:bar_chart:'))
@logger.catch
async def open_stat(msg: types.Message):
    if not await check_admin(msg.from_user.id):
        return
    years = await get_list_years()
    mes = await create_text_users_stat(years[-1])
    kb_stat = await create_kb_users_stat(years[-1])
    await add_kb_year(kb_stat, years[-1])
    await bot.send_message(msg.from_user.id, mes, reply_markup=kb_stat)


@dp.callback_query_handler(cb_years.filter())
@logger.catch
async def choose_year(call: types.CallbackQuery, callback_data: dict):
    years = await get_list_years()
    mes = await create_text_users_stat(callback_data['year'])
    kb_stat = await create_kb_users_stat(callback_data['year'])
    await add_kb_year(kb_stat, callback_data['year'])
    await call.message.edit_text(mes, reply_markup=kb_stat)
    await call.answer()


@dp.callback_query_handler(cb_user_stat.filter())
@logger.catch
async def open_stat_user(call: types.CallbackQuery, callback_data: dict):
    kb_user_stat = await create_kb_user_top_stat(callback_data['t_id'], 'und')
    await draw_understand_top_graph(callback_data['t_id'])
    user = await user_by_id(callback_data['t_id'])
    photo_input = types.InputFile('graph.jpg')
    mes = f'Понимаемость тем <b>{user.surname} {user.name} ({user.year})</b>'
    await bot.send_photo(call.from_user.id, photo_input, caption=mes, reply_markup=kb_user_stat)
    await call.answer()


@dp.callback_query_handler(cb_graph_top.filter())
@logger.catch
async def top_graph_stat(call: types.CallbackQuery, callback_data: dict):
    user = await user_by_id(callback_data['t_id'])
    if callback_data['type'] == 'execute':
        kb_user_stat = await create_kb_user_top_stat(callback_data['t_id'], 'und')
        await draw_understand_top_graph(callback_data['t_id'])
        mes = f'Понимаемость тем <b>{user.surname} {user.name} ({user.year})</b>'
    else:
        kb_user_stat = await create_kb_user_top_stat(callback_data['t_id'])
        await draw_execute_top_graph(callback_data['t_id'])
        mes = f'Выполняемость тем <b>{user.surname} {user.name} ({user.year})</b>'
    photo_input = types.InputFile('graph.jpg')
    photo = InputMedia(
            type='photo',
            media=photo_input,
            caption=mes)
    await call.message.edit_media(photo, reply_markup=kb_user_stat)
    await call.answer()


@dp.callback_query_handler(text='back_stat')
@logger.catch
async def back_stat(call: types.CallbackQuery):
    await call.message.delete()


@dp.callback_query_handler(cb_top_stat.filter())
@logger.catch
async def open_top_stat_user(call: types.CallbackQuery, callback_data: dict):
    kb_user_top_stat = await create_kb_user_sub_stat(callback_data['t_id'], callback_data['top_id'], 'und')
    await draw_understand_sub_graph(callback_data['top_id'], callback_data['t_id'])
    user = await user_by_id(callback_data['t_id'])
    topic = await topic_by_id(callback_data['top_id'])
    photo_input = types.InputFile('graph.jpg')
    mes = f'Понимаемость подтем ({topic.title}) <b>{user.surname} {user.name} ({user.year})</b>\n'
    photo = InputMedia(
            type='photo',
            media=photo_input,
            caption=mes)
    await call.message.edit_media(photo, reply_markup=kb_user_top_stat)
    await call.answer()


@dp.callback_query_handler(cb_graph_sub.filter())
@logger.catch
async def sub_graph_stat(call: types.CallbackQuery, callback_data: dict):
    user = await user_by_id(callback_data['t_id'])
    topic = await topic_by_id(callback_data['top_id'])
    if callback_data['type'] == 'execute':
        kb_user_top_stat = await create_kb_user_sub_stat(callback_data['t_id'], callback_data['top_id'], 'und')
        await draw_understand_sub_graph(callback_data['top_id'], callback_data['t_id'])
        mes = f'Понимаемость подтем ({topic.title}) <b>{user.surname} {user.name} ({user.year})</b>\n'
    else:
        kb_user_top_stat = await create_kb_user_sub_stat(callback_data['t_id'], callback_data['top_id'])
        await draw_execute_sub_graph(callback_data['top_id'], callback_data['t_id'])
        mes = f'Выполняемость подтем ({topic.title}) <b>{user.surname} {user.name} ({user.year})</b>'
    photo_input = types.InputFile('graph.jpg')
    photo = InputMedia(
        type='photo',
        media=photo_input,
        caption=mes)
    try:
        await call.message.edit_media(photo, reply_markup=kb_user_top_stat)
    except MessageNotModified:
        pass
    await call.answer()


@dp.callback_query_handler(cb_back_top_stat.filter())
@logger.catch
async def back_top(call: types.CallbackQuery, callback_data: dict):
    kb_user_stat = await create_kb_user_top_stat(callback_data['t_id'], 'und')
    await draw_understand_top_graph(callback_data['t_id'])
    user = await user_by_id(callback_data['t_id'])
    photo_input = types.InputFile('graph.jpg')
    mes = f'Понимаемость тем <b>{user.surname} {user.name} ({user.year})</b>'
    photo = InputMedia(
        type='photo',
        media=photo_input,
        caption=mes)
    await call.message.edit_media(photo, reply_markup=kb_user_stat)
    await call.answer()


@dp.callback_query_handler(text='description')
@logger.catch
async def show_description(call: types.CallbackQuery):
    mes = '<b><u>Описание графиков</u></b>\n\n' \
        '<b><i>Понимаемость</i></b> (синий) - процент заданий в теме, которые были выполнены дважды подряд правильно, ' \
        'относительно общего количества заданий в теме.\n' \
        '<b><i>Процент правильных выполнений</i></b> (зелёный) - процент всех правильных ответов на задания в теме, ' \
        'относительно общего количества ответов на задания в теме.\n'\
        '<b><i>Всего выполнений</i></b> (красный) - процент выполненных заданий в теме от общего количества ' \
        'выполненных заданий во всех темах.\n' \
        '<b><i>Всего правильных выполнений</i></b> (оранжевый) - процент правильно выполненных заданий в теме от ' \
        'общего количества правильно выполненных заданий во всех темах.\n' \
        '<b><i>Время по теме</i></b> (жёлтый) - процент времени, затраченного на выполнение заданий в теме, от ' \
        'общего времени, затраченного на выполнение заданий во всех темах. Значения над столбцами указаны в минутах.'
    kb_OK = InlineKeyboardMarkup()
    kb_OK.insert(InlineKeyboardButton('OK', callback_data='clear_desc'))
    await bot.send_message(call.from_user.id, mes, reply_markup=kb_OK)
    await call.answer()


@dp.callback_query_handler(text='clear_desc')
@logger.catch
async def clear_description(call: types.CallbackQuery):
    await call.message.delete()


@dp.callback_query_handler(cb_excel_stat.filter())
@logger.catch
async def send_excel_stat(call: types.CallbackQuery, callback_data: dict):
    wb = Workbook()
    ws1 = wb.create_sheet('Статистика по вопросам')
    ws2 = wb.create_sheet('Все решения')
    topics = await get_topics()
    n1, n2 = 1, 1
    for n_top, top in enumerate(topics):
        subtopics = await get_subtopics(top.id)
        for n_sub, sub in enumerate(subtopics):
            cell = ws1.cell(row=n1, column=1)
            cell.value = top.title
            cell = ws1.cell(row=n1, column=2)
            cell.value = sub.title
            questions = await get_questions(sub.id)
            for n_quest, quest in enumerate(questions):
                tasks = session.query(Task).filter(
                    Task.user_id == callback_data['t_id'],
                    Task.question_id == quest.id
                ).order_by(Task.start).all()
                corr_tasks = session.query(Task).filter(
                    Task.user_id == callback_data['t_id'],
                    Task.question_id == quest.id,
                    Task.answer_point == 1
                ).count()
                cell = ws1.cell(row=n1, column=n_quest + 3)
                cell.value = f'{corr_tasks}/{len(tasks)}'
                cell = ws2.cell(row=n2, column=1)
                cell.value = f'{top.index}.{sub.index}.{quest.index}'
                for n_t, t in enumerate(tasks):
                    cell = ws2.cell(row=n2, column=n_t + 2)
                    cell.value = await create_cell_text(t)
                n2 += 1
            n1 += 1
    wb.active = wb['Статистика по вопросам']
    user = await user_by_id(callback_data['t_id'])
    file_name = f'{user.surname}_{user.name}_статистика.xlsx'
    wb.save(file_name)
    await bot.send_document(call.from_user.id, open(file_name, 'rb'))
    os.remove(file_name)
    await call.answer()

