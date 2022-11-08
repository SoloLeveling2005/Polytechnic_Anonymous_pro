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
from SimpleQIWI import *
from datetime import date

from connect import token_qiwi, phone, price
from telebot.types import ReplyKeyboardRemove

from connect import bot, token
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


def check_premium_time():
    while True:
        with sql.connect('todo.db') as con:
            cur = con.cursor()
            cur.execute(f"""
                            SELECT user_id,prem_time FROM users;
                        """)
            prem_time = cur.fetchall()
        current_date = date.today()
        for i in prem_time:

            if i[1] == str(current_date).split("-")[2]:
                with sql.connect('todo.db') as con:
                    cur = con.cursor()
                    cur.execute(f"""
                                    UPDATE users SET prem_time = Null WHERE user_id = {i[0]};
                                """)
                bot.send_message(i[0],
                                 f"Месяц истек. Премиум статус отменен", )
        time.sleep(1)


check_premium_time_thread = threading.Thread(target=check_premium_time)
check_premium_time_thread.daemon = True
check_premium_time_thread.start()


def new_prem_user(message, prem_user):
    with sql.connect('todo.db') as con:
        cur = con.cursor()
        cur.execute(f"""
                        UPDATE users SET status = "premium" WHERE user_id = {prem_user};
                    """)
    bot.send_message(message.chat.id,
                     f"Вы изменили аккаунт юзера на premium")
    bot.send_message(prem_user,
                     f"Поздравляю, вы получили премиум")

def dell_prem_user(message, prem_user):
    with sql.connect('todo.db') as con:
        cur = con.cursor()
        cur.execute(f"""
                        UPDATE users SET status = "user" WHERE user_id = {prem_user};
                    """)
    bot.send_message(message.chat.id,
                     f"Вы изменили аккаунт юзера на user")
    bot.send_message(prem_user,
                     f"Ваш премиум аккаунт отменен.")


def it_is_prem_user(user_id) -> bool:
    with sql.connect('todo.db') as con:
        cur = con.cursor()
        cur.execute(f"""
                        SELECT status FROM users WHERE user_id = {user_id};
                    """)
        status = cur.fetchall()
    if status[0][0] == "premium":
        return True
    else:
        return False


def free_requests(user_id) -> bool:
    with sql.connect('todo.db') as con:
        cur = con.cursor()
        cur.execute(f"""
                        SELECT free_requests FROM users WHERE user_id = {user_id};
                    """)
        free_request = cur.fetchall()
    if free_request[0][0] > 1:
        return True
    else:
        return False


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
                    INSERT INTO users (user_id,status,free_requests) VALUES({user_id},"user",40)
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


def message_content_type_voice(message, user_id):
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


def message_content_type_video(message, user_id):
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


def message_content_type_document(message, user_id):
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


def message_content_type_sticker(message, user_id):
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


def message_content_type_photo(message, user_id):
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


def it_is_admin(admin_id) -> bool:
    with sql.connect('todo.db') as con:
        cur = con.cursor()
        cur.execute(f"""
                        SELECT user_id FROM admins WHERE user_id = {admin_id};
                    """)
        admins = cur.fetchall()
    if admins:
        return True
    else:
        return False


