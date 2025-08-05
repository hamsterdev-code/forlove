from sqlalchemy.orm import Session
from telebot import types, TeleBot
from db.handlers import create_user, get_user
from db.connect import engine
from yookassa import Configuration, Payment
import uuid
from db.models import PayMetadata


SECRET_API = "live_8sy3urnb4lO3FxsGsaxANT4wC20ZMT97Fb-PAnCD7Sk"
SHOP_ID = 1124758

Configuration.configure(SHOP_ID, SECRET_API)

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
        
        if " " in message.text:
            go_code = message.text.split()[1]
            if go_code == "pay_150" and user != None:
                with Session(engine) as session:
                
                    idempotence_key = str(uuid.uuid4())
                    
                    pay_metadata = PayMetadata(
                        user_id = user.id,
                        price = 150,
                        product = "poster",
                        procent_balance = 50,
                        inner_balance = 0
                    )
                    session.add(pay_metadata)
                    session.commit()
                
                    payment = Payment.create(
                        {
                            "id": idempotence_key,
                            "amount": {
                                "value": 150,
                                "currency": "RUB"
                            },
                            "confirmation": {
                                "type": "redirect",
                                "return_url": "https://t.me/forlove2025_bot"
                            },
                            "capture": True,
                            "description": pay_metadata.id,
                            "metadata": {
                                'orderNumber': pay_metadata.id
                            },
                            "receipt": {
                                "customer": {
                                    "full_name": "Николаев Артем Алексеевич",
                                    "email": "cfznyjdf13@mail.ru",
                                    "phone": "79166758299",
                                    "inn": "170108382176"
                                },
                                "items": [
                                    {
                                        "description": "Подписка платформы",
                                        "quantity": "1.00",
                                        "amount": {
                                            "value": 150,
                                            "currency": "RUB"
                                        },
                                        "vat_code": "2",
                                        "payment_mode": "full_payment",
                                        "payment_subject": "commodity",
                                        "country_of_origin_code": "RU",
                                        "product_code": "44 4D 01 00 21 FA 41 00 23 05 41 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 12 00 AB 00",
                                        "customs_declaration_number": "10714040/140917/0090376",
                                        "excise": "20.00",
                                        "supplier": {
                                            "name": "string",
                                            "phone": "string",
                                            "inn": "string"
                                        }
                                    },
                                ]
                            },
                        }, 
                        idempotency_key=idempotence_key
                    )
                    

                    # get confirmation url
                    confirmation_url = payment.confirmation.confirmation_url
                    markup = types.InlineKeyboardMarkup()
                    markup.add(types.InlineKeyboardButton("Оплатить создание афиши", url=confirmation_url))
                    bot.send_message(message.chat.id, '''
Вы оплачиваете 150 руб за создание афиши в едином фирменном стиле игры "За любовь". 
Готовую афишу вышлем Вам в чате ведущих в течение 1 суток после оплаты.

Спасибо , что поддерживаете нас и наш фирменный стиль ❤️''', reply_markup=markup)
                    
                    return
        
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
                    )
            
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
                bot.send_message(message.chat.id, "Подвердите свой номер телефона, нажав кнопку, либо введите другой в формате +7XXXXXXXXXX или 8XXXXXXXXXX", reply_markup=keyboard)
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
            bot.send_message(message.chat.id, "Подвердите свой номер телефона, нажав кнопку, либо введите другой в формате +7XXXXXXXXXX или 8XXXXXXXXXX", reply_markup=keyboard)
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
                bot.send_message(message.chat.id, "Вы зарегистрировались в проекте.\n\nПоздравляем с получением бесплатной подписки на 30 суток.Вам Активирован 1 уровень партнерской программы.\n\nПереходите в наш канал: @za_lyubov_igra")
                handle_start_message(bot, message.chat.id)
    except:
        if message.text.startswith("8") or message.text.startswith("+7"):
            phone_number = message.text
            if len(phone_number) == 12 or len(phone_number) == 11:
                with Session(engine) as session:
                    user = get_user(session, message.chat.id)
                    user.phone = str(phone_number)
                    user.has_ended = True
                    session.commit()
                    bot.send_message(message.chat.id, "Вы зарегистрировались в проекте.\n\nПоздравляем с получением бесплатной подписки на 30 суток.Вам Активирован 1 уровень партнерской программы.\n\nПереходите в наш канал: @za_lyubov_igra")
                    handle_start_message(bot, message.chat.id)
                    return
        bot.send_message(message.chat.id, "Номер телефона не получен")
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        reg_button = types.KeyboardButton(text="Отправить номер телефона", 
        request_contact=True)
        keyboard.add(reg_button)
        bot.send_message(message.chat.id, "Подвердите свой номер телефона, нажав кнопку, либо введите другой в формате +7XXXXXXXXXX или 8XXXXXXXXXX", reply_markup=keyboard)
        bot.register_next_step_handler(message, handle_phone, bot)