import telebot
from telebot import types
import sqlite3

bot = telebot.TeleBot('6554881247:AAE0GVjHxGdwjwmCWeDYkhT_r-EweXhhtgU')

# ВЫПОЛНЕНИЕ КОМАНДЫ
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Привет!')
    chose_table(message)


#Создание шаблона кнопок столов зала
def make_markup_tables():
    markup = types.ReplyKeyboardMarkup()

    btn3 = types.KeyboardButton('3')
    btn4 = types.KeyboardButton('4')
    btn5 = types.KeyboardButton('5')
    btn6 = types.KeyboardButton('6')
    btn7 = types.KeyboardButton('7')
    btn8 = types.KeyboardButton('8')
    markup.row(btn3, btn4, btn5, btn6, btn7, btn8)

    btn2 = types.KeyboardButton('2')
    btn14 = types.KeyboardButton('14')
    btn15 = types.KeyboardButton('15')
    btn16 = types.KeyboardButton('16')
    btn9 = types.KeyboardButton('9')
    markup.row(btn2, btn14, btn15, btn16, btn9)

    btn1 = types.KeyboardButton('1')
    btn13 = types.KeyboardButton('13')
    btn12 = types.KeyboardButton('12')
    btn11 = types.KeyboardButton('11')
    btn10 = types.KeyboardButton('10')
    markup.row(btn1, btn13, btn12, btn11, btn10)

    btn_client_tables = types.KeyboardButton('Мои столы')
    btn_reminder = types.KeyboardButton('Напоминания')
    markup.row(btn_client_tables, btn_reminder)

    return markup
@bot.message_handler(commands=['tables'])
#Выбор стола пользователем
def chose_table(message):
    bot.send_message(message.chat.id, 'Выбери стол', reply_markup=make_markup_tables())
    bot.register_next_step_handler(message, correct_table)
#Обработка выбранной кнопки
def correct_table(message):
    text = message.text

    if text.isdigit() and 0 < int(text) < 17:
        number_of_table = text
        bot.send_message(message.chat.id, f'Вы выбрали стол № {number_of_table}')
        return chose_guest(message, number_of_table)
    elif text == 'Мои столы':
        bot.send_message(message.chat.id, 'Здесь будут написаны твои столы')
        return chose_table(message)
    elif text == 'Напоминания':
        bot.send_message(message.chat.id, 'Здесь будут написаны твои напоминания')
        return chose_table(message)
    else:
        return chose_table(message)

