from telebot import TeleBot
from telebot import TeleBot
from db.models import init_db
from handlers.start import handle_start_message, handler_start
from handlers.callback import handler_callback

bot = TeleBot("7713812500:AAFBkZRpgYKbatoUkj0N-niA-5nXbYWZOJg")

@bot.message_handler(commands=['start'])
def start_handler(message):
    handler_start(bot, message)
    
@bot.message_handler(func=lambda message: True)    
def main_message_handler(message):
    if message.text == "На главную": handle_start_message(bot, message.chat.id)
    
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    handler_callback(bot, call)


if __name__ == "__main__":
    init_db()
    print("Бот успешно запустился")
    bot.infinity_polling()