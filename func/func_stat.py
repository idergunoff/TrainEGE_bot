from config import *
from func.func_subtopic import get_subtopics
from func.func_topic import get_topics, topic_by_id
from func.func_user import check_admin, user_by_id


@logger.catch
async def create_text_users_stat(year):
    users = session.query(User).filter_by(year=year, verify=1).order_by(User.surname).all()
    text = f'Cписок пользователей <b>{year}</b> года:\n'
    for n, user in enumerate(users):
        text += f'\n<b>{n+1}.</b> {user.surname} {user.name}'
    text += f'\n\nЧтобы просмотреть статистику определенного пользователя, нажмите на кнопку с его номером в списке.'
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
    for n, y in enumerate(years):
        if str(y) == year:
            if n == 0:
                kb.row(InlineKeyboardButton(text=emojize(f':backhand_index_pointing_right:{y}'), callback_data=0))
            else:
                kb.insert(InlineKeyboardButton(text=emojize(f':backhand_index_pointing_right:{y}'), callback_data=0))
        else:
            if n == 0:
                kb.row(InlineKeyboardButton(text=f'{y}', callback_data=cb_years.new(year=y)))
            else:
                kb.insert(InlineKeyboardButton(text=f'{y}', callback_data=cb_years.new(year=y)))

    return kb


@logger.catch
async def create_kb_user_top_stat(t_id: int, type_graph: str ='execute'):
    kb_user_top_stat = InlineKeyboardMarkup(row_width=2)
    btn_text = ':bar_chart:Выполняемость' if type_graph == 'und' else ':bar_chart:Понимаемость'
    kb_user_top_stat.insert(InlineKeyboardButton(emojize(btn_text), callback_data=cb_graph_top.new(t_id=t_id, type=type_graph)))
    kb_user_top_stat.insert(InlineKeyboardButton(emojize(':chart_increasing:Описание'), callback_data='description'))
    kb_user_top_stat.insert(InlineKeyboardButton(emojize('📉Excel'), callback_data=cb_excel_stat.new(t_id=t_id)))
    kb_user_top_stat.row(InlineKeyboardButton(emojize(':BACK_arrow:Назад'), callback_data='back_stat'))
    topics = await get_topics()
    for top in topics:
        kb_user_top_stat.insert(InlineKeyboardButton(top.title, callback_data=cb_top_stat.new(t_id=t_id, top_id=top.id)))
    return kb_user_top_stat


@logger.catch
async def create_kb_user_sub_stat(t_id, top_id, type_graph='execute'):
    kb_user_sub_stat = InlineKeyboardMarkup(row_width=3)
    btn_text = ':bar_chart:Выполняемость' if type_graph == 'und' else ':bar_chart:Понимаемость'
    btn_type_graph = 'execute' if type_graph == 'und' else 'und'
    topic = await topic_by_id(top_id)
    topics = await get_topics()
    list_id = [i.id for i in topics]
    index_quest = list_id.index(topic.id)
    index_prev = index_quest - 1 if index_quest != 0 else -1
    index_next = index_quest + 1 if index_quest != len(list_id) - 1 else 0
    kb_user_sub_stat.insert(InlineKeyboardButton('<<<', callback_data=cb_graph_sub.new(t_id=t_id, type=btn_type_graph, top_id=list_id[index_prev])))
    kb_user_sub_stat.insert(InlineKeyboardButton(emojize(btn_text), callback_data=cb_graph_sub.new(t_id=t_id, type=type_graph, top_id=top_id)))
    kb_user_sub_stat.insert(InlineKeyboardButton('>>>', callback_data=cb_graph_sub.new(t_id=t_id, type=btn_type_graph, top_id=list_id[index_next])))
    kb_user_sub_stat.insert(InlineKeyboardButton(emojize(':chart_increasing:Описание'), callback_data='description'))
    kb_user_sub_stat.insert(InlineKeyboardButton(emojize(':BACK_arrow:Назад'), callback_data=cb_back_top_stat.new(t_id=t_id)))
    return kb_user_sub_stat


@logger.catch
async def get_list_years():
    users = session.query(User).filter_by(verify=1).all()
    years = []
    for user in users:
        if user.year not in years:
            years.append(user.year)
    years.sort()
    return years


