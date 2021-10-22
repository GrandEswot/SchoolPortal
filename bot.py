import os
import datetime
import telebot
from telebot.types import CallbackQuery

from utils.telegramcalendar import create_calendar
from main import get_homework, get_marks_per_subject, get_shedules

Token = os.getenv('TELETOKEN')
telegram_api_url = 'https://api.telegram.org/bot'
bot = telebot.TeleBot(Token, parse_mode=None)
current_shown_dates = {}
son_name = ['']


@bot.message_handler(commands=['start'])
def exchange_command(message):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(
        telebot.types.InlineKeyboardButton("Расписание", callback_data="shedules"),
        telebot.types.InlineKeyboardButton("Домашняя работа", callback_data="homework"),
        telebot.types.InlineKeyboardButton("Оценки. Статистика", callback_data="statistic")
    )
    bot.send_message(
        message.chat.id, "Что показать?", reply_markup=keyboard
    )


@bot.callback_query_handler(func=lambda c: c.data.startswith('shedules'))
def commands(callback_query: CallbackQuery):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(
       telebot.types.InlineKeyboardButton('Степан', callback_data='son shedules stepan'),
       telebot.types.InlineKeyboardButton('Сергей', callback_data='son shedules sergey')
    )
    bot.send_message(callback_query.from_user.id, "Для кого вывести расписание?", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda c: c.data.startswith('homework'))
def commands(callback_query: CallbackQuery):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(
       telebot.types.InlineKeyboardButton('Степан', callback_data='son homework stepan'),
       telebot.types.InlineKeyboardButton('Сергей', callback_data='son homework sergey')
    )
    bot.send_message(callback_query.from_user.id, "Для кого вывести домашнее задание?", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda c: c.data.startswith('statistic'))
def commands(callback_query: CallbackQuery):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(
        telebot.types.InlineKeyboardButton('Степан', callback_data='son statistic stepan'),
        telebot.types.InlineKeyboardButton('Сергей', callback_data='son statistic sergey')
    )
    bot.send_message(callback_query.from_user.id, "Для кого вывести статистику по оценкам?", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda c: c.data.startswith('son'))
def commands(callback_query: CallbackQuery):
    command = callback_query.data
    if 'homework stepan' in command:
        answer = bot.send_message(callback_query.from_user.id, 'Домашнее задание для Степана')
        homework(answer, son='stepan')
    elif 'homework sergey' in command:
        answer = bot.send_message(callback_query.from_user.id, "Домашнее задание для Сергея")
        homework(answer, son='sergey')
    elif 'shedules stepan' in command:
        answer = bot.send_message(callback_query.from_user.id, "Расписание уроков на завтра для Степана")
        shedules(answer, son='stepan')
    elif 'shedules sergey' in command:
        answer = bot.send_message(callback_query.from_user.id, "Расписание уроков на завтра для Сергея")
        shedules(answer, son='sergey')
    elif 'statistic stepan' in command:
        answer = bot.send_message(callback_query.from_user.id, "Оценки Степана")
        statistic(answer, son='stepan')
    elif 'statistic sergey' in command:
        answer = bot.send_message(callback_query.from_user.id, "Оценки Сергея")
        statistic(answer, son='sergey')


def statistic(message, son):
    son_name[0] = son
    date = datetime.time()
    result = get_marks_per_subject(son_name[0].strip(), date)
    bot.send_message(message.chat.id, 'Оценочки')
    bot.send_message(chat_id=message.chat.id, text=result, parse_mode='Markdown')


@bot.callback_query_handler(func=lambda c: c.data.startswith('stat'))
def commands(callback_query: CallbackQuery):
    result = get_marks_per_subject('Stepan', None)
    bot.send_message(callback_query.from_user.id, 'Оценки за обучение для Степана')
    bot.send_message(chat_id=callback_query.from_user.id, text=result, parse_mode='Markdown')


@bot.message_handler()
def wrong_command(message):
    bot.reply_to(message, 'Вы ввели неправильную комманду, введите /start для начала работы')


def homework(message, son):
    son_name[0] = son
    handle_calendar_command(message)


def shedules(message, son):
    son_name[0] = son
    date = '1'
    result = get_shedules(son_name[0].strip(), date)
    if len(result) > 0:
        print(len(result))
        bot.send_message(chat_id=message.chat.id, text="Вот и расписание подоспело!")
        bot.send_message(chat_id=message.chat.id, text=result, parse_mode='Markdown')
    else:
        bot.send_message(chat_id=message.chat.id, text="А завтра нет уроков=)")


@bot.message_handler()
def handle_calendar_command(message):

    now = datetime.datetime.now()
    chat_id = message.chat.id

    date = (now.year, now.month)
    current_shown_dates[chat_id] = date

    markup = create_calendar(now.year, now.month)

    bot.send_message(message.chat.id, "Выбери дату!", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: 'DAY' in call.data[0:13])
def handle_day_query(call):
    chat_id = call.message.chat.id
    saved_date = current_shown_dates.get(chat_id)
    last_sep = call.data.rfind(';') + 1

    if saved_date is not None:

        day = call.data[last_sep:]
        date = str(datetime.datetime(int(saved_date[0]), int(saved_date[1]), int(day)).date())
        result = get_homework(son_name[0].strip(), date)
        print(result)
        # print(len(result))
        if len(result) > 0:
            bot.send_message(chat_id=chat_id, text="Лови домашку!")
            bot.send_message(chat_id=chat_id, text=result, parse_mode='Markdown')
        else:
            bot.send_message(chat_id=chat_id, text="Наверное дата неправильная. ДЗ не обнаружено")
    else:
        pass


@bot.callback_query_handler(func=lambda call: 'MONTH' in call.data)
def handle_month_query(call):

    info = call.data.split(';')
    month_opt = info[0].split('-')[0]
    year, month = int(info[1]), int(info[2])
    chat_id = call.message.chat.id

    if month_opt == 'PREV':
        month -= 1

    elif month_opt == 'NEXT':
        month += 1

    if month < 1:
        month = 12
        year -= 1

    if month > 12:
        month = 1
        year += 1

    date = (year, month)
    current_shown_dates[chat_id] = date
    markup = create_calendar(year, month)
    bot.edit_message_text("Выбери дату!", call.from_user.id, call.message.message_id, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: "IGNORE" in call.data)
def ignore(call):
    bot.answer_callback_query(call.id, text="OOPS... something went wrong")


bot.polling(none_stop=True)
