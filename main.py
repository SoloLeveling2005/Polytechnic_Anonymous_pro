import time
import os
import re
from random import randint
import telebot
from telebot import types  # кнопки Telegram
import datetime
import threading
import sqlite3 as sql
import json

from connect import bot
from create_db import create_db

# from help import checking_condition, add_user_db_users
from script_assistant import verify_job, insert_user_into_db_requests_connections_couple
from check_req.check_new_request import application_couple_threading

# from check_req.do_checking_application import do_checking_application_couple_threading

print("Нажмите Ctrl+C если хотите завершить работу бота")


#  Цикл проверяющий кто подключился и соединяющие их

def do_checking_application_couple_threading(message):
    applications_thread = threading.Thread(target=do_checking_application_couple, args=(message,))
    applications_thread.daemon = True
    applications_thread.start()


def do_checking_application_couple(message):
    user_id = message.chat.id
    while True:

        with sql.connect('todo.db') as con:
            cur = con.cursor()
            cur.execute(f"""
                            SELECT * FROM do WHERE user_id = {user_id};
                        """)
            request_data = cur.fetchall()
        print(request_data)
        if request_data:
            if request_data[0][1] == "chat":
                bot.send_message(message.chat.id,
                                 f"Нашел, ваш собеседник онлайн.",
                                 parse_mode='HTML')
                print("поиск нашел")

                chat(message)

            elif request_data[0][1] == "main_menu":
                bot.send_message(message.chat.id,
                                 f"Поиск отменен",
                                 parse_mode='HTML')
                print("отменили поиск")
                main_menu(message)
        time.sleep(1)


#  Цикл проверяющий кто подключился и соединяющие их


create_db()
application_couple_threading()

# do_checking_application_couple_threading()

@bot.message_handler(commands=['start'])
def start(message):
    # verify_job(message, where_was_called="start")

    main_menu(message)


# @bot.message_handler(commands=['main_menu'])
def main_menu(message):
    user_id = message.chat.id
    # verify_job(message, where_was_called="main_menu")
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    find_chat_button = types.KeyboardButton('🔎 Поиск собеседника')
    markup.add(find_chat_button)
    # find_group_button = types.KeyboardButton('🔎 Поиск группы')
    # markup.add(find_group_button)

    # Для премиум аккаунтов делаем  создание группы
    with sql.connect('todo.db') as con:
        cur = con.cursor()
        cur.execute(f"""
                        SELECT * FROM users WHERE user_id = {user_id};
                    """)
        user = cur.fetchall()
    if user:
        if user[0][3] == "premium":
            create_group_button = types.KeyboardButton('🔎 Создать группу')
            markup.add(create_group_button)

    bot.send_message(message.chat.id,
                     f"🏠Главное меню",
                     parse_mode='HTML', reply_markup=markup)

    @bot.message_handler(content_types=['text'])
    def get_text_messages(message):
        if message.text == '🔎 Поиск собеседника':
            find_chat(message)
        elif message.text == '🔎 Поиск группы':
            find_group(message)
        elif message.text == '🔎 Создать группу':
            with sql.connect('todo.db') as con:
                cur = con.cursor()
                cur.execute(f"""
                                SELECT * FROM users WHERE user_id = {user_id};
                            """)
                user_prem = cur.fetchall()
            if user_prem:
                if user_prem[0][3] == "premium":
                    create_group(message)


# @bot.message_handler(commands=['find_chat'])
def find_chat(message):
    do_checking = True
    user_id = message.chat.id

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    cancel_find_button = types.KeyboardButton('❌ Отмена поиска')
    markup.add(cancel_find_button)
    bot.send_message(message.chat.id,
                     f"🔎Начинаю поиск...",
                     parse_mode='HTML', reply_markup=markup)

    insert_user_into_db_requests_connections_couple(message)  # добавляем юзера в бд запросов на вход
    do_checking_application_couple_threading(message)
    @bot.message_handler(content_types=['text'])
    def get_text_messages(message):
        global do_checking
        if message.text == '❌ Отмена поиска':
            with sql.connect('todo.db') as con:
                cur = con.cursor()
                cur.execute(f"""
                                UPDATE do,
                                SET do.where_you = "main_menu"
                                WHERE do.user_id = {user_id};
                            """)



# @bot.message_handler(commands=['find_group'])
def find_group(message):
    # verify_job(message, where_was_called="find_group")
    pass


def create_group(message):
    pass


# @bot.message_handler(commands=['cancel_find'])
def cancel_find(message):
    verify_job(message, where_was_called="cancel_find")


# @bot.message_handler(commands=['disconnect'])
def disconnect(message):
    verify_job(message, where_was_called="disconnect")


def chat(message):
    pass


@bot.message_handler(commands=['help'])
def help(message):
    user_id = message.chat.id
    text_help = """
    Доступные команды:
    /main_menu - перейти в главное меню
    /find_chat - поиск анонимуса
    """
    with sql.connect('todo.db') as con:
        cur = con.cursor()
        cur.execute(f"""
                        SELECT * FROM users WHERE user_id = {user_id};
                    """)
        user = cur.fetchall()
    if user:
        if user[0][4] == "user_prem":
            text_help += "/find_group - поиск группы анонимус"
    else:
        pass
    text_help += """/cancel_find - отмена поиска
    /disconnect - отсоединиться от чата
    Вам не обязательно их вводить, они будут доступны в виде кнопок ниже
    """
    bot.send_message(message.chat.id,
                     text_help)


# def chat():
#     @bot.message_handler(content_types=['text'])
#     def get_text_messages(message):
#         if message.text == '🏠 Главное меню':
#             bot.send_message(message.chat.id,
#                              "Главное меню")
#             # main_menu(message)
#         elif message.text == '🔎 Поиск собеседника':
#             find_chat(message)
#         elif message.text == '🔎 Поиск группы':
#             find_group(message)
#         elif message.text == '❌ Отмена поиска':
#             cancel_find(message)
#         elif message.text == '🛑 Отключиться':
#             disconnect(message)
#         else:
#             pass


if __name__ == '__main__':
    bot.polling(none_stop=True)
    while True:
        try:
            bot.polling(none_stop=True)
            time.sleep(1)
        except Exception as e:
            time.sleep(3)
            a = datetime.datetime.today()
            print(e)
            print(a)
            bot = telebot.TeleBot('5488566542:AAEGQsiDrnLjwFCQb4kmbn7EJYnZqoaIfxk')
            bot.send_message(1303257033,
                             'Сообщение системы: Произошла перезагрузка программы')
            os.system('python main.py')
