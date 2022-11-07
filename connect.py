import telebot
from SimpleQIWI import *

# token = '5488566542:AAEGQsiDrnLjwFCQb4kmbn7EJYnZqoaIfxk'
token = '2072843035:AAEaTE2Zwh3dCpNPqdZ6w5QW87_HSpktyDY'
bot = telebot.TeleBot(token, parse_mode="HTML")
token_qiwi = "e457f630e4821937cacf9c4cf2015467"
phone = "+77712476799"

api = QApi(token=token_qiwi, phone=phone)
# (print(api.balance))

price = 1
comment = api.bill(price)

print("Pay %i rub for %s with comment '%s'" % (price, phone, comment))


@api.bind_echo()  # Создаем эхо-функцию.  Она будет вызываться при каждом новом полученном платеже. В качестве аргументов ей                  # передаётся информация о платеже.
def foo(bar):
    print("New payment!")
    print(bar)  # {'c6704b68-7ca2-4a32-a4cb-79e0bbd337e3': {'price': 1, 'currency': 643, 'success': True}}
    api.stop()


api.start()
