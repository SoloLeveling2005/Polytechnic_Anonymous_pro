import sqlite3 as sql


def create_bd():
    with sql.connect("todo.db") as con:
        cur = con.cursor()
        cur.execute(f"""
                        CREATE TABLE IF NOT EXISTS users (
                            ID INTEGER NOT NULL,
                            user_id INTEGER NOT NULL,
                            info VARCHAR, 
                            status VARCHAR NOT NULL,
                            prem_time VARCHAR,
                            PRIMARY KEY(ID AUTOINCREMENT)
                        )
                    """)
    with sql.connect("todo.db") as con:
        cur = con.cursor()
        cur.execute(f"""
                        CREATE TABLE IF NOT EXISTS do (
                            user_id INTEGER NOT NULL,
                            where_you VARCHAR NOT NULL
                        )
                    """)
    with sql.connect("todo.db") as con:
        cur = con.cursor()
        cur.execute(f"""
                        CREATE TABLE IF NOT EXISTS connection_couple (
                            ID INTEGER NOT NULL,
                            first INTEGER NOT NULL,
                            second INTEGER NOT NULL,
                            PRIMARY KEY(ID AUTOINCREMENT)
                        )
                    """)
    with sql.connect("todo.db") as con:
        cur = con.cursor()
        cur.execute(f"""
                        CREATE TABLE IF NOT EXISTS connection_group (
                            ID INTEGER NOT NULL,
                            id_group VARCHAR NOT NULL,
                            admin INTEGER NOT NULL,
                            user_two INTEGER,
                            user_three INTEGER,
                            user_four INTEGER,
                            how_many_people INTEGER NOT NULL,
                            PRIMARY KEY(ID AUTOINCREMENT)
                        )
                    """)
    with sql.connect("todo.db") as con:
        cur = con.cursor()
        cur.execute(f"""
                        CREATE TABLE IF NOT EXISTS request_connections_couple (
                            user_id INTEGER NOT NULL
                        )
                    """)
    with sql.connect("todo.db") as con:
        cur = con.cursor()
        cur.execute(f"""
                        CREATE TABLE IF NOT EXISTS request_connections_group (
                            user_id INTEGER NOT NULL
                        )
                    """)
