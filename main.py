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
        print(users)
        if users:
            if len(users) >= 1:
                user_id = users[0][0]

                with sql.connect('todo.db') as con:
                    cur = con.cursor()
                    cur.execute(f"""
                                    SELECT * FROM connection_group WHERE how_many_people < 4
                                """)
                    groups = cur.fetchall()

                if groups:
                    len_users = len(users)
                    index = 0
                    rand_index = random.randint(0, len_users - 1)
                    group = groups[rand_index]
                    # print(users)
                    # print(rand_index)
                    # print(len_users-1)
                    group_id = group[1]
                    admin = group[2]
                    how_many_people = group[4]
                    with sql.connect("todo.db") as con:
                        cur = con.cursor()
                        cur.execute(f"""
                                        INSERT INTO connection_group (id_group,admin,user_id,how_many_people) 
                                        VALUES("{group_id}",{admin},{user_id},{how_many_people + 1})
                                    """)
                    with sql.connect('todo.db') as con:
                        cur = con.cursor()
                        cur.execute(f"""
                                        UPDATE connection_group SET how_many_people = {how_many_people + 1} WHERE 
                                        id_group = "{group_id}"; 
                                    """)
                    with sql.connect('todo.db') as con:
                        cur = con.cursor()
                        cur.execute(f"""
                                      DELETE FROM request_connections_group WHERE user_id = {user_id};
                                      """)

                    with sql.connect('todo.db') as con:
                        cur = con.cursor()
                        cur.execute(f"""
                                        SELECT user_id FROM connection_group WHERE id_group = "{group_id}"
                                    """)
                        users = cur.fetchall()
                    for user in users:
                        if user[0] == user_id:
                            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                            disconnect_chat = types.KeyboardButton('Отключиться')
                            markup.add(disconnect_chat)
                            bot.send_message(user[0],
                                             f"Нашел, ваши собеседники онлайн.", reply_markup=markup)
                        else:

                            bot.send_message(user[0],
                                             f"Анонимус подключился")

                    what_do_you_do_update(user_id, what="chat_group")

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
                with sql.connect('todo.db') as con:
                    cur = con.cursor()
                    cur.execute(f"""
                                    SELECT where_you FROM do WHERE user_id = {one_id};
                                """)
                    user1 = cur.fetchall()
                with sql.connect('todo.db') as con:
                    cur = con.cursor()
                    cur.execute(f"""
                                    SELECT where_you FROM do WHERE user_id = {two_id};
                                """)
                    user2 = cur.fetchall()
                if user1 and user2:
                    if user1[0][0] == "find_chat" and user2[0][0] == "find_chat":
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
    with sql.connect('todo.db') as con:
        cur = con.cursor()
        cur.execute(f"""
                        SELECT user_id FROM connection_group WHERE user_id = "{user_id}"
                    """)
        users_id = cur.fetchall()
    if users_id:
        pass
    else:
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
    admin = user[0][2]
    group_id = user[0][1]
    if user_id == admin:
        with sql.connect('todo.db') as con:
            cur = con.cursor()
            cur.execute(f"""
                            SELECT user_id FROM connection_group WHERE id_group = "{group_id}"
                        """)
            users_id = cur.fetchall()
        for user_id_for in users_id:
            if user_id == user_id_for[0]:
                bot.send_message(user_id_for[0],
                                 f"Вы завершили групповой чат",
                                 parse_mode='HTML')
                main_menu(message, user_id_disconnect=user_id_for[0])
            else:
                bot.send_message(user_id_for[0],
                                 f"Организатор завершил групповой чат",
                                 parse_mode='HTML')
                main_menu(message, user_id_disconnect=user_id_for[0])
        with sql.connect('todo.db') as con:
            cur = con.cursor()
            cur.execute(f"""
                            DELETE FROM connection_group WHERE id_group = "{group_id}";
                          """)
    else:
        with sql.connect('todo.db') as con:
            cur = con.cursor()
            cur.execute(f"""
                            SELECT user_id FROM connection_group WHERE id_group = "{group_id}"
                        """)
            users_id = cur.fetchall()

        with sql.connect('todo.db') as con:
            cur = con.cursor()
            cur.execute(f"""
                            DELETE FROM connection_group WHERE user_id = "{user_id}";
                          """)
        for user_id1 in users_id:
            if user_id == user_id1:
                bot.send_message(user_id1[0],
                                 f"Вы вышли из группового чата",
                                 parse_mode='HTML')
                main_menu(message, user_id_disconnect=user_id[0])
            bot.send_message(user_id1[0],
                             f"Один из собеседников вышел из чата",
                             parse_mode='HTML')


