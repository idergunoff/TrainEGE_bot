from config import *


@logger.catch
async def check_user(user_id):
    return session.query(User).filter(User.t_id == user_id).first()


@logger.catch
async def check_user_year(user_id):
    return session.query(User.year).filter(User.t_id == user_id).first()[0]


@logger.catch
async def add_user(user_id, user_name):
    new_user = User(t_id=user_id, username=user_name)
    session.add(new_user)
    session.commit()


@logger.catch
async def check_admin(t_id):
    return session.query(User.admin).filter(User.t_id == t_id).first()[0]