def new_admin(message, id_new_admin):
    with sql.connect('todo.db') as con:
        cur = con.cursor()
        cur.execute(f"""
                        INSERT INTO admins user_id VALUES({id_new_admin})
                    """)
    bot.send_message(message.chat.id,
                     f"Вы назначили нового администратора")
    bot.send_message(id_new_admin,
                     f"Вы стали администратором")


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
        markup = types.InlineKeyboardMarkup()
        qiwi_pay = types.InlineKeyboardButton(text="Оплата через киви",
                                              callback_data="qiwi_pay")
        other_pay = types.InlineKeyboardButton(text="Иной способ оплаты",
                                               callback_data="other_pay")
        info_pay = types.InlineKeyboardButton(text="Подробнее",
                                              callback_data="info_pay")
        markup.add(qiwi_pay)
        markup.add(other_pay)
        markup.add(info_pay)
        bot.send_message(message.chat.id,
                         f"Выберите способ оплаты", reply_markup=markup)

    @bot.message_handler(commands=['new_prem_user'])
    def new_prem_user_command(message):
        admin_id = message.chat.id
        if it_is_admin(admin_id):
            # Дописаттььььььььььььььььььььььььььььььььььььььььььььььььььььььььььььььььььььььььььььььь (прописать кому сделать аккаунт)
            new_prem_user(message, user_id)

    @bot.message_handler(commands=['dell_prem_user'])
    def dell_prem_user_command(message):
        admin_id = message.chat.id
        if it_is_admin(admin_id):
            # Дописаттььььььььььььььььььььььььььььььььььььььььььььььььььььььььььььььььььььььььььььььь (прописать кому сделать аккаунт)
            dell_prem_user(message, user_id)

    @bot.message_handler(commands=['new_admin'])
    def new_prem_user_command(message):
        with sql.connect('todo.db') as con:
            cur = con.cursor()
            cur.execute(f"""
                            SELECT user_id FROM admins WHERE user_id = {user_id};
                        """)
            admins = cur.fetchall()
        if admins:
            new_admin(message, admins[0][0])

    @bot.message_handler(content_types=["voice", "video", "document", "sticker", "photo", "text"])
    def get_message(message):
        print("Есть контакт")
        user_id = message.chat.id
        if message.content_type == 'voice':
            if it_is_prem_user(user_id):
                message_content_type_voice(message, user_id)
            else:
                if free_requests(user_id):
                    message_content_type_voice(message, user_id)
                else:
                    bot.send_message(user_id,
                                     f"Пробный периуд истек, для отправки фото, стикеров и прочего приобретите премиум")
        elif message.content_type == 'video':
            if it_is_prem_user(user_id):
                message_content_type_video(message, user_id)
            else:
                if free_requests(user_id):
                    message_content_type_video(message, user_id)
                else:
                    bot.send_message(user_id,
                                     f"Пробный периуд истек, для отправки фото, стикеров и прочего приобретите премиум")
        elif message.content_type == "document":
            if it_is_prem_user(user_id):
                message_content_type_document(message, user_id)
            else:
                if free_requests(user_id):
                    message_content_type_document(message, user_id)
                else:
                    bot.send_message(user_id,
                                     f"Пробный периуд истек, для отправки фото, стикеров и прочего приобретите премиум")
        elif message.content_type == "sticker":
            if it_is_prem_user(user_id):
                message_content_type_sticker(message, user_id)
            else:
                if free_requests(user_id):
                    message_content_type_sticker(message, user_id)
                else:
                    bot.send_message(user_id,
                                     f"Пробный периуд истек, для отправки фото, стикеров и прочего приобретите премиум")
        elif message.content_type == "photo":
            if it_is_prem_user(user_id):
                message_content_type_photo(message, user_id)
            else:
                if free_requests(user_id):
                    message_content_type_photo(message, user_id)
                else:
                    bot.send_message(user_id,
                                     f"Пробный периуд истек, для отправки фото, стикеров и прочего приобретите премиум")
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
                what_do_you_do_update(message.chat.id, what="main_menu")
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
                what_do_you_do_update(message.chat.id, what="main_menu")
                main_menu(message)


def check_qiwi_pay(message):
    user_id = message.chat.id
    time_remained = 60 * 10
    api = QApi(token=token_qiwi, phone=phone)
    comment = api.bill(price)
    print("Pay %i rub for %s with comment '%s'" % (price, phone, comment))

    with sql.connect("todo.db") as con:
        cur = con.cursor()
        cur.execute(f"""
                INSERT INTO request_qiwi (user_id,special_code) VALUES({user_id},"{comment}")
                """)
        print("Данные добавлены в таблицу request_qiwi")

    bot.send_message(message.chat.id,
                     f"Ваш код {comment}. Номер телефона {phone}")

    api.start()  # Начинаем прием платежей
    while True:
        if api.check(comment):  # Проверяем статус # {'c6704b68-7ca2-4a32-a4cb-79e0bbd337e3': {'price': 1,
            # 'currency': 643, 'success': True}}
            print("Платёж получен!")
            bot.send_message(message.chat.id,
                             f"Платеж успешно получен! Теперь вы премиум аккаунт")
            with sql.connect('todo.db') as con:
                cur = con.cursor()
                cur.execute(f"""
                                UPDATE users SET status = "premium" WHERE user_id = {user_id};
                            """)
            current_date = date.today()
            with sql.connect('todo.db') as con:
                cur = con.cursor()
                cur.execute(f"""
                                UPDATE users SET prem_time = {str(current_date).split("-")[2]} WHERE user_id = {user_id};
                            """)
            break
        if time_remained < 0:
            bot.send_message(message.chat.id,
                             f"Код деактивирован")
            with sql.connect('todo.db') as con:
                cur = con.cursor()
                cur.execute(f"""
                                DELETE FROM request_qiwi WHERE user_id = {user_id}
                            """)
            break
        time_remained -= 1
        time.sleep(1)
    api.stop()
    main_menu(message)


