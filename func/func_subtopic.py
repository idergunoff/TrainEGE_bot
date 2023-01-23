from config import *
from func.func_topic import topic_by_id


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