#Создание шаблона кнопок гостей за столом
def make_markup_guests(number_of_table):
    markup = types.ReplyKeyboardMarkup()
    
    btn_pass = types.KeyboardButton('.')
    btn_table = types.KeyboardButton('###')
    btn_tables = types.KeyboardButton('Зал')
    btn_client_tables = types.KeyboardButton('Мои столы')
    btn_reminder = types.KeyboardButton('Напоминания')

    if number_of_table in ['3', '8']:
        btn1 = types.KeyboardButton('1')
        markup.row(btn_pass, btn1, btn_pass, btn_pass)

        btn2 = types.KeyboardButton('2')
        btn3 = types.KeyboardButton('3')
        markup.row(btn2, btn_table, btn3, btn_tables)

        btn4 = types.KeyboardButton('4')
        btn5 = types.KeyboardButton('5')
        markup.row(btn4, btn_table, btn5, btn_client_tables)

        btn6 = types.KeyboardButton('6')
        btn7 = types.KeyboardButton('7')
        markup.row(btn6, btn_table, btn7, btn_reminder)

        btn8 = types.KeyboardButton('8')
        markup.row(btn_pass, btn8, btn_pass, btn_pass)
    elif number_of_table in ['4', '5', '6', '7']:
        btn1 = types.KeyboardButton('1')
        markup.row(btn_pass, btn1, btn_pass, btn_tables)

        btn2 = types.KeyboardButton('2')
        btn3 = types.KeyboardButton('3')
        markup.row(btn2, btn_table, btn3, btn_client_tables)

        btn4 = types.KeyboardButton('4')
        btn5 = types.KeyboardButton('5')
        markup.row(btn4, btn_table, btn5, btn_reminder)

        btn6 = types.KeyboardButton('6')
        markup.row(btn_pass, btn6, btn_pass, btn_pass)
    elif number_of_table in ['1', '2']:
        btn1 = types.KeyboardButton('1')
        markup.row(btn1, btn_pass, btn_tables)

        btn2 = types.KeyboardButton('2')
        markup.row(btn_table, btn2, btn_client_tables)

        btn3 = types.KeyboardButton('3')
        markup.row(btn3, btn_pass, btn_reminder)
    elif number_of_table in ['9', '10']:
        btn1 = types.KeyboardButton('1')
        markup.row(btn_pass, btn1, btn_tables)

        btn2 = types.KeyboardButton('2')
        markup.row(btn2, btn_table, btn_client_tables)

        btn3 = types.KeyboardButton('3')
        markup.row(btn_pass, btn3, btn_reminder)
    elif number_of_table in ['14', '15', '16', '13', '12', '11']:  
        btn2 = types.KeyboardButton('2')
        btn3 = types.KeyboardButton('3')
        markup.row(btn_pass, btn2, btn3, btn_pass, btn_tables)

        btn1 = types.KeyboardButton('1')
        btn4 = types.KeyboardButton('4')
        markup.row(btn1, btn_table, btn_table, btn4, btn_client_tables)

        btn5 = types.KeyboardButton('5')
        btn6 = types.KeyboardButton('6')
        markup.row(btn_pass, btn5, btn6, btn_pass, btn_reminder)
    
    return markup
#Выбор гостя пользователем
def chose_guest(message, number_of_table):
    bot.send_message(message.chat.id, 'Выбери гостя', reply_markup=make_markup_guests(number_of_table))
    bot.register_next_step_handler(message, correct_guest, number_of_table)
#Обработка выбранной кнопки
def correct_guest(message, number_of_table):
    text = message.text

    if text.isdigit():
        number_of_guest = text
        bot.send_message(message.chat.id, f'Вы выбрали гостя № {number_of_guest}')
        return chose_order(message, number_of_table, number_of_guest)
    elif text == 'Зал':
        return chose_table(message)
    elif text == 'Мои столы':
        bot.send_message(message.chat.id, 'Здесь будут написаны твои столы')
        return chose_guest(message, number_of_table)
    elif text == 'Напоминания':
        bot.send_message(message.chat.id, 'Здесь будут написаны твои напоминания')
        return chose_guest(message, number_of_table)
    else:
        return chose_guest(message, number_of_table)

#Создание шаблона кнопок меню
def make_markup_order():
    markup = types.ReplyKeyboardMarkup()

    btn_menu = types.KeyboardButton('Меню')
    btn_menu_for_child = types.KeyboardButton('Детское')
    markup.row(btn_menu, btn_menu_for_child)

    btn_non_alcoholic_drinks = types.KeyboardButton('б/а напитки')
    btn_alcoholic_drinks = types.KeyboardButton('алк напитки')
    markup.row(btn_non_alcoholic_drinks, btn_alcoholic_drinks)

    btn_lunch = types.KeyboardButton('Ланч')
    btn_tickets = types.KeyboardButton('Билеты')
    markup.row(btn_lunch, btn_tickets)

    btn_tables = types.KeyboardButton('Зал')
    btn_client_tables = types.KeyboardButton('Мои столы')
    markup.row(btn_tables, btn_client_tables)

    btn_guests_for_table = types.KeyboardButton('Гости')
    btn_reminder = types.KeyboardButton('Напоминания')
    markup.row(btn_guests_for_table, btn_reminder)

    return markup
#Выбор меню пользователем
def chose_order(message, number_of_table, number_of_guest):
    bot.send_message(message.chat.id, 'Выбери раздел', reply_markup=make_markup_order())
    bot.register_next_step_handler(message, correct_order, number_of_table, number_of_guest)
