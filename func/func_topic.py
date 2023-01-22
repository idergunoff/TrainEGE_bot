from config import *


@logger.catch
async def get_topics():
    return session.query(Topic).order_by(Topic.index).all()


@logger.catch
async def check_topic(topic):
    return session.query(Topic).filter(Topic.title == topic).count()


@logger.catch
async def get_topic_max_index():
    return session.query(Topic.index).order_by(desc(Topic.index)).first()


@logger.catch
async def add_new_topic(text):
    max_index = await get_topic_max_index()
    index = max_index[0] + 1 if max_index else 1
    new_topic = Topic(title=text, index=index)
    session.add(new_topic)
    session.commit()


@logger.catch
async def topic_by_id(id):
    return session.query(Topic).filter(Topic.id == id).first()


@logger.catch
async def up_down_topic(topic_id, updown):
    topic = await topic_by_id(topic_id)
    topic_index = topic.index
    if updown == 'up':
        if topic_index > 1:
            session.query(Topic).filter(Topic.index == topic_index).update({'index': 999},
                                                                                     synchronize_session='fetch')
            session.query(Topic).filter(Topic.index == topic_index - 1).update({'index': topic_index},
                                                                                         synchronize_session='fetch')
            session.query(Topic).filter(Topic.index == 999).update({'index': topic_index - 1},
                                                                                         synchronize_session='fetch')
    elif updown == 'down':
        max_index = await get_topic_max_index()
        if topic_index < max_index[0]:
            session.query(Topic).filter(Topic.index == topic_index).update({'index': 999},
                                                                                     synchronize_session='fetch')
            session.query(Topic).filter(Topic.index == topic_index + 1).update({'index': topic_index},
                                                                                         synchronize_session='fetch')
            session.query(Topic).filter(Topic.index == 999).update({'index': topic_index + 1},
                                                                          synchronize_session='fetch')
    session.commit()


@logger.catch
async def update_topic(text, topic_id):
    session.query(Topic).filter(Topic.id == topic_id).update({'title': text}, synchronize_session='fetch')
    session.commit()


@logger.catch
async def delete_topic(topic_id):
    topic_index = session.query(Topic.index).filter(Topic.id == topic_id).first()[0]
    session.query(Topic).filter(Topic.id == topic_id).delete()
    max_index = await get_topic_max_index()
    for i in range(topic_index + 1, max_index[0] + 1):
        session.query(Topic).filter(Topic.index == i).update({'index': i - 1}, synchronize_session='fetch')
    session.commit()


@logger.catch
async def count_subtopic(topic_id):
    return session.query(Subtopic).filter(Subtopic.topic_id == topic_id).count()
