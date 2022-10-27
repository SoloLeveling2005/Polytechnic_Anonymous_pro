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

print("Нажмите Ctrl+C если хотите завершить работу бота")

create_db()


@bot.message_handler(commands=['start', 'main_menu'])
def main_menu(message):
    # Проверить находится ли пользователь в другом моменте(шаге)
    # Если он в моменте chat то отменяет его и выходит в главное меню
    # Если он в моменте find_chat или find_group то отменяет его и выходит в главное меню
    # Если он в моменте cancel_find или disconnect или в main_menu то выходим в главное меню
    pass


@bot.message_handler(commands=['find_chat'])
def find_chat(message):
    # Проверить находится ли пользователь в другом моменте(шаге)
    # Если он в моменте chat то сообщает что уже открыто соединение, закройте его
    # Если он в шаге main_menu или cancel_find или disconnect то начинает поиск
    # Если он в шаге main_menu или cancel_find или disconnect то начинает поиск
    pass



@bot.message_handler(commands=['find_group'])
def find_group(message):
    pass


@bot.message_handler(commands=['cancel_find'])
def cancel_find(message):
    pass


@bot.message_handler(commands=['disconnect'])
def disconnect(message):
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

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == '🏠 Главное меню':
        main_menu(message)
    elif message.text == '🔎 Поиск собеседника':
        find_chat(message)
    elif message.text == '🔎 Поиск группы':
        find_group(message)
    elif message.text == '❌ Отмена поиска':
        cancel_find(message)
    elif message.text == '🛑 Отключиться':
        disconnect(message)
    else:
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
