from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData
from emoji import emojize


# CallbackData

cb_topic = CallbackData('topic', 'topic_id')    # выбор темы
cb_index_topic = CallbackData("index_topic", "topic_id")    # выбор темы для изменения порядка
cb_up_down_index = CallbackData('up_down_index', 'topic_id', 'up_down') # повысить или понизить индекс
cb_edit_topic = CallbackData('edit_topic', 'topic_id')  # выбор темы для ее редактирования
cb_delete_topic = CallbackData('delete_topic', 'topic_id')  # выбор темы для ее удаления



# KeyboardButton

btn_topic = KeyboardButton('Темы')
btn_exam = KeyboardButton('Экзамен')
btn_mistake = KeyboardButton('Работа над ошибками')



# ReplyKeyboardMarkup

kb_start = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
kb_start.row(btn_topic, btn_exam).row(btn_mistake)



# InlineKeyboardButton

btn_back_topic = InlineKeyboardButton(emojize(':BACK_arrow:Назад'), callback_data='back_topic')

btn_new_topic = InlineKeyboardButton(text=emojize('Новая тема:memo:'), callback_data='new_topic')
btn_index_topic = InlineKeyboardButton(text=emojize('Порядок тем:up-down_arrow:'), callback_data='index_topic')
btn_edit_topic = InlineKeyboardButton(text=emojize('Изменить тему:wrench:'), callback_data='edit_topic')
btn_delete_topic = InlineKeyboardButton(text=emojize('Удалить тему:wastebasket:'), callback_data='delete_topic')

btn_new_subtopic = InlineKeyboardButton(text=emojize('Новая подтема:memo:'), callback_data='new_subtopic')
btn_index_subtopic = InlineKeyboardButton(text=emojize('Порядок подтем:up-down_arrow:'), callback_data='index_subtopic')
btn_edit_subtopic = InlineKeyboardButton(text=emojize('Изменить подтему:wrench:'), callback_data='edit_subtopic')
btn_delete_subtopic = InlineKeyboardButton(text=emojize('Удалить подтему:wastebasket:'), callback_data='delete_subtopic')


# btn_link_bot = InlineKeyboardButton(emojize(':robot:Перейти в бот'), url='https://t.me/alco24kzn_bot')



# kb_post = InlineKeyboardMarkup()
# kb_post.row(btn_send_post).row(btn_back_category)
#
# kb_option = InlineKeyboardMarkup()
# kb_option.row(btn_channel, btn_phone).row(btn_operator, btn_edit_del).row(btn_back_category)




class TrainStates(StatesGroup):
    NEW_TOPIC = State()
    EDIT_TOPIC = State()
    NEW_SUBTOPIC = State()
    EDIT_SUBTOPIC = State()