def send_message_from_group(message):
    user_id = message.chat.id
    with sql.connect('todo.db') as con:
        cur = con.cursor()
        cur.execute(f"""
                        SELECT id_group FROM connection_group WHERE user_id = {user_id};
                    """)
        group_id = cur.fetchall()
    group_id = group_id[0][0]
    with sql.connect('todo.db') as con:
        cur = con.cursor()
        cur.execute(f"""
                        SELECT user_id FROM connection_group WHERE id_group = {group_id};
                    """)
        users = cur.fetchall()
    for users_id in users:
        print(users_id)
        print(users_id[0])
        if user_id == users_id[0]:
            pass
        else:
            bot.send_message(users_id[0],
                             f"" + message.text)


def send_message_from_group_all(message, subject, what):
    user_id = message.chat.id
    with sql.connect('todo.db') as con:
        cur = con.cursor()
        cur.execute(f"""
                            SELECT id_group FROM connection_group WHERE user_id = {user_id};
                        """)
        group_id = cur.fetchall()
    group_id = group_id[0][0]
    with sql.connect('todo.db') as con:
        cur = con.cursor()
        cur.execute(f"""
                            SELECT user_id FROM connection_group WHERE id_group = {group_id};
                        """)
        users = cur.fetchall()
    for users_id in users:
        print(users_id)
        print(users_id[0])
        if user_id == users_id[0]:
            pass
        else:
            if what == "photo":
                print("photo")
                bot.send_photo(users_id[0], subject)
            elif what == "voice":
                print("voice")
                bot.send_audio(users_id[0], subject)
            elif what == "video":
                print("video")
                bot.send_video(users_id[0], subject)
            elif what == "document":
                print("document")
                bot.send_document(users_id[0], subject)
            elif what == "sticker":
                print("sticker")
                bot.send_sticker(users_id[0], subject)


@bot.message_handler(commands=['start'])
def start(message):
    print("start")
    reg_user_insert(message)
    what_do_you_do_insert(message.chat.id, what="main_menu")
    # Выход в главное меню
    main_menu(message)


def main_menu(message, user_id_disconnect=None):
    try:
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
    except:
        pass

    @bot.message_handler(commands=['buy_premium'])
    def buy_premium(message):
        pass
    @bot.message_handler(content_types=["voice", "video", "document", "sticker", "photo", "text"])
    def get_message(message):
        print("Есть контакт")
        if message.content_type == 'voice':

            user_id = message.chat.id
            with sql.connect('todo.db') as con:
                cur = con.cursor()
                cur.execute(f"""
                            SELECT * FROM do WHERE user_id = {user_id};
                        """)
                user = cur.fetchall()
            if user:
                if user[0][1] == "chat":
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
                        audio_id = message.voice.file_id
                        bot.send_audio(companion, audio_id)

                elif user[0][1] == "chat_group":
                    audio_id = message.voice.file_id
                    send_message_from_group_all(message, audio_id, what="voice")
        elif message.content_type == 'video':

            user_id = message.chat.id
            with sql.connect('todo.db') as con:
                cur = con.cursor()
                cur.execute(f"""
                                                                                SELECT * FROM do WHERE user_id = {user_id};
                                                                            """)
                user = cur.fetchall()
            if user:
                if user[0][1] == "chat":
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
                        video_id = message.video.file_id
                        bot.send_video(companion, video_id)

                elif user[0][1] == "chat_group":
                    video_id = message.video.file_id
                    send_message_from_group_all(message, video_id, what="video")
        elif message.content_type == "document":

            user_id = message.chat.id
            with sql.connect('todo.db') as con:
                cur = con.cursor()
                cur.execute(f"""
                                                                    SELECT * FROM do WHERE user_id = {user_id};
                                                                """)
                user = cur.fetchall()
            if user:
                if user[0][1] == "chat":
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
                        document_id = message.document.file_id
                        bot.send_document(companion, document_id)

                elif user[0][1] == "chat_group":
                    document_id = message.document.file_id
                    send_message_from_group_all(message, document_id, what="document")
        elif message.content_type == "sticker":
            user_id = message.chat.id
            with sql.connect('todo.db') as con:
                cur = con.cursor()
                cur.execute(f"""
                                                        SELECT * FROM do WHERE user_id = {user_id};
                                                    """)
                user = cur.fetchall()
            if user:
                if user[0][1] == "chat":
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
                        sticker_id = message.sticker.file_id
                        bot.send_sticker(companion, sticker_id)

                elif user[0][1] == "chat_group":
                    sticker_id = message.sticker.file_id
                    send_message_from_group_all(message, sticker_id, what="sticker")

        elif message.content_type == "photo":
            user_id = message.chat.id
            with sql.connect('todo.db') as con:
                cur = con.cursor()
                cur.execute(f"""
                                            SELECT * FROM do WHERE user_id = {user_id};
                                        """)
                user = cur.fetchall()
            if user:
                if user[0][1] == "chat":
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
                        img = message.photo[0].file_id
                        bot.send_photo(companion, img)

                elif user[0][1] == "chat_group":
                    img = message.photo[0].file_id
                    send_message_from_group_all(message, img, what="photo")

        elif message.content_type == "text":
            user_id = message.chat.id
            with sql.connect('todo.db') as con:
                cur = con.cursor()
                cur.execute(f"""
                                SELECT * FROM do WHERE user_id = {user_id};
                            """)
                user = cur.fetchall()
            print(user)
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
                        else:
                            main_menu(message)

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
                        # Отключиться
                        with sql.connect('todo.db') as con:
                            cur = con.cursor()
                            cur.execute(f"""
                                            SELECT * FROM connection_group WHERE user_id = {user_id};
                                        """)
                            users = cur.fetchall()
                        if users:
                            disconnect_user_from_group(message, users)
                        else:
                            main_menu(message)
                    else:
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
                            callback_button = types.InlineKeyboardButton(text="Отмена поиска",
                                                                         callback_data="cancel_find")
                            markup.add(callback_button)
                            bot.send_message(message.chat.id,
                                             f"Начинаю поиск...", reply_markup=markup)

                    elif message.text == "Поиск группы":
                        with sql.connect('todo.db') as con:
                            cur = con.cursor()
                            cur.execute(f"""
                                            SELECT * FROM request_connections_group WHERE user_id = {user_id};
                                        """)
                            user_req = cur.fetchall()
                        if user_req:
                            bot.send_message(message.chat.id,
                                             f"Поиск уже начат, подождите.")
                        else:
                            find_group(message)
                            bot.send_message(message.chat.id,
                                             f"Секунду", reply_markup=ReplyKeyboardRemove())

                            markup = types.InlineKeyboardMarkup()
                            callback_button = types.InlineKeyboardButton(text="Отмена поиска",
                                                                         callback_data="cancel_find_group")
                            markup.add(callback_button)
                            bot.send_message(message.chat.id,
                                             f"Начинаю поиск...", reply_markup=markup)

                        # main_menu(message)

                    elif message.text == "Создать группу":
                        create_group(message)
            # else:
            #     if message.text == "Поиск собеседника":
            #         markup = types.InlineKeyboardMarkup()
            #         callback_button = types.InlineKeyboardButton(text="Отмена поиска", callback_data="cancel_find")
            #         markup.add(callback_button)
            #         bot.send_message(message.chat.id,
            #                          f"Начинаю поиск...", reply_markup=markup)
            #         find_chat(message)
            #     elif message.text == "Поиск группы":
            #         find_group(message)
            #         # main_menu(message)

