from config import *


@logger.catch
async def user_by_id(t_id):
    return session.query(User).filter(User.t_id == t_id).first()


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


@logger.catch
async def check_user_reg(name, surname, year):
    return session.query(User).filter(User.name == name, User.surname == surname, User.year == year).first()


@logger.catch
async def user_registration(t_id, name, surname, year):
    session.query(User).filter(User.t_id == t_id).update({
        'name': name, 'surname': surname, 'year': year
    }, synchronize_session='fetch')
    session.commit()


@logger.catch
async def get_admins():
    return session.query(User).filter(User.admin == 1).all()


@logger.catch
async def verify_user_db(t_id):
    session.query(User).filter(User.t_id == t_id).update({'verify': 1}, synchronize_session='fetch')
    session.commit()