import os
import datetime
import telebot
from telebot.types import CallbackQuery

from utils.telegramcalendar import create_calendar
from main import main


# Token = os.getenv('TELETOKEN')
Token = '2083449644:AAGI3iS46ArAigv6D_saGUSYmR8_2LyguvA'
telegram_api_url = 'https://api.telegram.org/bot'
bot = telebot.TeleBot(Token, parse_mode=None)
current_shown_dates = {}
son = ['']

#
# @bot.message_handler(commands=['start'])
# def start(message):
#     bot.reply_to(message, "Привет, {}! Хочешь узнать домашку?"
#                           "\nДля получения информации нажмите /help".format(message.chat.first_name))


@bot.message_handler(commands=['start'])
def exchange_command(message):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(
        telebot.types.InlineKeyboardButton("Степан", callback_data="stepan"),
        telebot.types.InlineKeyboardButton(
            "Сергей", callback_data="sergey"
        ),
    )
    bot.send_message(
        message.chat.id, "Чью домашку показать?", reply_markup=keyboard
    )


@bot.callback_query_handler(func=lambda c: c.data.startswith('s'))
def commands(callback_query: CallbackQuery):
    command = callback_query.data
    if command == 'stepan':
        answer = bot.send_message(callback_query.from_user.id, 'Домашнее задание для Степана')
        stepan(answer)
    elif command == 'sergey':
        answer = bot.send_message(callback_query.from_user.id, "Домашнее задание для Сергея")
        # sergey(answer)


@bot.message_handler()
def wrong_command(message):
    bot.reply_to(message, 'Вы ввели неправильную комманду, введите /help для получения информации')


def stepan(message):
    son[0] = 'Stepan'
    handle_calendar_command(message)

# def sergey(message):
#     pass


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
        result = main(son[0].strip(), date)
        bot.send_message(chat_id=chat_id, text="Лови домашку!")
        bot.send_message(chat_id=chat_id, text=result, parse_mode='Markdown')

    else:
        # add your reaction for shown an error
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
