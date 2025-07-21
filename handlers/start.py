from sqlalchemy.orm import Session
from telebot import types, TeleBot
from db.handlers import create_user, get_user
from db.connect import engine

def handle_start_message(bot: TeleBot, chat_id: int):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton('На главную')
    markup.add(item1)
    bot.send_message(chat_id, "Спасибо, что присоединились к нам! 🎉", reply_markup=markup)
    
    
    markup = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton("О проекте",callback_data="about_project")
    button2 = types.InlineKeyboardButton("Запись на игру",callback_data="sign_for_game")
    button3 = types.InlineKeyboardButton("Подписка",callback_data="subscribe")
    button4 = types.InlineKeyboardButton("Медиа каналы",callback_data="media_channels")
    button5 = types.InlineKeyboardButton("Наши мероприятия", callback_data="our_events")   
    button6 = types.InlineKeyboardButton("Наши продукты", callback_data="our_products")   
    
    markup.add(button1, button2, button3, button6, button5, button4, row_width=2)
    button8 = types.InlineKeyboardButton("Вопросы и поддержка", callback_data="support")   
    button7 = types.InlineKeyboardButton("Рефералка и баланс", callback_data="ref_program")   

    markup.add(button7, button8, row_width=1)
    bot.send_message(chat_id, "Проект 'За любовь' — это движение, которое объединяет людей, стремящихся к осознанным отношениям, личностному росту и вдохновляющему сообществу.\n\nЧерез наши игры, курсы, клубы знакомств и партнерскую программу вы найдете новые возможности для счастья и успеха. Выберите раздел, чтобы узнать больше:", reply_markup=markup)
    
    


def handler_start(bot: TeleBot, message: types.Message):
    with Session(engine) as session:
        user = get_user(session, message.from_user.id)
        
        if user and user.has_ended:            
            handle_start_message(bot, message.chat.id)
        else:
            if not user:
                ref = 1
                if " " in message.text:
                    referrer_candidate = message.text.split()[1]
                    
                    # Пробуем преобразовать строку в число
                    try:
                        referrer_candidate = int(referrer_candidate)

                        # Проверяем на несоответствие TG ID пользователя TG ID реферера
                        if message.from_user.id != referrer_candidate: 
                            ref = referrer_candidate
                    except ValueError:
                        pass
                user = create_user(
                    session, 
                    message.chat.id, 
                    message.from_user.full_name, 
                    message.from_user.username, 
                    ref)
            
            if user.city == "":
                bot.send_message(message.chat.id, """
Добро пожаловать в мир 'За любовь'! 🌟 \n\nМы создали уникальную экосистему, чтобы помочь вам строить гармоничные отношения, находить единомышленников и раскрывать свой потенциал. Чтобы мы могли предложить вам самые актуальные мероприятия, игры и возможности в вашем регионе, пожалуйста, укажите ваш город и поделитесь номером телефона, привязанным к Telegram. Это займет всего минуту!""")
                msg = bot.send_message(message.chat.id, "Из какого вы города?")
                bot.register_next_step_handler(msg, handler_city, bot)
            elif user.phone == "":
                keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
                reg_button = types.KeyboardButton(text="Отправить номер телефона", 
                request_contact=True)
                keyboard.add(reg_button)
                bot.send_message(message.chat.id, "Отправьте номер телефона по кнопке ниже", reply_markup=keyboard)
                bot.register_next_step_handler(message, handle_phone, bot)
                
            
def handler_city(message: types.Message, bot: TeleBot):
    if message.text.startswith("/") or len(message.text) < 3:
        bot.send_message(message.chat.id, "Введите корректный город")
        bot.register_next_step_handler(message, handler_city, bot)
    else:
        with Session(engine) as session:
            user = get_user(session, message.chat.id)
            user.city = message.text
            session.commit()
            
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            reg_button = types.KeyboardButton(text="Отправить номер телефона", 
            request_contact=True)
            keyboard.add(reg_button)
            bot.send_message(message.chat.id, "Отправьте номер телефона по кнопке ниже", reply_markup=keyboard)
            bot.register_next_step_handler(message, handle_phone, bot)

def handle_phone(message: types.Message, bot: TeleBot):
    try:
        phone_number = message.contact.phone_number
        if phone_number:
            with Session(engine) as session:
                user = get_user(session, message.chat.id)
                user.phone = str(phone_number)
                user.has_ended = True
                session.commit()
                handle_start_message(bot, message.chat.id)
    except:
        bot.send_message(message.chat.id, "Номер телефона не получен")
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        reg_button = types.KeyboardButton(text="Отправить номер телефона", 
        request_contact=True)
        keyboard.add(reg_button)
        bot.send_message(message.chat.id, "Отправьте номер телефона по кнопке ниже", reply_markup=keyboard)
        bot.register_next_step_handler(message, handle_phone, bot)