def check_other_pay():
    pass


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    user_id = call.message.chat.id
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
        elif call.data == "qiwi_pay":
            try:
                bot.delete_message(call.message.chat.id, call.message.message_id)
            except:
                pass
            second_now = time.time()
            code = str(second_now).split(".")[0] + str(user_id)
            with sql.connect('todo.db') as con:
                cur = con.cursor()
                cur.execute(f"""
                                    SELECT * FROM request_qiwi WHERE user_id = {user_id};
                                """)
                request_qiwi_db = cur.fetchall()
            if request_qiwi_db:
                bot.send_message(call.message.chat.id,
                                 f"Ваш код {request_qiwi_db[0][1]}. Номер телефона {phone}")
                main_menu(call.message)
            else:
                check_qiwi_pay(call.message)

        elif call.data == "other_pay":
            try:
                bot.delete_message(call.message.chat.id, call.message.message_id)
            except:
                pass

            second_now = time.time()
            code = str(second_now).split(".")[0] + str(user_id)
            with sql.connect('todo.db') as con:
                cur = con.cursor()
                cur.execute(f"""
                                    SELECT * FROM request_payment_with_confirmation WHERE user_id = {user_id};
                                """)
                request_payment_with_confirmation_db = cur.fetchall()
            if request_payment_with_confirmation_db:
                bot.send_message(call.message.chat.id,
                                 f"Ваш код {request_payment_with_confirmation_db[0][1]}. Номер телефона {phone}")
                main_menu(call.message)
            else:
                with sql.connect("todo.db") as con:
                    cur = con.cursor()
                    cur.execute(f"""
                            INSERT INTO request_payment_with_confirmation (user_id,special_code) VALUES({user_id},"{code}")
                            """)
                    print("Данные добавлены в таблицу request_payment_with_confirmation")

                bot.send_message(call.message.chat.id,
                                 f"Ваш код {code}. Номер телефона {phone}")


        elif call.data == "info_pay":
            try:
                bot.delete_message(call.message.chat.id, call.message.message_id)
            except:
                pass
            bot.send_message(call.message.chat.id,
                             f""" У нас присутсвует два способа оплаты. \n1. Через Qiwi. После платежа вам 
                             автоматически присвоется вип статус. Вы получаете номер телефона и специальный код. В 
                             переводах в Qiwi вы указываете номер телефона получателя и СПЕЦИАЛЬНЫЙ КОД ОСТАВЛЯЕТСЯ В 
                             КОММЕНТАРИЯХ! ВНИМАНИЕ! ЕСЛИ ВЫ НЕКОРЕКТНО УКАЖИТЕ КОД, ПЛАТЕЖ НЕ ПРОЙДЕТ И ВАМ ПРИДЕТСЯ 
                             ОБРАЩАТЬСЯ В ТЕХ ПОДДЕРЖКУ. \n2. Через Каспи и Билайн. ВНИМАНИЕ! 
                             При оплате через второй способ вам начислиться премиум статус в течении 48 часов. Вы 
                             получаете номер телефона и код. Код оставляете в комментариях при переводе на номер телефона. 
                             Код действителен в течении 10 минут. После чего надо будет 
                             заново пересоздать его (повторить те же действия). 
                             Если что то пошло не так, обращяйтесь в тех поддержку по номеру +77774208321
                            """)
            main_menu(call.message)


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
            bot = telebot.TeleBot(token)
            bot.send_message(1303257033,
                             'Сообщение системы: Произошла перезагрузка программы')
            os.system('python main.py')
        finally:
            print("hi")
