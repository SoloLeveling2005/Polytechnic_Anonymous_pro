import random
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

from telebot.types import ReplyKeyboardRemove

from connect import bot
from create_bd import create_bd

print("Нажмите Ctrl+C если хотите завершить работу бота")

create_bd()



def what_do_you_do_update(user_id, what):
    with sql.connect('todo.db') as con:
        cur = con.cursor()
        cur.execute(f"""
                        UPDATE do SET where_you = "{what}" WHERE user_id = {user_id};
                    """)


def what_do_you_do_insert(user_id, what):
    with sql.connect("todo.db") as con:
        cur = con.cursor()
        cur.execute(f"""
                INSERT INTO do (user_id,where_you) VALUES({user_id},"{what}")
                """)


def request_connections_group():
    while True:
        with sql.connect('todo.db') as con:
            cur = con.cursor()
            cur.execute(f"""
                            SELECT * FROM request_connections_group
                        """)
            users = cur.fetchall()
        if users:
            if len(users) >= 1:
                user_id = users[0][0]
                with sql.connect('todo.db') as con:
                    cur = con.cursor()
                    cur.execute(f"""
                                  DELETE FROM request_connections_group WHERE user_id = {user_id};
                                  """)
                with sql.connect('todo.db') as con:
                    cur = con.cursor()
                    cur.execute(f"""
                                    SELECT * FROM connection_group WHERE how_many_people < 4
                                """)
                    users = cur.fetchall()
                if users:
                    len_users = len(users)
                    index = 0
                    rand_index = random.randint(0, len_users-1)
                    print(users)
                    print(rand_index)
                    print(len_users-1)
                    group_id = users[rand_index][1]
                    group_participants = users[rand_index][2]
                    keys_bd_users = ['user_two', 'user_three', 'user_four']
                    for i in [3, 4, 5]:
                        if users[rand_index][i] is None:
                            with sql.connect('todo.db') as con:
                                cur = con.cursor()
                                cur.execute(f"""
                                                UPDATE connection_group SET {keys_bd_users[index]} = "{user_id}" WHERE 
                                                id_group = {group_id}; 
                                            """)
                                cur = con.cursor()
                                cur.execute(f"""
                                                UPDATE connection_group SET how_many_people = "{index+2}" WHERE 
                                                id_group = {group_id}; 
                                            """)
                                what_do_you_do_update(user_id, what="chat_group")
                            break
                        index += 1
        time.sleep(3)


request_connections_group_thread = threading.Thread(target=request_connections_group)
request_connections_group_thread.daemon = True
request_connections_group_thread.start()


def request_connections_couple():
    while True:
        with sql.connect('todo.db') as con:
            cur = con.cursor()
            cur.execute(f"""
                            SELECT * FROM request_connections_couple
                        """)
            users = cur.fetchall()
        if users:
            if len(users) > 1:
                one_id = users[0][0]
                two_id = users[1][0]
                with sql.connect("todo.db") as con:
                    cur = con.cursor()
                    cur.execute(f"""
                            INSERT INTO connection_couple (first,second) VALUES({one_id},{two_id})
                            """)
                with sql.connect("todo.db") as con:
                    cur = con.cursor()
                    cur.execute(f"""
                            INSERT INTO connection_couple (first,second) VALUES({two_id},{one_id})
                            """)
                    print("Данные добавлены в таблицу connections")
                with sql.connect('todo.db') as con:
                    cur = con.cursor()
                    cur.execute(f"""
                                      DELETE FROM request_connections_couple WHERE user_id = {one_id};
                                      """)
                with sql.connect('todo.db') as con:
                    cur = con.cursor()
                    cur.execute(f"""
                                  DELETE FROM request_connections_couple WHERE user_id = {two_id};
                                  """)
                print("Данные удалены с таблицы request_connections_couple")
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                disconnect_chat = types.KeyboardButton('Отключиться')
                markup.add(disconnect_chat)
                bot.send_message(one_id,
                                 f"Нашел, ваш собеседник онлайн", reply_markup=markup)
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                disconnect_chat = types.KeyboardButton('Отключиться')
                markup.add(disconnect_chat)
                bot.send_message(two_id,
                                 f"Нашел, ваш собеседник онлайн", reply_markup=markup)
                what_do_you_do_update(one_id, what="chat")
                what_do_you_do_update(two_id, what="chat")
        time.sleep(3)


request_connections_couple_thread = threading.Thread(target=request_connections_couple)
request_connections_couple_thread.daemon = True
request_connections_couple_thread.start()


def reg_user_insert(message):
    user_id = message.chat.id
    with sql.connect("todo.db") as con:
        cur = con.cursor()
        cur.execute(f"""
                INSERT INTO users (user_id,status) VALUES({user_id},"user")
                """)
        print("Данные добавлены в таблицу users")


