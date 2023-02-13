from config import *
from button import *
from func.func_user import user_by_id


@logger.catch
async def get_questions(sub_id):
    return session.query(Question).filter(Question.subtopic_id == sub_id).all()


@logger.catch
async def create_kb_admin_question(kb, subtopic):
    questions = await get_questions(subtopic.id)
    if len(questions) > 0:
        for i in questions:
            kb.insert(InlineKeyboardButton(
                text=f'{i.subtopic.topic.index}.{i.subtopic.index}.{i.index}',
                callback_data=cb_question.new(quest_id=i.id))
                )
    kb.row(InlineKeyboardButton('Загрузить вопрос', callback_data=cb_new_question.new(sub_id=subtopic.id)))
    return kb


@logger.catch
async def create_kb_question(kb, subtopic, t_id):
    user = await user_by_id(t_id)
    btn_exam_subtopic = InlineKeyboardButton(f'Тест по подтеме "{subtopic.title}"', callback_data=cb_exam_subtopic.new(sub_id=subtopic.id))
    btn_back_subtopic = InlineKeyboardButton(emojize(':BACK_arrow:Назад'), callback_data=cb_back_subtopic.new(topic_id=subtopic.topic_id))
    if user.verify:
        kb.row(btn_exam_subtopic)
    kb.row(btn_back_subtopic)
    return kb


@logger.catch
async def get_question_max_index(subtopic_id):
    return session.query(Question.index).filter(Question.subtopic_id == subtopic_id).order_by(desc(Question.index)).first()


@logger.catch
async def add_question(sub_id, link, answer):
    max_index = await get_question_max_index(sub_id)
    index = max_index[0] + 1 if max_index else 1
    new_question = Question(subtopic_id=sub_id, link=link, answer=answer, index=index)
    session.add(new_question)
    session.commit()


@logger.catch
async def question_by_id(id):
    return session.query(Question).filter(Question.id == id).first()


@logger.catch
async def create_kb_current_quest(quest):
    kb_quest = InlineKeyboardMarkup(row_width=3)
    list_id = [i.id for i in quest.subtopic.questions]
    index_quest = list_id.index(quest.id)
    index_prev = index_quest - 1 if index_quest != 0 else -1
    index_next = index_quest + 1 if index_quest != len(list_id) - 1 else 0
    btn_prev = InlineKeyboardButton('<<<', callback_data=cb_question_pict.new(quest_id=list_id[index_prev]))
    btn_next = InlineKeyboardButton('>>>', callback_data=cb_question_pict.new(quest_id=list_id[index_next]))
    btn_del = InlineKeyboardButton('Удалить', callback_data=cb_del_quest.new(quest_id=quest.id))
    btn_not_show = InlineKeyboardButton('Убрать', callback_data=cb_not_show_quest.new(quest_id=quest.id))
    btn_show = InlineKeyboardButton('Вернуть', callback_data=cb_show_quest.new(quest_id=quest.id))
    btn_edit_pict = InlineKeyboardButton(
            emojize(':wrench:вопрос'),
            callback_data=cb_edit_pict_quest.new(quest_id=quest.id)
            )
    btn_edit_answ = InlineKeyboardButton(
            emojize(':wrench:ответ'),
            callback_data=cb_edit_answer_quest.new(quest_id=quest.id)
            )
    btn_back = InlineKeyboardButton('Назад', callback_data=cb_back_question.new(sub_id=quest.subtopic_id))
    kb_quest.row(btn_prev, btn_back, btn_next).row(btn_edit_pict, btn_edit_answ)
    if session.query(Task).filter(Task.question_id == quest.id).count() > 0:
        if quest.showing:
            kb_quest.insert(btn_not_show)
        else:
            kb_quest.insert(btn_show)
    else:
        kb_quest.insert(btn_del)
    return kb_quest


@logger.catch
async def delete_question_db(id):
    quest = await question_by_id(id)
    quest_index = session.query(Question.index).filter(Question.id == id).first()[0]
    session.query(Question).filter(Question.id == id).delete()
    max_index = await get_question_max_index(quest.subtopic_id)
    for i in range(quest_index + 1, max_index[0] + 1):
        session.query(Question).filter(Question.index == i).update({'index': i - 1}, synchronize_session='fetch')
    session.commit()


@logger.catch
async def update_not_showing(q_id):
    session.query(Question).filter(Question.id == q_id).update({'showing': 0}, synchronize_session='fetch')
    session.commit()


@logger.catch
async def update_showing(q_id):
    session.query(Question).filter(Question.id == q_id).update({'showing': 1}, synchronize_session='fetch')
    session.commit()


@logger.catch
async def update_pict_question(quest_id, file_id):
    session.query(Question).filter(Question.id == quest_id).update({'link': file_id}, synchronize_session='fetch')
    session.commit()


@logger.catch
async def update_answer_question(quest_id, text):
    session.query(Question).filter(Question.id == quest_id).update({'answer': text}, synchronize_session='fetch')
    session.commit()