#Обработка выбранной кнопки
def correct_order(message, number_of_table, number_of_guest):
    text = message.text

    if text == 'Меню':
        return chose_category_menu(message, number_of_table, number_of_guest)
    elif text == 'Детское меню':
        return chose_category_child_menu(message, number_of_table, number_of_guest)
    elif text == 'Зал':
        return chose_table(message)
    elif text == 'Мои столы':
        bot.send_message(message.chat.id, 'Здесь будут написаны твои столы')
        return chose_order(message, number_of_table, number_of_guest)
    elif text == 'Напоминания':
        bot.send_message(message.chat.id, 'Здесь будут написаны твои напоминания')
        return chose_order(message, number_of_table, number_of_guest)
    elif text == 'Гости':
        return chose_guest(message, number_of_table)
    else:
        bot.send_message(message.chat.id, 'Товар не найден')
        return chose_order(message, number_of_table, number_of_guest)

#Создание шаблона кнопок категорий меню
def make_markup_categories():
    markup = types.ReplyKeyboardMarkup()

    btn_breakfast = types.KeyboardButton('Завтраки')
    btn_snacks = types.KeyboardButton('Закуски')
    btn_salads = types.KeyboardButton("Салаты")
    markup.row(btn_breakfast, btn_snacks, btn_salads)

    btn_soups = types.KeyboardButton('Супы')
    btn_main_dish = types.KeyboardButton("Горячее")
    btn_pasta = types.KeyboardButton("Паста")
    markup.row(btn_soups, btn_main_dish, btn_pasta)

    btn_steak = types.KeyboardButton('Стейк')
    btn_pizza = types.KeyboardButton("Пицца")
    btn_desserts = types.KeyboardButton("Десерты")
    markup.row(btn_steak, btn_pizza, btn_desserts)

    btn_tables = types.KeyboardButton('Зал')
    btn_client_tables = types.KeyboardButton('Мои столы')
    markup.row(btn_tables, btn_client_tables)

    btn_guests_for_table = types.KeyboardButton('Гости')
    btn_reminder = types.KeyboardButton('Напоминания')
    markup.row(btn_guests_for_table, btn_reminder)

    return markup
#Выбор категории меню пользователем
def chose_category_menu(message, number_of_table, number_of_guest):
    bot.send_message(message.chat.id, 'Выбери категорию', reply_markup=make_markup_categories())
    bot.register_next_step_handler(message, correct_category_menu, number_of_table, number_of_guest)
#Обработка выбранной кнопки
def correct_category_menu(message, number_of_table, number_of_guest):
    text = message.text

    if text in ["Завтраки", "Закуски", "Салаты", "Супы", "Горячее", "Паста", "Стейк", "Десерты", "Пицца"]:
        return chose_goods( message, number_of_table, number_of_guest, str('основное ' + text).lower() )
    elif text == 'Зал':
        return chose_table(message)
    elif text == 'Мои столы':
        bot.send_message(message.chat.id, 'Здесь будут написаны твои столы')
        return chose_order(message, number_of_table, number_of_guest)
    elif text == 'Напоминания':
        bot.send_message(message.chat.id, 'Здесь будут написаны твои напоминания')
        return chose_order(message, number_of_table, number_of_guest)
    elif text == 'Гости':
        return chose_guest(message, number_of_table)
    else:
        bot.send_message(message.chat.id, 'Товар не найден')
        return chose_order(message, number_of_table, number_of_guest)


