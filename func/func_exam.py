import datetime

from config import *
from button import *


@logger.catch
async def add_new_exam(t_id, type_exam):
    new_exam = Exam(user_id=t_id, type=type_exam, start=datetime.datetime.now())
    session.add(new_exam)
    session.commit()
    return new_exam.id


@logger.catch
async def create_tasks_sub_exam(t_id, sub_id, exam_id):
    questions = session.query(Question).filter(Question.subtopic_id == sub_id, Question.showing == 1).all()
    list_count_quest = []
    for q in questions:
        list_q = [session.query(Task).filter(Task.user_id == t_id, Task.question_id == q.id).count(), q.id]
        list_count_quest.append(list_q)
    random.shuffle(list_count_quest)
    list_count_quest.sort(key=lambda x: x[0])
    print(list_count_quest[:10])
    for lq in list_count_quest[:10]:
        new_task = Task(exam_id=exam_id, user_id=t_id, question_id=lq[1])
        session.add(new_task)
    session.commit()


@logger.catch
async def create_tasks_top_exam(t_id, top_id, exam_id):
    questions = session.query(Question).join(Subtopic).filter(Subtopic.topic_id == top_id, Question.showing == 1).all()
    list_count_quest = []
    for q in questions:
        list_q = [session.query(Task).filter(Task.user_id == t_id, Task.question_id == q.id).count(), q.id]
        list_count_quest.append(list_q)
    random.shuffle(list_count_quest)
    list_count_quest.sort(key=lambda x: x[0])
    print(list_count_quest[:10])
    for lq in list_count_quest[:10]:
        new_task = Task(exam_id=exam_id, user_id=t_id, question_id=lq[1])
        session.add(new_task)
    session.commit()


@logger.catch
async def create_tasks_error_exam(t_id, exam_id):
    questions = session.query(Question).filter(Question.showing == 1).all()
    list_error_quest = []
    for q in questions:
        task = session.query(Task).filter(Task.user_id == t_id, Task.question_id == q.id).order_by(desc(Task.stop)).first()
        if task:
            if task.answer_point == 0:
                list_error_quest.append(q.id)
    random.shuffle(list_error_quest)
    print(list_error_quest[:10])
    for lq in list_error_quest[:10]:
        new_task = Task(exam_id=exam_id, user_id=t_id, question_id=lq)
        session.add(new_task)
    session.commit()


@logger.catch
async def create_tasks_exam_ege(t_id, exam_id):
    list_ege_quest = []
    for top in session.query(Topic).all():
        questions = session.query(Question).join(Subtopic).filter(Subtopic.topic_id == top.id, Question.showing == 1).all()
        list_count_quest = []
        for q in questions:
            list_q = [session.query(Task).filter(Task.user_id == t_id, Task.question_id == q.id).count(), q.id]
            list_count_quest.append(list_q)
        random.shuffle(list_count_quest)
        list_count_quest.sort(key=lambda x: x[0])
        if len(list_count_quest) > 0:
            list_ege_quest.append(list_count_quest[0][1])
    print(list_ege_quest)
    for lq in list_ege_quest:
        new_task = Task(exam_id=exam_id, user_id=t_id, question_id=lq)
        session.add(new_task)
    session.commit()

@logger.catch
async def get_task(t_id):
    return session.query(Task).filter(Task.user_id == t_id, Task.answer_text == '').first()


@logger.catch
async def start_task(task_id):
    session.query(Task).filter(Task.id == task_id).update({'start': datetime.datetime.now()}, synchronize_session='fetch')
    session.commit()


@logger.catch
async def check_answer(answer, quest, task_id):
    point = 1 if answer == quest.answer else 0
    session.query(Task).filter(Task.id == task_id).update({
        'stop': datetime.datetime.now(),
        'answer_text': answer,
        'answer_point': point
    }, synchronize_session='fetch')
    session.commit()
    return point


@logger.catch
async def create_report(exam_id):
    session.query(Exam).filter(Exam.id == exam_id).update({'stop': datetime.datetime.now()}, synchronize_session='fetch')
    session.commit()
    tasks = session.query(Task).filter(Task.exam_id == exam_id).all()
    list_tasks, right_answer, all_time = [], 0, 0
    for t in tasks:
        list_tasks.append([
            f'{t.question.subtopic.topic.index}.{t.question.subtopic.index}.{t.question.index}',
            t.answer_text,
            t.question.answer,
            int((t.stop - t.start).total_seconds())
        ])
        right_answer += t.answer_point
        all_time += int((t.stop - t.start).total_seconds())
    text = f'Правильных ответов: <b>{right_answer}</b> из <b>{len(list_tasks)}</b>\nОбщее время: <i>{all_time} секунд</i>\n'
    for i in list_tasks:
        text += f'\n<u><b>{i[0]}</b></u>. Ответ: <b>{i[1]}({i[2]})</b>. Время: <i>{i[3]} секунд</i>'
    return text


@logger.catch
async def exam_by_id(exam_id):
    return session.query(Exam).filter(Exam.id == exam_id).first()


@logger.catch
async def get_test_name(exam_id):
    exam = await exam_by_id(exam_id)
    name = 'тест'
    if exam.type == 'sub':
        name = f'теста по подтеме <b>"{exam.tasks[0].question.subtopic.title}"</b>'
    elif exam.type == 'top':
        name = f'теста по теме <b>"{exam.tasks[0].question.subtopic.topic.title}"</b>'
    elif exam.type == 'exam':
        name = 'теста по всем темам'
    elif exam.type == 'error':
        name = 'теста "Работа над ошибками"'
    return name
