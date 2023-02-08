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
        text += f'\nЗадание <u><b>{i[0]}</b></u>. Ответ: <b>{i[1]}</b>, правильный ответ: <b>{i[2]}</b>. Время: <i>{i[3]} секунд</i>'
    return text




@logger.catch
async def exam_by_id(exam_id):
    return session.query(Exam).filter(Exam.id == exam_id).first()