def disconnect_user_from_chat(message, user):
    user_id = message.chat.id
    first_user = user[0][1]
    second_user = user[0][2]

    with sql.connect('todo.db') as con:
        cur = con.cursor()
        cur.execute(f"""
                      DELETE FROM connection_couple WHERE first = {first_user};
                      """)
    with sql.connect('todo.db') as con:
        cur = con.cursor()
        cur.execute(f"""
                      DELETE FROM connection_couple WHERE first = {second_user};
                      """)

    if user_id == first_user:
        bot.send_message(first_user,
                         f"Вы отключились от чата",
                         parse_mode='HTML')
        bot.send_message(second_user,
                         f"Ваш собеседник отключился",
                         parse_mode='HTML')
        main_menu(message, user_id_disconnect=first_user)
        main_menu(message, user_id_disconnect=second_user)
    elif user_id == second_user:
        bot.send_message(first_user,
                         f"Ваш собеседник отключился",
                         parse_mode='HTML')
        bot.send_message(second_user,
                         f"Вы отключились от чата",
                         parse_mode='HTML')
        main_menu(message, user_id_disconnect=first_user)
        main_menu(message, user_id_disconnect=second_user)
    what_do_you_do_update(first_user, what="main_menu")
    what_do_you_do_update(second_user, what="main_menu")

def disconnect_user_from_group(message, user):
    user_id = message.chat.id
    first_user = user[0][1]
    second_user = user[0][2]

    with sql.connect('todo.db') as con:
        cur = con.cursor()
        cur.execute(f"""
                      DELETE FROM connection_couple WHERE first = {first_user};
                      """)
    with sql.connect('todo.db') as con:
        cur = con.cursor()
        cur.execute(f"""
                      DELETE FROM connection_couple WHERE first = {second_user};
                      """)

    if user_id == first_user:
        bot.send_message(first_user,
                         f"Вы отключились от чата",
                         parse_mode='HTML')
        bot.send_message(second_user,
                         f"Ваш собеседник отключился",
                         parse_mode='HTML')
        main_menu(message, user_id_disconnect=first_user)
        main_menu(message, user_id_disconnect=second_user)
    elif user_id == second_user:
        bot.send_message(first_user,
                         f"Ваш собеседник отключился",
                         parse_mode='HTML')
        bot.send_message(second_user,
                         f"Вы отключились от чата",
                         parse_mode='HTML')
        main_menu(message, user_id_disconnect=first_user)
        main_menu(message, user_id_disconnect=second_user)
    what_do_you_do_update(first_user, what="main_menu")
    what_do_you_do_update(second_user, what="main_menu")


def disconnect_user_from_group_admin(message, user):
    pass

def send_message_from_group(message):
    pass


@bot.message_handler(commands=['start'])
def start(message):
    print("start")
    reg_user_insert(message)
    what_do_you_do_insert(message.chat.id, what="main_menu")
    # Выход в главное меню
    main_menu(message)


