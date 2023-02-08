from func.func_exam import *
from func.func_question import question_by_id
from func.func_user import get_admins, user_by_id


@dp.callback_query_handler(cb_exam_subtopic.filter())
@logger.catch
async def start_exam_subtopic(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    # todo проверка, есть ли начатый тест
    exam_id = await add_new_exam(call.from_user.id, 'sub')
    await create_tasks_sub_exam(call.from_user.id, callback_data['sub_id'], exam_id)
    await TrainStates.EXAM.set()
    task = await get_task(call.from_user.id)
    await state.update_data(quest_id=task.question_id, exam_id=exam_id, task_id=task.id)
    quest = await question_by_id(task.question_id)
    mes = f'Отправьте ответ на задание <b>{quest.subtopic.topic.index}.{quest.subtopic.index}.{quest.index}</b>'
    await bot.send_photo(task.user_id, quest.link, caption=mes)
    await start_task(task.id)
    await call.answer()


@dp.message_handler(state=TrainStates.EXAM)
@logger.catch
async def accept_answer(msg: types.Message, state: FSMContext):
    user_data = await state.get_data()
    quest = await question_by_id(user_data['quest_id'])
    point = await check_answer(msg.text, quest, user_data['task_id'])
    mes = f'Вы ответили <b>{msg.text}</b> на задание <b>{quest.subtopic.topic.index}.{quest.subtopic.index}.{quest.index}</b>' \
          f'\nЭто {"правильный" if point else "не правильный"} ответ.'
    await msg.reply(mes)
    task = await get_task(msg.from_user.id)
    if task:
        await state.update_data(quest_id=task.question_id, task_id=task.id)
        quest = await question_by_id(task.question_id)
        mes = f'Отправьте ответ на задание <b>{quest.subtopic.topic.index}.{quest.subtopic.index}.{quest.index}</b>'
        await bot.send_photo(task.user_id, quest.link, caption=mes)
        await start_task(task.id)
    else:
        await state.finish()
        test_name = await get_test_name(user_data['exam_id'])
        report = await create_report(user_data['exam_id'])
        mes = f'Вы ответили на все вопросы {test_name}. Ваш результат:\n' + report
        await bot.send_message(msg.from_user.id, mes)
        user = await user_by_id(msg.from_user.id)
        mes = f'Результаты {test_name} пользователя <b>{user.surname} {user.name} ({user.year})</b>:\n' + report
        for admin in await get_admins():
            await bot.send_message(admin.t_id, mes)