# Нужен запуск скрипта если произошла перезагрузка бота
main_menu(1234)


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
                        INSERT INTO connection_group (id_group,admin,user_id,how_many_people) VALUES({id_group},{user_id},{user_id},1)
                    """)
    what_do_you_do_update(user_id, what="chat_group")
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    disconnect_chat = types.KeyboardButton('Отключиться')
    markup.add(disconnect_chat)
    bot.send_message(message.chat.id,
                     f"Группа удачно создана, дождитесь подключения других участников. В данный момент в группе 1/4 "
                     f"участников. Отключение от группы приведет к ее удалению и удалению всех подключенных учатсников "
                     f"из нее.", reply_markup=markup)


def find_group(message):
    user_id = message.chat.id
    with sql.connect('todo.db') as con:
        cur = con.cursor()
        cur.execute(f"""
                        DELETE FROM request_connections_group WHERE user_id = {user_id}
                    """)
    with sql.connect('todo.db') as con:
        cur = con.cursor()
        cur.execute(f"""
                        INSERT INTO request_connections_group (user_id) VALUES({user_id})
                    """)
    what_do_you_do_update(user_id, what="find_group")


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
    what_do_you_do_update(user_id, what="find_chat")


def cancel_find(message):
    user_id = message.chat.id
    with sql.connect('todo.db') as con:
        cur = con.cursor()
        cur.execute(f"""
                        SELECT * FROM do WHERE user_id = {user_id};
                    """)
        user = cur.fetchall()
    if user:
        if user[0][1] == 'find_chat':
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
                bot.send_message(message.chat.id,
                                 f"Поиск отменен")
                print("Поиск отменен")
                what_do_you_do_insert(message.chat.id, what="main_menu")
                main_menu(message)
            else:
                pass
        elif user[0][1] == 'find_group':
            with sql.connect('todo.db') as con:
                cur = con.cursor()
                cur.execute(f"""
                                SELECT * FROM request_connections_group WHERE user_id = {user_id};
                            """)
                user = cur.fetchall()
            if user:
                with sql.connect('todo.db') as con:
                    cur = con.cursor()
                    cur.execute(f"""
                                    DELETE FROM request_connections_group WHERE user_id = {user_id}
                                """)
                bot.send_message(message.chat.id,
                                 f"Поиск отменен")
                print("Поиск отменен")
                what_do_you_do_insert(message.chat.id, what="main_menu")
                main_menu(message)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.message:
        if call.data == "cancel_find":
            try:
                bot.delete_message(call.message.chat.id, call.message.message_id)
                cancel_find(call.message)
            except:
                pass
        elif call.data == "cancel_find_group":
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
