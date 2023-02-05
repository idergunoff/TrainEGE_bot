from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData
from emoji import emojize


# CallbackData

cb_verify = CallbackData('verify', 't_id', 'yesno') # подтверждение регистрации

cb_topic = CallbackData('topic', 'topic_id')    # выбор темы
cb_index_topic = CallbackData("index_topic", "topic_id")    # выбор темы для изменения порядка
cb_up_down_index = CallbackData('up_down_index', 'topic_id', 'up_down') # повысить или понизить индекс
cb_edit_topic = CallbackData('edit_topic', 'topic_id')  # выбор темы для ее редактирования
cb_delete_topic = CallbackData('delete_topic', 'topic_id')  # выбор темы для ее удаления

cb_subtopic_menu = CallbackData('subtopic_menu', 'topic_id', 'type') # выбор темы для меню подте

cb_subtopic = CallbackData('subtopic', 'sub_id')    # выбор подтемы
cb_index_subtopic = CallbackData("index_subtopic", "sub_id")    # выбор подтемы для изменения порядка
cb_up_down_index_subtopic = CallbackData('up_down_index_sub', 'sub_id', 'up_down') # повысить или понизить индекс подтемы
cb_edit_subtopic = CallbackData('edit_subtopic', 'sub_id')  # выбор подтемы для ее редактирования
cb_delete_subtopic = CallbackData('delete_subtopic', 'sub_id')  # выбор подтемы для ее удаления
cb_back_subtopic = CallbackData('subtopic_back', 'topic_id') # выбор темы для выхода к списку подтем
cb_exam_topic = CallbackData('exam_topic', 'topic_id')  # выбор темы для экзамена по теме

cb_question = CallbackData('question', 'quest_id')   # выбор вопроса
cb_new_question = CallbackData('new_question', 'sub_id')    # выбор подтемы для нового вопроса
cb_exam_subtopic = CallbackData('exam_subtopic', 'sub_id')  # выбор подтемы для экзамена по подтеме
cb_back_question = CallbackData('back_question', 'sub_id') # выбор подтемы для выхода к списку вопросов
cb_question_pict = CallbackData('question_pict', 'quest_id')   # выбор следующего и предыдущего вопроса
cb_del_quest = CallbackData('del_quest', 'quest_id') # выбор вопроса для удаления
cb_edit_pict_quest = CallbackData('edit_pict_quest', 'quest_id') # выбор вопроса для редактирования фото
cb_edit_answer_quest = CallbackData('edit_answer_quest', 'quest_id') # выбор вопроса для редактирования ответа


# KeyboardButton

btn_reg = KeyboardButton(emojize('Регистрация:crystal_ball:'))
btn_topic = KeyboardButton(emojize('Темы:abacus:'))
btn_exam = KeyboardButton(emojize('Экзамен:bullseye:'))
btn_mistake = KeyboardButton(emojize('Работа над ошибками:scissors:'))



# ReplyKeyboardMarkup

kb_start_unreg = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
kb_start_unreg.row(btn_reg)

kb_start_reg = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
kb_start_reg.row(btn_topic, btn_exam).row(btn_mistake)



# InlineKeyboardButton

btn_back_topic = InlineKeyboardButton(emojize(':BACK_arrow:Назад'), callback_data='back_topic')

btn_new_topic = InlineKeyboardButton(text=emojize('Новая тема:memo:'), callback_data='new_topic')
btn_index_topic = InlineKeyboardButton(text=emojize('Порядок тем:up-down_arrow:'), callback_data='index_topic')
btn_edit_topic = InlineKeyboardButton(text=emojize('Изменить тему:wrench:'), callback_data='edit_topic')
btn_delete_topic = InlineKeyboardButton(text=emojize('Удалить тему:wastebasket:'), callback_data='delete_topic')


# btn_link_bot = InlineKeyboardButton(emojize(':robot:Перейти в бот'), url='https://t.me/alco24kzn_bot')



# kb_post = InlineKeyboardMarkup()
# kb_post.row(btn_send_post).row(btn_back_category)
#
# kb_option = InlineKeyboardMarkup()
# kb_option.row(btn_channel, btn_phone).row(btn_operator, btn_edit_del).row(btn_back_category)


class TrainStates(StatesGroup):
    REG_NAME = State()
    REG_SURNAME = State()
    REG_YEAR = State()

    NEW_TOPIC = State()
    EDIT_TOPIC = State()

    NEW_SUBTOPIC = State()
    INDEX_SUBTOPIC = State()
    EDIT_SUBTOPIC = State()
    CHOOSE_EDIT_SUBTOPIC = State()
    CHOOSE_DELETE_SUBTOPIC = State()

    NEW_QUESTION_PICT = State()
    NEW_QUESTION_ANSWER = State()
    EDIT_PICT_QUEST = State()
    EDIT_ANSWER_QUEST = State()
