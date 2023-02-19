from config import *
from func.func_user import check_admin


@logger.catch
async def create_text_users_stat(year):
    users = session.query(User).filter_by(year=year, verify=1).order_by(User.surname).all()
    text = f'Cписок пользователей <b>{year}</b> года:\n'
    for n, user in enumerate(users):
        text += f'\n<b>{n+1}.</b> {user.surname} {user.name}'
    text += f'\n\nДля выбора статистики конкретного пользователя, нажмите на кнопку с номером пользователя в списке.'
    return text


@logger.catch
async def create_kb_users_stat(year):
    users = session.query(User).filter_by(year=year, verify=1).order_by(User.surname).all()
    kb_users_stat = InlineKeyboardMarkup(row_width=5)
    for n, user in enumerate(users):
        kb_users_stat.insert(InlineKeyboardButton(text=str(n+1), callback_data=cb_user_stat.new(t_id=user.t_id)))
    return kb_users_stat


@logger.catch
async def add_kb_year(kb, year):
    years = await get_list_years()
    # todo smart row - every 4 button
    for y in years:
        if y == year:
            kb.row(InlineKeyboardButton(text=emojize(f':backhand_index_pointing_right:{y}'), callback_data=0))
        else:
            kb.row(InlineKeyboardButton(text='y', callback_data=cb_years.new(year=y)))
    return kb


@logger.catch
async def get_list_years():
    users = session.query(User).filter_by(verify=1).all()
    years = []
    for user in users:
        if user.year not in years:
            years.append(user.year)
    years.sort()
    return years