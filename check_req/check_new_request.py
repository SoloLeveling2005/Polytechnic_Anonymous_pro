import time
import sqlite3 as sql
import threading


def application_couple_threading():
    applications_thread = threading.Thread(target=application_couple)
    applications_thread.daemon = True
    applications_thread.start()


def application_couple():
    while True:
        with sql.connect('todo.db') as con:
            cur = con.cursor()
            cur.execute(f"""
                          SELECT * FROM requests_connections_couple;
                          """)
            requests_users = cur.fetchall()
            if len(requests_users) > 1:
                one_id = requests_users[0][0]
                two_id = requests_users[1][0]
                with sql.connect("todo.db") as con:
                    cur = con.cursor()
                    cur.execute(f"""
                                INSERT INTO connections_couple (first,second) VALUES({one_id},{two_id})
                            """)
                    cur = con.cursor()
                    cur.execute(f"""
                                INSERT INTO connections_couple (first,second) VALUES({two_id},{one_id})
                            """)

                with sql.connect('todo.db') as con:
                    cur = con.cursor()
                    cur.execute(f"""
                                    UPDATE do,
                                    SET do.where_you = "chat"
                                    WHERE do.user_id = {one_id}
                                """)
                    cur = con.cursor()
                    cur.execute(f"""
                                    UPDATE do,
                                    SET do.where_you = "chat"
                                    WHERE do.user_id = {two_id}
                                """)
                with sql.connect('todo.db') as con:
                    cur = con.cursor()
                    cur.execute(f"""
                                      DELETE FROM requests_connections_couple WHERE id_user = {one_id};
                                      """)
                    cur = con.cursor()
                    cur.execute(f"""
                                  DELETE FROM requests_connections_couple WHERE id_user = {two_id};
                                  """)
        time.sleep(2.5)
