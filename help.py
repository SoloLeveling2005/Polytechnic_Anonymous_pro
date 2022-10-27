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








#################################################################################################





def main_menu(message, step):
    checking_condition(message, step=step)


@bot.message_handler(commands=['start'])
def start(message):
    main_menu(message, step="start")


@bot.message_handler(commands=['main_menu'])
def start(message):
    main_menu(message, step="main_menu")



@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id,
                     "Доступные команды:")
    bot.send_message(message.chat.id,
                     "/main_menu " + "- перейти в главное меню")
    bot.send_message(message.chat.id,
                     "/find_chat " + "- поиск анонимуса")
    bot.send_message(message.chat.id,
                     "/find_group " + "- поиск группы анонимус")
    bot.send_message(message.chat.id,
                     "/cancel_find " + "- отмена поиска")
    bot.send_message(message.chat.id,
                     "/disconnect " + "- отсоединиться от чата")
    bot.send_message(message.chat.id,
                     "Вам не обязательно их вводить, они будут доступны в виде кнопок ниже")


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == '🏠 Главное меню':
        pass
    elif message.text == '🔎 Поиск собеседника':
        pass
    elif message.text == '🔎 Поиск группы':
        pass
    elif message.text == '❌ Отмена поиска':
        pass
    elif message.text == '🛑 Отключиться':
        pass
    else:
        pass






#################################################################################################






class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def main_menu(message, user_id, message_send="🏠 Главное меню"):
    chat_id = user_id
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    find_chat = types.KeyboardButton('🔎 Поиск собеседника')
    find_group = types.KeyboardButton('🔎 Поиск группы')
    markup.add(find_chat)
    markup.add(find_group)
    bot.send_message(chat_id,
                     message_send,
                     parse_mode='HTML', reply_markup=markup)


def checking_condition(message, step):
    user_id = message.chat.id
    with sql.connect('todo.db') as con:
        cur = con.cursor()
        cur.execute(f"""
                        SELECT * FROM users WHERE user_id = {user_id};
                    """)
        request_data = cur.fetchall()
    if request_data is not []:
        condition = request_data[0][2]
        where_user = request_data[0][3]['where_user']
        if condition == "main menu":
            pass
        elif condition == "find chat":
            pass
        elif condition == "cancel chat":
            pass
        elif condition == "disconnected chat":
            pass
        elif condition == "chat":
            if step == "main menu":
                disconnected_user(message, where_user)  # Отключаем юзера от чата
        elif condition == "":
            if step == "main menu":
                disconnected_user(message, where_user)  # Отключаем юзера от чата
    else:
        info = {
            'where_user': 'None',
        }
        info = json.dumps(info)
        request = f"INSERT INTO users (user_id,condition,info,status) VALUES({user_id},'main menu','{info}','user')"
        cur.execute(request)


def add_user_db_users(message):
    pass


def disconnected_user(message, where_user):
    user_id = message.chat.id
    if where_user == "None":
        pass
    elif where_user == "group":
        with sql.connect('todo.db') as con:
            cur = con.cursor()
            cur.execute(f"""
                            SELECT * FROM connections_groups WHERE user = {user_id};
                        """)
            request_data = cur.fetchall()
        if request_data is not []:
            admin_group = request_data[0][2]

            if user_id == admin_group:
                cur.execute(f"""
                                DELETE FROM connections_groups WHERE admin = {user_id};
                            """)
            else:
                cur.execute(f"""
                                SELECT * FROM connections_groups WHERE user = {user_id};
                            """)
                request_data = cur.fetchall()
                id_group = request_data[0][1]
                cur.execute(f"""
                                DELETE FROM connections_groups WHERE user = {user_id};
                            """)
                cur.execute(f"""
                                SELECT * FROM connections_groups WHERE id_group = {id_group};
                            """)
                request_data = cur.fetchall()
                for i in request_data:
                    user_id = i[3]
                    bot.send_message(user_id,
                         f"Один из Анонимусов вышел из чата",
                         parse_mode='HTML')
        else:
            print(bcolors.WARNING + "Ошибка! Пользователь состоит в группе но его нет в БД с подключениями("
                                    "connections_groups)")
    elif where_user == "chat":
        with sql.connect('todo.db') as con:
            cur = con.cursor()
            cur.execute(f"""
                            SELECT * FROM connections_couple WHERE first = {user_id};
                        """)
            request_data = cur.fetchall()
            if request_data is not []:
                first = request_data[0][1]
                second = request_data[0][2]
                cur.execute(f"""
                                DELETE FROM connections_couple WHERE first = {user_id};
                            """)
                bot.send_message(first,
                                 "Вы вышли из чата",
                                 parse_mode='HTML')
                main_menu(message, first)

                cur.execute(f"""
                                DELETE FROM connections_couple WHERE second = {user_id};
                            """)
                bot.send_message(second,
                                 "Ваш собеседник покинул чат. Вы вышли из чата",
                                 parse_mode='HTML')
                main_menu(message, second)
            else:
                print(bcolors.WARNING + "Ошибка! Пользователь находится в чате но его нет в БД с подключениями("
                                        "connections_couple)")




# @bot.message_handler(content_types=["voice", "video", "document", "sticker", "photo", "text"])
# def get_message(message):
#     print("Есть контакт")
#     if message.content_type == 'voice':
#         audio_id = message.voice.file_id
#         bot.send_audio(message.chat.id, audio_id)
#         print(audio_id)
#     elif message.content_type == 'video':
#         video_id = message.video.file_id
#         bot.send_audio(message.chat.id, video_id)
#         print(video_id)
#     elif message.content_type == "document":
#         document_id = message.document.file_id
#         bot.send_document(message.chat.id, document_id)
#         print(document_id)
#     elif message.content_type == "sticker":
#         sticker_id = message.sticker.file_id
#         bot.send_sticker(message.chat.id, sticker_id)
#         print(sticker_id)
#     elif message.content_type == "photo":
#         img = message.photo[0].file_id
#         bot.send_photo(message.chat.id, img)
#         print(img)
#     elif message.content_type == "text":
#         print(message)
#         bot.send_message(message.chat.id,
#                          message.text)
#