# @logger.catch
# async def draw_understand_top_graph(t_id):
#     topics = await get_topics()
#     all_quest_top, und_count_list, und_percent_list, top_title_list = [], [], [], []
#     for top in topics:
#         und_count = 0
#         questions = session.query(Question).join(Subtopic).filter(Subtopic.topic_id == top.id).all()
#         all_quest_top.append(len(questions))
#         for q in questions:
#             tasks = session.query(Task).filter(Task.user_id == t_id, Task.question_id == q.id).order_by(Task.start).all()
#             for i in range(1, len(tasks)):
#                 if tasks[i].answer_point and tasks[i-1].answer_point:
#                     und_count += 1
#                     break
#         und_count_list.append(und_count)
#         top_title_list.append(top.title)
#         und_percent_list.append(int(und_count / len(questions) * 100))
#     # Создание столбчатой диаграммы
#     plt.bar(top_title_list, und_percent_list)
#
#     # Добавление названий столбцов
#     for i in range(len(top_title_list)):
#         plt.text(i, und_percent_list[i]+1, f'{und_count_list[i]}/{all_quest_top[i]}', ha='center')
#
#     # Настройка заголовка диаграммы и меток осей
#     user = await user_by_id(t_id)
#     plt.title(f'{user.name} {user.surname} {user.year} год\nПонимаемость тем')
#     plt.xticks(rotation=75, fontsize=8)
#     plt.xlabel('Темы')
#     plt.ylabel('%')
#     plt.tight_layout()
#     plt.savefig('graph.jpg', dpi=300)
@logger.catch
async def draw_understand_top_graph(t_id):
    topics = await get_topics()
    all_quest_top, und_count_list, und_percent_list, top_title_list, percent_all_corr_list, title_bar_list = [], [], [], [], [], []
    for top in topics:
        und_count = 0
        questions = session.query(Question).join(Subtopic).filter(Subtopic.topic_id == top.id).all()
        all_quest_top.append(len(questions))
        for q in questions:
            tasks = session.query(Task).filter(Task.user_id == t_id, Task.question_id == q.id).order_by(Task.start).all()
            for i in range(1, len(tasks)):
                if tasks[i].answer_point and tasks[i-1].answer_point:
                    und_count += 1
                    break
        und_count_list.append(und_count)
        top_title_list.append(top.title)
        und_percent_list.append(int(und_count / len(questions) * 100))
        top_task = session.query(Task).join(Question).join(Subtopic).filter(
            Task.user_id == t_id,
            Subtopic.topic_id == top.id
        ).count()
        top_corr_task = session.query(Task).join(Question).join(Subtopic).filter(
            Task.user_id == t_id,
            Task.answer_point == 1,
            Subtopic.topic_id == top.id
        ).count()
        percent_all_corr_list.append(int(top_corr_task / top_task * 100))
        title_bar_list.append(f'{top_corr_task}\n{top_task}')

    # Создаем фигуру и оси
    fig, ax = plt.subplots(figsize=(10, 7))

    # Создаем столбчатую диаграмму
    bar_width = 0.35

    ax.bar(np.arange(len(top_title_list)), und_percent_list, bar_width, color='b', label='Понимаемость, %')
    ax.bar(np.arange(len(top_title_list)) + bar_width, percent_all_corr_list, bar_width, color='g', label='Правильных\nвыполнений в теме, %')

    # Настраиваем оси и заголовок
    plt.ylabel('%')
    plt.xlabel('Темы')
    user = await user_by_id(t_id)
    plt.title(f'{user.name} {user.surname} {user.year} год\nПонимаемость тем')

    # Устанавливаем позиции на оси x для каждой группы
    ax.set_xticks(np.arange(len(top_title_list)) + bar_width / 2)
    ax.set_xticklabels(top_title_list, rotation=75, fontsize=8)

    # Добавляем подписи значений над каждым столбцом
    for i in range(len(top_title_list)):
        ax.annotate(f'{und_count_list[i]}\n{all_quest_top[i]}', xy=(i - 0.1, und_percent_list[i] + 1), fontsize=8)
        ax.annotate(title_bar_list[i], xy=(i + bar_width - 0.1, percent_all_corr_list[i] + 1), fontsize=8)

    # Добавляем легенду
    ax.legend(fontsize=8)

    plt.tight_layout()
    # Отображаем диаграмму
    plt.savefig('graph.jpg', dpi=300)