#Созданиие шаблона товаров выбранной категории
def make_markup_goods(categories, number_of_guest):
    markup = types.ReplyKeyboardMarkup()

    conn = sqlite3.connect('DNK.db')
    cur = conn.cursor()

    cur.execute(f"SELECT name from goods where category = '{categories}'")
    goods = cur.fetchall()

    cur.close()
    conn.close()

    btns = [[]]
    for good in goods:
        if len(btns[-1]) == 2:
            btns.append([])    
        btns[-1].append( types.KeyboardButton( good[0] ) )

    for row in btns:
        markup.row( *row )

    btn_tables = types.KeyboardButton('Зал')
    btn_client_tables = types.KeyboardButton('Мои столы')
    markup.row(btn_tables, btn_client_tables)

    btn_guests_for_table = types.KeyboardButton('Гости')
    btn_chosen_guest = types.KeyboardButton(f'Гость {number_of_guest}')
    markup.row(btn_guests_for_table, btn_chosen_guest)

    return markup
#Выбор блюд выбранной категории
def chose_goods(message, number_of_table, number_of_guest, categories):
    bot.send_message(message.chat.id, 'Выбери товар', reply_markup=make_markup_goods(categories, number_of_guest))
    bot.register_next_step_handler(message, correct_goods, number_of_table, number_of_guest, categories)
#Обработка выбранной кнопки
def correct_goods(message, number_of_table, number_of_guest, categories):
    text = message.text

    if text == 'Зал':
        return chose_table(message)
    elif text == 'Мои столы':
        bot.send_message(message.chat.id, 'Здесь будут написаны твои столы')
        return chose_order(message, number_of_table, number_of_guest)
    elif text == f'Гость {number_of_guest}':
        return chose_order(message, number_of_table, number_of_guest)
    elif text == 'Гости':
        return chose_guest(message, number_of_table)
    else:
        conn = sqlite3.connect('DNK.db')
        cur = conn.cursor()

        cur.execute(f"SELECT * from goods where name = '{text}'")
        goods = cur.fetchall()

        cur.close()
        conn.close()
        
        if goods:
            bot.send_message(message.chat.id, 'Товар найден')
            return chose_goods(message, number_of_table, number_of_guest, categories)
        else:
            bot.send_message(message.chat.id, f'Товар не найден')
            return chose_order(message, number_of_table, number_of_guest)

#ПОЛУЧЕНИЕ ФОТО
@bot.message_handler(content_types=['photo'])
def set_photo(message):
    bot.send_message(message.chat.id, 'Фото установлено!')

#СООБЩЕНИЕ С КНОПКАМИ
@bot.message_handler(commands=['list_of_dishes'])
def func(message):
    bot.send_message(message.chat.id, 'СПИСОК БЛЮД:')
    bot.send_message(message.chat.id, 'блюдо1', reply_markup=make_buttons())

#КНОПКИ
def make_buttons():
    markup = types.InlineKeyboardMarkup()

    #Создание каждой кнопки в новом ряду
    #markup.add(types.InlineKeyboardButton('1', callback_data='1'))
    #markup.add(types.InlineKeyboardButton('2', callback_data='2'))
    #markup.add(types.InlineKeyboardButton('3', callback_data='3'))

    #Создание ряда

    btn1 = types.InlineKeyboardButton('состав', callback_data='compound')
    markup.row(btn1)

    btn2 = types.InlineKeyboardButton('комментарий', callback_data='comment')
    btn3 = types.InlineKeyboardButton('удалить', callback_data='delete')
    markup.row(btn2, btn3)

    return markup


#СОЗДАНИИЕ ФУНКЦИИ ДЛЯ КНОПОК
@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
    if callback.data == 'delete': #УДАЛИТЬ СООБЩЕНИЕ С КНОПКАМИ
        bot.delete_message(callback.message.chat.id, callback.message.message_id)
    elif callback.data == 'comment': #ОСТАВИТЬ КОММЕНТАРИЙ К БЛЮДУ
        bot.edit_message_text(callback.message.text + '\nСкоро здесь можно будет оставлять комментарий', callback.message.chat.id, callback.message.message_id, reply_markup=make_buttons())
    elif callback.data == 'compound': #ВЫВЕСТИ СОСТАВ БЛЮДА
        bot.send_message(callback.message.chat.id, 'состав')


bot.polling(non_stop=True)