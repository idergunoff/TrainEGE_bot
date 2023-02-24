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


@dp.callback_query_handler(cb_user_stat.filter())
@logger.catch
async def open_stat_user(call: types.CallbackQuery, callback_data: dict):
    kb_user_stat = await create_kb_user_top_stat(callback_data['t_id'], 'und')
    await draw_understand_top_graph(callback_data['t_id'])
    user = await user_by_id(callback_data['t_id'])
    photo_input = types.InputFile('graph.jpg')
    mes = f'Понимаемость тем <b>{user.surname} {user.name} ({user.year})</b>\n' \
          f'<i>Понимаемость</i> (синим) - процент заданий в теме, которые были выполнены дважды подряд правильно, ' \
          f'относительно общего количества заданий в теме.\n' \
          f'<i>Процент правильных выполнений</i> (зелёным) - процент всех правильных ответов на задания в теме, ' \
          f'относительно общего количества ответов на задания в теме.'
    await bot.send_photo(call.from_user.id, photo_input, caption=mes, reply_markup=kb_user_stat)
    await call.answer()


@dp.callback_query_handler(cb_graph_top.filter())
@logger.catch
async def top_graph_stat(call: types.CallbackQuery, callback_data: dict):
    user = await user_by_id(callback_data['t_id'])
    if callback_data['type'] == 'execute':
        kb_user_stat = await create_kb_user_top_stat(callback_data['t_id'], 'und')
        await draw_understand_top_graph(callback_data['t_id'])
        mes = f'Понимаемость тем <b>{user.surname} {user.name} ({user.year})</b>\n' \
          f'<i>Понимаемость</i> (синим) - процент заданий в теме, которые были выполнены дважды подряд правильно, ' \
          f'относительно общего количества заданий в теме.\n' \
          f'<i>Процент правильных выполнений</i> (зелёным) - процент всех правильных ответов на задания в теме, ' \
          f'относительно общего количества ответов на задания в теме.'
    else:
        kb_user_stat = await create_kb_user_top_stat(callback_data['t_id'])
        await draw_execute_top_graph(callback_data['t_id'])
        mes = f'выполняемость тем <b>{user.surname} {user.name} ({user.year})</b>\n' \
              f'<i>Всего выполнений</i> (красным) - процент выполненных заданий в теме от общего количества ' \
              f'выполненных заданий во всех темах.\n' \
              f'<i>Всего правильных выполнений</i> (оранжевым) - процент правильно выполненных заданий в теме от ' \
              f'общего количества правильно выполненных заданий во всех темах.\n' \
              f'<i>Время по теме</i> (жёлтым) - процент времени, затраченного на выполнение заданий в теме, от ' \
              f'общего времени, затраченного на выполнение заданий во всех темах. Значения над столбцами указаны в минутах.'
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