@logger.catch
async def draw_understand_sub_graph(topic_id, t_id):
    subtopics = await get_subtopics(topic_id)
    sub_all_quest, sub_und_count_list, sub_und_percent_list, sub_title_list, sub_percent_all_corr_list, sub_title_bar_list = [], [], [], [], [], []
    for sub in subtopics:
        und_count = 0
        questions = session.query(Question).filter(Question.subtopic_id == sub.id).all()
        sub_all_quest.append(len(questions))
        for q in questions:
            tasks = session.query(Task).filter(Task.user_id == t_id, Task.question_id == q.id).order_by(Task.start).all()
            for i in range(1, len(tasks)):
                if tasks[i].answer_point and tasks[i-1].answer_point:
                    und_count += 1
                    break
        sub_und_count_list.append(und_count)
        sub_title_list.append(sub.title)
        sub_und_percent_list.append(int(und_count / len(questions) * 100))
        sub_task = session.query(Task).join(Question).filter(
            Task.user_id == t_id,
            Question.subtopic_id == sub.id
        ).count()
        sub_corr_task = session.query(Task).join(Question).filter(
            Task.user_id == t_id,
            Task.answer_point == 1,
            Question.subtopic_id == sub.id
        ).count()
        sub_percent_all_corr_list.append(int(sub_corr_task / sub_task * 100))
        sub_title_bar_list.append(f'{sub_corr_task}\n{sub_task}')

    # Создаем фигуру и оси
    fig, ax = plt.subplots(figsize=(10, 7))

    # Создаем столбчатую диаграмму
    bar_width = 0.35

    ax.bar(np.arange(len(sub_title_list)), sub_und_percent_list, bar_width, color='b', label='Понимаемость, %')
    ax.bar(np.arange(len(sub_title_list)) + bar_width, sub_percent_all_corr_list, bar_width, color='g', label='Правильных\nвыполнений в подтеме, %')

    # Настраиваем оси и заголовок
    plt.ylabel('%')
    top = await topic_by_id(topic_id)
    plt.xlabel(f'Подтемы ({top.title})')
    user = await user_by_id(t_id)
    plt.title(f'{user.name} {user.surname} {user.year} год\nПонимаемость подтем ({top.title})')

    # Устанавливаем позиции на оси x для каждой группы
    ax.set_xticks(np.arange(len(sub_title_list)) + bar_width / 2)
    ax.set_xticklabels(sub_title_list, rotation=75, fontsize=8)

    # Добавляем подписи значений над каждым столбцом
    for i in range(len(sub_title_list)):
        ax.annotate(f'{sub_und_count_list[i]}\n{sub_all_quest[i]}', xy=(i - 0.1, sub_und_percent_list[i] + 1), fontsize=8)
        ax.annotate(sub_title_bar_list[i], xy=(i + bar_width - 0.1, sub_percent_all_corr_list[i] + 1), fontsize=8)

    # Добавляем легенду
    ax.legend(fontsize=8)

    plt.tight_layout()
    # Отображаем диаграмму
    plt.savefig('graph.jpg', dpi=300)


