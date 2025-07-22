from sqlalchemy import select, and_
from telebot import TeleBot, types
from sqlalchemy.orm import Session
from yoomoney import Authorize, Client, Quickpay
from db.connect import engine
from db.models import City, PayMetadata, Schedule, User
from datetime import datetime
from handlers.handler import ref_handler


ADMIN_ACCOUNT = 6062822304


def handler_callback(bot: TeleBot, call: types.CallbackQuery):
    with Session(engine) as session:
        user = session.execute(select(User).where(User.tg_id == call.from_user.id)).scalar() # call.from_user.id
        
        if call.data == "about_project":
            bot.send_message(call.from_user.id, """        
Проект 'За любовь' — это уникальная экосистема, созданная для тех, кто хочет строить крепкие и осознанные отношения, развиваться как личность и быть частью большого сообщества единомышленников. Мы верим, что любовь, уважение и верность — это основа счастливой жизни. Наши инструменты — это увлекательные настольные игры, образовательные курсы, оффлайн-клубы знакомств, фестивали и партнерская программа, которая позволяет зарабатывать, делясь нашими ценностями. Узнайте больше о том, как мы помогаем людям находить гармонию и вдохновение!

Присоединяйтесь к движению, которое меняет жизни к лучшему!
    """)
            f = open('assets/Презентация о проекте.pdf', 'rb')
            bot.send_document(call.from_user.id, f)
        elif call.data == 'media_channels':
            markup = types.InlineKeyboardMarkup()
            button = types.InlineKeyboardButton("Telegram канал", url="https://t.me/za_lyubov_igra")
            markup.add(button)
            bot.send_message(call.from_user.id, """        
Будьте в курсе всех новостей и событий проекта 'За любовь'! 

Подписывайтесь на наши социальные сети, чтобы следить за анонсами мероприятий, вдохновляющими историями участников и полезными материалами. 
Мы делимся видео, статьями и отзывами, чтобы вы чувствовали себя частью нашего сообщества!
    """, reply_markup=markup)
        
        # ГОРОДА
        elif call.data == "sign_for_game":
            markup = types.InlineKeyboardMarkup()
            button1 = types.InlineKeyboardButton("Об игре",callback_data="about_game")
            button2 = types.InlineKeyboardButton("Наши города",callback_data="our_cities") 
            markup.add(button1, button2, row_width=1)
            bot.send_message(call.from_user.id, "Настольная игра 'За любовь' — это не просто развлечение, а уникальный способ познакомиться с новыми людьми, укрепить связи и обсудить важные жизненные темы в легкой и непринужденной атмосфере.\n\nИгра подходит для всех — от друзей до семейных пар. Запишитесь на ближайшее мероприятие в вашем городе и откройте для себя мир осознанного общения!", reply_markup=markup)
        elif call.data == "about_game":
            bot.send_message(call.from_user.id, """
Игра 'За любовь' создана для 1–12 участников и подходит для людей любого возраста, которые хотят лучше понять себя и других. 

В комплект входят карточки с глубокими вопросами, заданиями и сценариями, которые помогают раскрыться, обсудить ценности и выстроить доверие. 
Это идеальный способ начать свое путешествие в экосистеме 'За любовь'. Узнайте, как игра может изменить ваш взгляд на отношения!""")
        elif call.data == "our_cities":
            cities = session.execute(select(City)).scalars().all()
            markup = types.InlineKeyboardMarkup()
            for city in cities:
                button = types.InlineKeyboardButton(city.name, callback_data=f"city_{city.id}")
                markup.add(button)
            bot.send_message(call.from_user.id, "Мы уже работаем в 12 городах России, и наша сеть растет!\n\nВыберите свой город, чтобы узнать о ближайших играх, познакомиться с организатором и присоединиться к местному сообществу 'За любовь'", reply_markup=markup)
        elif call.data.startswith("city_"):
            city_id = int(call.data.split("_")[1])
            city = session.execute(select(City).where(City.id == city_id)).scalar()
            markup = types.InlineKeyboardMarkup()
            button = types.InlineKeyboardButton("Ссылка на Telegram представителя", url=city.agent_account)
            button2 = types.InlineKeyboardButton("Ссылка на Telegram-канал", url=city.channel_link)
            markup.add(button,button2, row_width=1)
            bot.send_message(call.from_user.id, f"""
В городе {city.name} игры 'За любовь' проводит наш представитель, который с радостью поможет вам погрузиться в мир осознанных отношений. Свяжитесь с ним или подпишитесь на Telegram-канал города {city.name}, чтобы быть в курсе всех событий!

Для более подробной информации напишите основателю проекта: @Forlove2025
                             """)
        
        # ПОДПИСКА
        elif call.data == "subscribe":
            markup = types.InlineKeyboardMarkup()
            button = types.InlineKeyboardButton("На месяц за 333 ₽", callback_data=f"buy-subscribe_1_333")
            button2 = types.InlineKeyboardButton("На год за 3333 ₽", callback_data=f"buy-subscribe_12_3333")
            markup.add(button,button2, row_width=1)
            bot.send_message(call.from_user.id, """
Подписка 'За любовь' — это ваш ключ к полной экосистеме проекта! За 333 руб./мес. (первый месяц бесплатно) вы получаете доступ к эксклюзивным образовательным курсам по психологии отношений, эмоциональному интеллекту и личностному росту, а также к маркетплейсу, партнерской программе и закрытым мероприятиям. Это ваш шанс учиться, общаться и зарабатывать в одном месте. Также вы сможете начать зарабатывать по партнерской программе.

Оформите подписку и начните свое путешествие к гармонии""", reply_markup=markup)
        elif call.data.startswith("buy-subscribe"):
            # реализовать создание платежа
            pay_link = 'https://example.com'
            months = call.data.split("_")[1]
            price = call.data.split("_")[2]
            
            pay_metadata = PayMetadata(
            user_id = user.id, 
                price = price,
                product = f"subscribe-{months}",
                procent_balance = 50,
                inner_balance = 0
            )
            
            session.add(pay_metadata)
            session.commit()
            
            quickpay = Quickpay(
                receiver="4100119236552041",
                quickpay_form="shop",
                targets="Sponsor this project",
                paymentType="SB",
                sum=int(price),
                label=pay_metadata.id
            )
            
            markup = types.InlineKeyboardMarkup()
            button = types.InlineKeyboardButton(f"Оплатить ({price} ₽)", url=quickpay.redirected_url)
            #button2 = types.InlineKeyboardButton(f"Проверить оплату", callback_data=f"check-buy-subscribe_{pay_metadata.id}")
            markup.add(button, row_width=1)
            
            
            bot.send_message(call.from_user.id, f"""
После оплаты ОБЯЗАТЕЛЬНО нажмите кнопку "Проверить оплату", иначе ваша покупка не зафиксируется                    
                             """, reply_markup=markup)
        elif call.data.startswith("check-buy-subscribe"):
            pay_metadata_id = int(call.data.split('_')[1])
            client = Client("4100119236552041.62F531CC6CF1B5DBC00C5D38439C9ADF529D86C6E59F50507F0BCCF28A08A81561341999C0A80BA151B9EDA7D1BC45B6A60F4F2288D7315C2E42ABD29953788F11DB5746B31547AD6B2AE7A9DDAEBD835994DC7827D7403FC3E43E6252E78C7FFF1D03B3026251118E1DEB4E3ACC0427DF9F8AC976A380DA9CF640518CFC5D3D")
            history = client.operation_history(label=pay_metadata_id)
            if len(history.operations) > 0 and history.operations[0].status == "success":
                payed = True
            else: payed = False
            
            if payed:
                pay_metadata = session.execute(select(PayMetadata).where(PayMetadata.id == pay_metadata_id)).scalar()
                if pay_metadata.has_payed == True:
                    bot.send_message(call.from_user.id, "Оплата уже проверена")
                pay_metadata.has_payed = True
                ref_handler(session, user, pay_metadata)
                bot.send_message(call.from_user.id, "Для получения дальнейших инструкций обратитесь к @Forlove2025")
                bot.send_message(ADMIN_ACCOUNT, f"""
Пользователь @{user.username} купил подписку {"на месяц"if pay_metadata.price == 333 else "на год"}
                                 """)
            else:
                bot.answer_callback_query(call.id, text='Оплата не прошла. Проверьте и повторите попытку', show_alert=True)
        elif call.data == "_subscribe-send_forlove":
            bot.send_message(call.from_user.id, "Для получения реквизитов напишите основателю проекта: @Forlove2025")
        #ПРОДУКТЫ
        elif call.data == "our_products":
            markup = types.InlineKeyboardMarkup()
            button = types.InlineKeyboardButton("Ведущий игры за 55555 ₽", callback_data=f"buy-product_game_55555")
            
            #button = types.InlineKeyboardButton("Владелец сертификата за 15 555 ₽", callback_data=f"buy-product_game_55555")
            #button = types.InlineKeyboardButton("Управление городом за 15 555 ₽", callback_data=f"buy-product_game_55555")
            #button = types.InlineKeyboardButton("Организатор туров за 15 555 ₽", callback_data=f"buy-product_game_55555")
            #button = types.InlineKeyboardButton("Производитель/поставщик за 15 555 ₽", callback_data=f"buy-product_game_55555")
            
            button2 = types.InlineKeyboardButton("Организатор Клуба знакомств за 79999 ₽", callback_data=f"buy-product_clubtraining_79999")
            
            markup.add(button,button2, row_width=1)
            
            if user.ref_level == 1: 
                button3 = types.InlineKeyboardButton("Пакет за 5000 ₽", callback_data=f"buy-product_package_5000")
                markup.add(button3)
            if user.ref_level > 1:
                if user.ref_level <= 2: 
                    button4 = types.InlineKeyboardButton("Пакет за 15000 ₽", callback_data=f"buy-product_package_15000")
                    markup.add(button4)
                if user.ref_level <= 3:
                    button5 = types.InlineKeyboardButton("Пакет за 25000 ₽", callback_data=f"buy-product_package_25000")
                    markup.add(button5)
                if user.ref_level <= 4:
                    button6 = types.InlineKeyboardButton("Пакет за 45000 ₽", callback_data=f"buy-product_package_45000")
                    markup.add(button6)
                if user.ref_level <= 5: 
                    button7 = types.InlineKeyboardButton("Пакет за 100000 ₽", callback_data=f"buy-product_package_100000")
                    markup.add(button7)
            #сначала только 5к, затем все пакеты должны быть открыты

            
            bot.send_message(call.from_user.id, """
Хотите зарабатывать, делясь ценностями 'За любовь'?
Наша бизнес-модель открывает множество возможностей: от проведения игр до управления городом или создания контента. 

Выберите роль, которая вам ближе, и начните свой путь к финансовой свободе и вдохновению. Мы поддержим вас на каждом шагу: предоставим обучение, маркетинговые материалы и доступ к нашей экосистеме!    
""",reply_markup=markup)
        elif call.data.startswith("buy-product"):
            name = call.data.split("_")[1]
            price = call.data.split("_")[2]
            pay_link = 'https://example.com'
            
            pay_metadata = PayMetadata(
                user_id = user.id,
                price = price,
                product = name,
                procent_balance = 25,
                inner_balance = 25
            )
            
            session.add(pay_metadata)
            session.commit()
            
            quickpay = Quickpay(
                receiver="4100119236552041",
                quickpay_form="shop",
                targets="Sponsor this project",
                paymentType="SB",
                sum=int(price),
                label=pay_metadata.id
            )
            
            markup = types.InlineKeyboardMarkup()    
            button = types.InlineKeyboardButton(f"Оплатить ({price} ₽)", url=quickpay.redirected_url)
            #button2 = types.InlineKeyboardButton(f"Проверить оплату", callback_data=f"check-buy-product_{pay_metadata.id}")
            markup.add(button, row_width=1)
            
            
            
            text = ""
            if name == "game":
                image_url = "https://iimg.su/s/17/WjbY8Fs5oXFRxx3LDZV9yUSzQjtvA2BCBQWwMad1.png"
                text = """
КОМПЛЕКТ ВЕДУЩЕГО ИГР

Мы присылаем вам комплект настольной игры, с ним вы сможете проводить игры в своем городе и зарабатывать на этом. Инструкции и базовое обучение также прилагается.
Вы будете получать доход от проведения игр и бонусы по партнерской программе.
Стоимость: 55.555 руб.
Прогназируемая окупаемость: 1-2 месяца.
                """
            elif name == "clubtraining":
                image_url = "https://iimg.su/s/17/tAG14iNFiiiGpLTVv4o9Ip07onLPoN3IQ6wMrinK.png"
                text = """
ОБУЧАЮЩИЙ КУРС "РУКОВОДИТЕЛЬ ГОРОДСКОГО КЛУБА ЗНАКОМСТВ"

Мы присылаем вам комплект настольной игры, с ним вы сможете проводить игры в своем городе и зарабатывать на этом. Инструкции и базовое обучение прилагается.
Также вы сможете организовывать мероприятия, туры, фестивали от нашей компании.
Вы будете получать доход от проведения игр и других мероприятий, и бонусы по партнерской программе.
Стоимость: 79.999 руб.
Прогназируемая окупаемость: 1-2 месяца.                
"""
            elif name == "package":
                text = """
Возможность расширить заработок с реферальной программы
"""
                image_url = None
            if image_url:
                bot.send_photo(call.from_user.id, image_url, text, reply_markup=markup)
            else:
                bot.send_message(call.from_user.id, text, reply_markup=markup)
        elif call.data == "_buy-product_forlove":
            bot.send_message(call.from_user.id, "Для получения реквизитов напишите основателю проекта: @Forlove2025")
        elif call.data.startswith("check-buy-product"):
            pay_metadata_id = int(call.data.split('_')[1])
            client = Client("4100119236552041.62F531CC6CF1B5DBC00C5D38439C9ADF529D86C6E59F50507F0BCCF28A08A81561341999C0A80BA151B9EDA7D1BC45B6A60F4F2288D7315C2E42ABD29953788F11DB5746B31547AD6B2AE7A9DDAEBD835994DC7827D7403FC3E43E6252E78C7FFF1D03B3026251118E1DEB4E3ACC0427DF9F8AC976A380DA9CF640518CFC5D3D")
            history = client.operation_history(label=pay_metadata_id)
            if len(history.operations) > 0 and history.operations[0].status == "success":
                payed = True
            else: payed = False
            
            if payed:
                pay_metadata = session.execute(select(PayMetadata).where(PayMetadata.id == int(call.data.split('_')[1]))).scalar()
                if pay_metadata.has_payed == True:
                    bot.send_message(call.from_user.id, "Оплата уже проверена")
                pay_metadata.has_payed = True
                if pay_metadata.product == "package":
                    if pay_metadata.price == 5000: user.ref_level = 2
                    if pay_metadata.price == 15000: user.ref_level = 3
                    if pay_metadata.price == 25000: user.ref_level = 4
                    if pay_metadata.price == 45000: user.ref_level = 5
                    if pay_metadata.price == 100000: user.ref_level = 6
                ref_handler(session, user, pay_metadata)
                bot.send_message(ADMIN_ACCOUNT, f"""
Пользователь @{user.username} купил продукт на {pay_metadata} рублей
                                 """)
                if pay_metadata.product != "package":
                    bot.send_message(call.from_user.id, "Для получения дальнейших инструкций обратитесь к @Forlove2025")
                else:
                    bot.send_message(call.from_user.id, "Увеличен заработок с реферальной программы")
            else:
                bot.answer_callback_query(call.id, text='Оплата не прошла. Проверьте и повторите попытку', show_alert=True)
            
        #МЕРОПРИЯТИЯ
        elif call.data == "our_events":
            markup = types.InlineKeyboardMarkup()    
            button = types.InlineKeyboardButton("Форматы мероприятий", callback_data="event_formats")
            button2 = types.InlineKeyboardButton("Расписание", callback_data="event_table")
            button3 = types.InlineKeyboardButton("Стать гидом", callback_data="become_guide")
            markup.add(button, button2, button3, row_width=1)
            
            bot.send_message(call.from_user.id, """
Проект 'За любовь' — это не только игры, но и яркие оффлайн-мероприятия: фестивали знакомств, туры, конкурсы красоты и вдохновляющие встречи. 

Каждое событие создано, чтобы объединять людей, помогать находить друзей, партнеров или единомышленников. 
Узнайте больше о наших форматах, посмотрите расписание или станьте гидом, чтобы организовывать события в своем городе!
                             """, reply_markup=markup)
        
        elif call.data == "event_formats":
            markup = types.InlineKeyboardMarkup()    
            button = types.InlineKeyboardButton("Туры", callback_data="event_forlove")
            button2 = types.InlineKeyboardButton("Фестивали", callback_data="event_forlove")
            button3 = types.InlineKeyboardButton("Конкурсы красоты", callback_data="event_forlove")
            button4 = types.InlineKeyboardButton("Ретриты", callback_data="event_forlove")
            button5 = types.InlineKeyboardButton("Региональные встречи", callback_data="event_forlove")
            markup.add(button, button2, button3, button4, button5, row_width=2)
            
            bot.send_message(call.from_user.id, """
Мы проводим разные форматы мероприятий, чтобы каждый нашел что-то для себя. 
Выберите, что вас вдохновляет: фестивали, туры, конкурсы или мастер-классы.
Для более подробной информации напишите основателю проекта: @Forlove2025
                             """, reply_markup=markup)
        elif call.data == "_event_tour":
            bot.send_message(call.from_user.id, """Инфа про Тур""")
        elif call.data == "event_forlove":
            bot.send_message(call.from_user.id, """Для более подробной информации напишите основателю проекта: @Forlove2025""")
        elif call.data == "_event_festival":
            bot.send_message(call.from_user.id, """Инфа про Фестиваль""")
        elif call.data == "_event_conferences":
            bot.send_message(call.from_user.id, """Инфа про Конференции""")
        
        elif call.data == "event_table":
            today = datetime.now().strftime("%d.%m")
            
            stmt = select(Schedule).where(Schedule.start >= today) # поправить баг с отображением расписания
            results = session.execute(stmt)
            schedules = results.scalars().all()
            markup = types.InlineKeyboardMarkup()    
            for schedule in schedules: 
                button = types.InlineKeyboardButton(f"{schedule.name}, {schedule.city}, {schedule.start}", callback_data=f"event_table_inner-{schedule.id}")
                markup.add(button, row_width=1)
            addiction_text = ""
            if len(schedules) == 0: addiction_text = "Расписание появится скоро"
            bot.send_message(call.from_user.id, f"""
Ознакомьтесь с расписанием наших мероприятий и выберите то, что вам интересно! От фестивалей до локальных встреч — у нас всегда есть что-то особенное.

{addiction_text}
                             """, reply_markup=markup)
        elif call.data.startswith("event_table_inner"):
            schedule_id = int(call.data.split("-")[1])
            schedule = session.execute(select(Schedule).where(Schedule.id == schedule_id)).scalar()
            
            pay_link = "https://example.com"
            
            markup = types.InlineKeyboardMarkup()
            button = types.InlineKeyboardButton("Купить сертификат", callback_data="inner_event_table_text")
            markup.add(button)
            
            bot.send_message(call.from_user.id, f"""
Информация:
{schedule.name}, {schedule.city}, {schedule.start}
""", reply_markup=markup)
        elif call.data == "inner_event_table_text":
            bot.send_message(call.from_user.id, f"Для получения реквизитов и дальнейших инструкций обратитесь к @Forlove2025")
        
        elif call.data == "become_guide":
            markup = types.InlineKeyboardMarkup()
            button = types.InlineKeyboardButton("Оставить заявку", callback_data="become_guide_stay")
            markup.add(button)
            bot.send_message(call.from_user.id, f"""
Мечтаете организовывать туры и мероприятия 'За любовь' в вашем городе? 

Станьте гидом и вдохновляйте людей на новые знакомства и развитие! Мы предоставим вам обучение, материалы и поддержку, чтобы вы могли создавать незабываемые события. Узнайте, как начать, и подайте заявку!
Для более подробной информации напишите основателю проекта: @Forlove2025
""", reply_markup=markup)
        
        elif call.data == "become_guide_stay":
            bot.send_message(call.from_user.id, f"Ваша заявка отправлена")
            bot.send_message(ADMIN_ACCOUNT, f"Заявка от @{user.username} на 'Гида'")
        
        # РЕФЕРАЛЬНАЯ СИСТЕМА
        elif call.data == "ref_program":
            markup = types.InlineKeyboardMarkup()
            button = types.InlineKeyboardButton("Моя структура", callback_data="ref_structure")
            button2 = types.InlineKeyboardButton("Конвертация бонусов", callback_data="return_balance")
            markup.add(button, button2, row_width=1)
            
            bot.send_message(call.from_user.id, f"""
Зарабатывайте, приглашая друзей в проект 'За любовь'! Наша реферальная программа позволяет вам получать доход от подписок, игр и со всех других продуктов, которыми делятся ваши приглашенные. Чем больше ваша команда, тем выше ваш заработок — до 20 уровней партнерской сети. Получите свою уникальную ссылку, следите за балансом и стройте свою структуру уже сегодня!

Реферальная ссылка:
<code>https://t.me/forlove2025_bot?start={call.from_user.id}</code>

Бонусный баланс:
{user.balance} ₽

Накопительный баланс:
{user.inner_balance} ₽
                             """, reply_markup=markup, parse_mode="html")
        elif call.data == "ref_structure":
            ref_users = session.execute(select(User).where(User.ref == user.tg_id)).scalars().all() # реферальная структура
            nicks = """"""
            for ref in ref_users:
                nicks += f"@{ref.username}\n"
            bot.send_message(call.from_user.id, f"""
Посмотрите, как растет ваша команда! Здесь вы можете увидеть участников вашей первой линии и скачать полную структуру, чтобы отслеживать свой прогресс. Создавайте сообщество единомышленников и зарабатывайте вместе!

Ваша 1-я линия:
{nicks}   
                             """)
        elif call.data == "return_balance":
            bot.send_message(call.from_user.id, "Для более подробной информации напишите основателю проекта: @Forlove2025")

        # ПОДДЕРЖКА
        elif call.data == "support":
            markup = types.InlineKeyboardMarkup()
            button = types.InlineKeyboardButton("Отправить сообщение в поддержку", callback_data="support_message")
            markup.add(button)
            bot.send_message(call.from_user.id, "У вас есть вопросы или нужна помощь? Мы всегда рядом!\n\nНапишите нам, расскажите о вашей ситуации или задайте вопрос, и наша команда поддержки ответит в кратчайшие сроки. Если хотите, прикрепите фото, чтобы мы лучше поняли ваш запрос. Давайте сделаем ваш опыт с 'За любовь' незабываемым!", reply_markup=markup)
        elif call.data == "support_message":
            bot.send_message(call.from_user.id, "Отправьте сообщение в поддержку")
            bot.register_next_step_handler(call.message, support_message, bot)
            
    bot.answer_callback_query(call.id)  # Теперь у вас открылись все возможности нашей платформы      
    
def support_message(message: types.Message, bot: TeleBot):
    bot.send_message(message.chat.id, "Сообщение отправлено в поддержку")
    bot.send_message(ADMIN_ACCOUNT, f"""
Пользователь @{message.from_user.username} отправил сообщение в поддержку:

{message.text}
                     """)