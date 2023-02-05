from config import *
from button import *
from func.func_topic import topic_by_id
from func.func_user import user_by_id


@logger.catch
async def get_subtopics(topic_id):
    return session.query(Subtopic).filter(Subtopic.topic_id == topic_id).order_by(Subtopic.index).all()


@logger.catch
async def check_subtopic(msg, topic_id):
    return session.query(Subtopic).filter(Subtopic.title == msg, Subtopic.topic_id == topic_id).count()


@logger.catch
async def get_subtopic_max_index(topic_id):
    return session.query(Subtopic.index).filter(Subtopic.topic_id == topic_id).order_by(desc(Subtopic.index)).first()


@logger.catch
async def add_new_subtopic(text, topic_id):
    max_index = await get_subtopic_max_index(topic_id)
    index = max_index[0] + 1 if max_index else 1
    new_subtopic = Subtopic(title=text, index=index, topic_id=topic_id)
    session.add(new_subtopic)
    session.commit()


@logger.catch
async def subtopic_by_id(id):
    return session.query(Subtopic).filter(Subtopic.id == id).first()


@logger.catch
async def up_down_subtopic(sub_id, updown):
    subtopic = await subtopic_by_id(sub_id)
    subtopic_index = subtopic.index
    if updown == 'up':
        if subtopic_index > 1:
            session.query(Subtopic).filter(
                Subtopic.index == subtopic_index,
                Subtopic.topic_id == subtopic.topic_id
            ).update({'index': 999}, synchronize_session='fetch')
            session.query(Subtopic).filter(
                Subtopic.index == subtopic_index - 1,
                Subtopic.topic_id == subtopic.topic_id
            ).update({'index': subtopic_index}, synchronize_session='fetch')
            session.query(Subtopic).filter(
                Subtopic.index == 999,
                Subtopic.topic_id == subtopic.topic_id
            ).update({'index': subtopic_index - 1}, synchronize_session='fetch')
    elif updown == 'down':
        max_index = await get_subtopic_max_index(subtopic.topic_id)
        if subtopic_index < max_index[0]:
            session.query(Subtopic).filter(
                Subtopic.index == subtopic_index,
                Subtopic.topic_id == subtopic.topic_id
            ).update({'index': 999}, synchronize_session='fetch')
            session.query(Subtopic).filter(
                Subtopic.index == subtopic_index + 1,
                Subtopic.topic_id == subtopic.topic_id
            ).update({'index': subtopic_index}, synchronize_session='fetch')
            session.query(Subtopic).filter(
                Subtopic.index == 999,
                Subtopic.topic_id == subtopic.topic_id
            ).update({'index': subtopic_index + 1}, synchronize_session='fetch')
    session.commit()


@logger.catch
async def update_subtopic(text, sub_id):
    session.query(Subtopic).filter(Subtopic.id == sub_id).update({'title': text}, synchronize_session='fetch')
    session.commit()


@logger.catch
async def delete_subtopic(sub_id):
    subtopic = await subtopic_by_id(sub_id)
    subtopic_index = session.query(Subtopic.index).filter(Subtopic.id == sub_id).first()[0]
    session.query(Subtopic).filter(Subtopic.id == sub_id).delete()
    max_index = await get_subtopic_max_index(subtopic.topic_id)
    for i in range(subtopic_index + 1, max_index[0] + 1):
        session.query(Subtopic).filter(Subtopic.index == i).update({'index': i - 1}, synchronize_session='fetch')
    session.commit()


@logger.catch
async def count_questions(sub_id):
    return session.query(Question).filter(Question.subtopic_id == sub_id).count()


@logger.catch
async def create_kb_subtopic(topic, cb, t_id):
    user = await user_by_id(t_id)
    kb_subtopic = InlineKeyboardMarkup(row_width=2)
    if user.verify:
        kb_subtopic.row(InlineKeyboardButton(text=f'Тест по теме "{topic.title}"', callback_data=cb_exam_topic.new(topic_id=topic.id)))
    subtopics = await get_subtopics(topic.id)
    if len(subtopics) > 0:
        for i in subtopics:
            kb_subtopic.insert(InlineKeyboardButton(text=f'{topic.index}.{i.index}. {i.title}',
                                                    callback_data=cb.new(sub_id=i.id)))
    return kb_subtopic


@logger.catch
async def add_kb_admin(topic, kb):
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
    kb.row(btn_new_subtopic, btn_index_subtopic).row(btn_edit_subtopic, btn_delete_subtopic)
    return kb