@logger.catch
async def draw_execute_top_graph(t_id):
    topics = await get_topics()
    top_task_list, top_corr_task_list, top_time_task_list, top_title_list = [], [], [], []
    for top in topics:
        top_time_task = 0
        top_tasks = session.query(Task).join(Question).join(Subtopic).filter(
            Task.user_id == t_id,
            Subtopic.topic_id == top.id
        ).all()
        top_corr_task = session.query(Task).join(Question).join(Subtopic).filter(
            Task.user_id == t_id,
            Task.answer_point == 1,
            Subtopic.topic_id == top.id
        ).count()
        for task in top_tasks:
             top_time_task += int((task.stop - task.start).total_seconds())
        top_task_list.append(len(top_tasks))
        top_corr_task_list.append(top_corr_task)
        top_title_list.append(top.title)
        top_time_task_list.append(top_time_task)
    top_task_percent_list = [int(x / sum(top_task_list) * 100) for x in top_task_list]
    top_corr_task_percent_list = [int(x / sum(top_corr_task_list) * 100) for x in top_corr_task_list]
    top_time_task_percent_list = [int(x / sum(top_time_task_list) * 100) for x in top_time_task_list]

    # Создаем фигуру и оси
    fig, ax = plt.subplots(figsize=(10, 7))

    # Создаем столбчатую диаграмму
    bar_width = 0.25

    ax.bar(np.arange(len(top_title_list)), top_task_percent_list, bar_width, color='Tomato', label='Всего выполнений, %')
    ax.bar(np.arange(len(top_title_list)) + bar_width, top_corr_task_percent_list, bar_width, color='DarkOrange',
           label='Всего правильных, %')
    ax.bar(np.arange(len(top_title_list)) + 2 * bar_width, top_time_task_percent_list, bar_width, color='Gold',
           label='Время, %')


    # Настраиваем оси и заголовок
    plt.ylabel('%')
    plt.xlabel('Темы')
    user = await user_by_id(t_id)
    plt.title(f'{user.name} {user.surname} {user.year} год\nВыполняемость тем')

    # Устанавливаем позиции на оси x для каждой группы
    ax.set_xticks(np.arange(len(top_title_list)) + bar_width)
    ax.set_xticklabels(top_title_list, rotation=75, fontsize=8)

    # Добавляем подписи значений над каждым столбцом
    for i in range(len(top_title_list)):
        ax.annotate(str(top_task_list[i]), xy=(i - 0.1, top_task_percent_list[i] + 0.5), fontsize=8)
        ax.annotate(str(top_corr_task_list[i]), xy=(i + bar_width - 0.1, top_corr_task_percent_list[i] + 0.5), fontsize=8)
        ax.annotate(str(top_time_task_list[i] // 60), xy=(i + 2 * bar_width - 0.1, top_time_task_percent_list[i] + 0.5), fontsize=8)

    # Добавляем легенду
    ax.legend(fontsize=8)

    plt.tight_layout()
    # Отображаем диаграмму
    plt.savefig('graph.jpg', dpi=300)


@logger.catch
async def draw_execute_sub_graph(topic_id, t_id):
    subtopics = await get_subtopics(topic_id)
    sub_task_list, sub_corr_task_list, sub_time_task_list, sub_title_list = [], [], [], []
    for sub in subtopics:
        sub_time_task = 0
        sub_tasks = session.query(Task).join(Question).filter(
            Task.user_id == t_id,
            Question.subtopic_id == sub.id
        ).all()
        sub_corr_task = session.query(Task).join(Question).filter(
            Task.user_id == t_id,
            Task.answer_point == 1,
            Question.subtopic_id == sub.id
        ).count()
        for task in sub_tasks:
            sub_time_task += int((task.stop - task.start).total_seconds())
        sub_task_list.append(len(sub_tasks))
        sub_corr_task_list.append(sub_corr_task)
        sub_title_list.append(sub.title)
        sub_time_task_list.append(sub_time_task)
    sub_task_percent_list = [int(x / sum(sub_task_list) * 100) for x in sub_task_list]
    sub_corr_task_percent_list = [int(x / sum(sub_corr_task_list) * 100) for x in sub_corr_task_list]
    sub_time_task_percent_list = [int(x / sum(sub_time_task_list) * 100) for x in sub_time_task_list]

    # Создаем фигуру и оси
    fig, ax = plt.subplots(figsize=(10, 7))

    # Создаем столбчатую диаграмму
    bar_width = 0.25

    ax.bar(np.arange(len(sub_title_list)), sub_task_percent_list, bar_width, color='Tomato', label='Всего выполнений, %')
    ax.bar(np.arange(len(sub_title_list)) + bar_width, sub_corr_task_percent_list, bar_width, color='DarkOrange',
           label='Всего правильных, %')
    ax.bar(np.arange(len(sub_title_list)) + 2 * bar_width, sub_time_task_percent_list, bar_width, color='Gold',
           label='Время, %')

    # Настраиваем оси и заголовок
    plt.ylabel('%')
    top = await topic_by_id(topic_id)
    plt.xlabel(f'Подтемы ({top.title})')
    user = await user_by_id(t_id)
    plt.title(f'{user.name} {user.surname} {user.year} год\nВыполняемость подтем ({top.title})')

    # Устанавливаем позиции на оси x для каждой группы
    ax.set_xticks(np.arange(len(sub_title_list)) + bar_width)
    ax.set_xticklabels(sub_title_list, rotation=75, fontsize=8)

    # Добавляем подписи значений над каждым столбцом
    for i in range(len(sub_title_list)):
        ax.annotate(str(sub_task_list[i]), xy=(i - 0.1, sub_task_percent_list[i] + 0.5), fontsize=8)
        ax.annotate(str(sub_corr_task_list[i]), xy=(i + bar_width - 0.1, sub_corr_task_percent_list[i] + 0.5), fontsize=8)
        ax.annotate(str(sub_time_task_list[i] // 60), xy=(i + 2 * bar_width - 0.1, sub_time_task_percent_list[i] + 0.5), fontsize=8)

    # Добавляем легенду
    ax.legend(fontsize=8)

    plt.tight_layout()
    # Отображаем диаграмму
    plt.savefig('graph.jpg', dpi=300)


@logger.catch
async def create_cell_text(task):
    return f'{task.start.strftime("%d.%m.%Y")} {task.answer_text} {(task.stop - task.start).total_seconds()/60}мин'