def main_menu(message, user_id_disconnect=None):
    if user_id_disconnect is None:
        user_id = message.chat.id
    else:
        user_id = user_id_disconnect
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    find_chat_button = types.KeyboardButton('Поиск собеседника')
    create_group_button = types.KeyboardButton('Создать группу')
    find_group_button = types.KeyboardButton('Поиск группы')
    markup.add(find_chat_button)
    markup.add(find_group_button)
    markup.add(create_group_button)
    bot.send_message(user_id,
                     f"Главное меню",
                     parse_mode='HTML', reply_markup=markup)

    @bot.message_handler(content_types=['text'])
    def get_text_messages(message):
        user_id = message.chat.id
        with sql.connect('todo.db') as con:
            cur = con.cursor()
            cur.execute(f"""
                            SELECT * FROM do WHERE user_id = {user_id};
                        """)
            user = cur.fetchall()
        if user:
            if user[0][1] == "chat":
                print("Пишем в чат")
                if message.text == "Отключиться":
                    with sql.connect('todo.db') as con:
                        cur = con.cursor()
                        cur.execute(f"""
                                        SELECT * FROM connection_couple WHERE first = {user_id};
                                    """)
                        user = cur.fetchall()
                    if user:
                        disconnect_user_from_chat(message, user)

                with sql.connect('todo.db') as con:
                    cur = con.cursor()
                    cur.execute(f"""
                                    SELECT * FROM connection_couple WHERE first = {user_id};
                                """)
                    user_couple = cur.fetchall()
                if user_couple:
                    if user_couple[0][1] == user_id:
                        companion = user_couple[0][2]
                    else:
                        companion = user_couple[0][1]
                    bot.send_message(companion,
                                     f"{message.text}")
            elif user[0][1] == "chat_group":
                if message.text == "Отключиться":
                    # Если отключается админ
                    with sql.connect('todo.db') as con:
                        cur = con.cursor()
                        cur.execute(f"""
                                        SELECT * FROM connection_group WHERE admin = {user_id};
                                    """)
                        user = cur.fetchall()
                    if user:
                        user = user[0][2]
                        disconnect_user_from_group_admin(message, user)
                    else:
                        # Если отключаются участники
                        with sql.connect('todo.db') as con:
                            cur = con.cursor()
                            cur.execute(f"""
                                            SELECT * FROM connection_group WHERE user_two = {user_id};
                                        """)
                            user = cur.fetchall()
                        if user:
                            user = user[0][3]
                            disconnect_user_from_group(message, user)
                        else:
                            with sql.connect('todo.db') as con:
                                cur = con.cursor()
                                cur.execute(f"""
                                                SELECT * FROM connection_group WHERE user_tree = {user_id};
                                            """)
                                user = cur.fetchall()
                            if user:
                                user = user[0][4]
                                disconnect_user_from_group(message, user)
                            else:
                                with sql.connect('todo.db') as con:
                                    cur = con.cursor()
                                    cur.execute(f"""
                                                    SELECT * FROM connection_group WHERE user_four = {user_id};
                                                """)
                                    user = cur.fetchall()
                                if user:
                                    user = user[0][5]
                                    disconnect_user_from_group(message, user)
                                    
                send_message_from_group(message)
            else:
                if message.text == "Поиск собеседника":

                    with sql.connect('todo.db') as con:
                        cur = con.cursor()
                        cur.execute(f"""
                                        SELECT * FROM request_connections_couple WHERE user_id = {user_id};
                                    """)
                        user_req = cur.fetchall()
                    if user_req:
                        bot.send_message(message.chat.id,
                                         f"Поиск уже начат, подождите.")
                    else:
                        find_chat(message)
                        bot.send_message(message.chat.id,
                                         f"Секунду", reply_markup=ReplyKeyboardRemove())

                        markup = types.InlineKeyboardMarkup()
                        callback_button = types.InlineKeyboardButton(text="Отмена поиска", callback_data="cancel_find")
                        markup.add(callback_button)
                        bot.send_message(message.chat.id,
                                         f"Начинаю поиск...", reply_markup=markup)

                elif message.text == "Поиск группы":
                    find_group(message)
                    # main_menu(message)

                elif message.text == "Создать группу":
                    create_group(message)
        else:
            if message.text == "Поиск собеседника":
                markup = types.InlineKeyboardMarkup()
                callback_button = types.InlineKeyboardButton(text="Отмена поиска", callback_data="cancel_find")
                markup.add(callback_button)
                bot.send_message(message.chat.id,
                                 f"Начинаю поиск...", reply_markup=markup)
                find_chat(message)
            elif message.text == "Поиск группы":
                find_group(message)
                # main_menu(message)


def create_group(message):
    user_id = message.chat.id
    id_group = user_id + random.randint(10, 99)
    with sql.connect('todo.db') as con:
        cur = con.cursor()
        cur.execute(f"""
                        SELECT * FROM connection_group WHERE admin = {user_id};
                    """)
        user_group = cur.fetchall()
    if user_group:
        with sql.connect('todo.db') as con:
            cur = con.cursor()
            cur.execute(f"""
                            DELETE FROM connection_group WHERE admin = {user_id};
                        """)
    with sql.connect('todo.db') as con:
        cur = con.cursor()
        cur.execute(f"""
                        INSERT INTO connection_group (id_group,admin,how_many_people) VALUES({id_group},{user_id},1)
                    """)
    what_do_you_do_update(user_id, what="chat_group")
    bot.send_message(message.chat.id,
                     f"Группа удачно создана, дождитесь подключения других участников. "
                     f"В данный момент в группе 1/4 участников.")


def find_group(message):
    user_id = message.chat.id
    with sql.connect('todo.db') as con:
        cur = con.cursor()
        cur.execute(f"""
                        DELETE FROM request_connections_group WHERE user_id = {user_id}
                    """)
        cur = con.cursor()
        cur.execute(f"""
                        INSERT INTO request_connections_group (user_id) VALUES({user_id})
                    """)


def find_chat(message):
    user_id = message.chat.id
    with sql.connect('todo.db') as con:
        cur = con.cursor()
        cur.execute(f"""
                        DELETE FROM request_connections_couple WHERE user_id = {user_id}
                    """)
        cur = con.cursor()
        cur.execute(f"""
                         INSERT INTO request_connections_couple (user_id) VALUES({user_id})
                    """)


def cancel_find(message):
    user_id = message.chat.id
    with sql.connect('todo.db') as con:
        cur = con.cursor()
        cur.execute(f"""
                        SELECT * FROM request_connections_couple WHERE user_id = {user_id};
                    """)
        user = cur.fetchall()
    if user:
        with sql.connect('todo.db') as con:
            cur = con.cursor()
            cur.execute(f"""
                            DELETE FROM request_connections_couple WHERE user_id = {user_id}
                        """)
        print("Поиск отменен")
        main_menu(message)
    else:
        pass


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.message:
        if call.data == "cancel_find":
            try:
                bot.delete_message(call.message.chat.id, call.message.message_id)
                cancel_find(call.message)
            except:
                pass


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
        finally:
            print("hi")
