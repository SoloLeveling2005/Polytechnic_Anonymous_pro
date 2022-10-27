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


# from main import chat, main_menu

def verify_job(message, where_was_called):
    user_id = message.chat.id
    with sql.connect('todo.db') as con:
        cur = con.cursor()
        cur.execute(f"""
                        SELECT * FROM do WHERE user_id = {user_id};
                    """)
        verify = cur.fetchall()

    if verify:
        if verify[0][2] == "chat":
            pass




def insert_user_into_db_requests_connections_couple(message):
    print("запустился скрипт с добавлением пользователей")
    user_id = message.chat.id
    with sql.connect('todo.db') as con:
        cur = con.cursor()
        cur.execute(f"""
                      INSERT INTO requests_connections_couple (user_id) VALUES({user_id})
                      """)


