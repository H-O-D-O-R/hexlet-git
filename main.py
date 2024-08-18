import telebot
from telebot import types
import sqlite3
import json

bot = telebot.TeleBot('6554881247:AAE0GVjHxGdwjwmCWeDYkhT_r-EweXhhtgU')

# ВЫПОЛНЕНИЕ КОМАНДЫ
@bot.message_handler(commands=['start'])
def start(message):
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
        # bot.send_message(message.chat.id, f'Вы выбрали гостя № {number_of_guest}')
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

#ДОБАВИТЬ ТОВАР В ЗАКАЗ
def add_good_to_order(message, number_of_table, number_of_guest, good, variant=''):
    conn = sqlite3.connect('DNK.db')
    cur = conn.cursor()

    cur.execute(f"SELECT * from waiters where id_chat = '{message.chat.id}'")
    waiter = cur.fetchall()[0]

    if not waiter[4]:
        data = {'order': {}}
    else:
        data = json.loads( waiter[4] )
    
    data['order'][number_of_table] = data['order'].get(number_of_table, {})
    data['order'][number_of_table][number_of_guest] = data['order'][number_of_table].get(number_of_guest, {})

    data_of_guest = data['order'][number_of_table][number_of_guest]
    if variant:
        data_of_guest[good[1] + '_' + variant] = data_of_guest.get(good[1] + '_' + variant, {'quantity': 0, 'comment': variant})
        data_of_guest[good[1] + '_' + variant]['quantity'] += 1
    else:
        data_of_guest[good[1]] = data_of_guest.get(good[1], {'quantity': 0, 'comment': variant})
        data_of_guest[good[1]]['quantity'] += 1
     
    data = json.dumps(data, ensure_ascii=False)

    cur.execute(f'''UPDATE waiters SET json_draft = '{data}' where id_chat = '{message.chat.id}' ''')
    conn.commit()

    cur.close()
    conn.close()

    display_order(message, number_of_table, number_of_guest)

#Вывод заказа стола
def display_order(message, number_of_table, number_of_guest):
    bot.send_message(message.chat.id, f" {'-' * 60}\n{' ' * 25}СТОЛ {number_of_table}\n{'-'*60}")

    conn = sqlite3.connect('DNK.db')
    cur = conn.cursor()
    
    cur.execute(f"SELECT json_draft from waiters where id_chat = '{message.chat.id}'")
    data = json.loads(cur.fetchall()[0][0])
    new_data_of_guests = data['order'][number_of_table]

    cur.execute(f"SELECT json_detailed_order from moving_of_tables where active = '1' and number_of_table = '{number_of_table}'")
    last_data_of_guests = cur.fetchall()

    if last_data_of_guests:
        last_data_of_guests = json.loads(last_data_of_guests[0], ensure_ascii=False)
    else:
        last_data_of_guests = {}

    guests = sorted( set( list(last_data_of_guests.keys()) + list(new_data_of_guests.keys()) ) - {number_of_guest}) + [number_of_guest]

    for guest in guests:
        if not last_data_of_guests.get(guest, False) and not new_data_of_guests.get(guest, False):
            continue

        bot.send_message(message.chat.id, f'{"-" * 60}\n{" " * 25}ГОСТЬ {guest}\n{"-" * 60}')

        markup = make_buttons_for_good(False, number_of_table, guest)
        for name, value in last_data_of_guests.get(guest, {}).items():
            bot.send_message(message.chat.id, f"{name.split('_')[0]}, {value['quantity']} шт\n{value['comment']}", reply_markup=markup)
        
        markup = make_buttons_for_good(True, number_of_table, guest)
        for name, value in new_data_of_guests.get(guest, {}).items():
            bot.send_message(message.chat.id, f"🔄 {name.split('_')[0]}, {value['quantity']} шт\n{value['comment']}", reply_markup=markup)
        
    cur.close()
    conn.close()

#Создание шаблона кнопок для товаров заказа
def make_buttons_for_good(is_draft, number_of_table, guest):
    markup = types.InlineKeyboardMarkup()

    btn_add = types.InlineKeyboardButton('➕', callback_data=f"a_{number_of_table}_{guest}")    
    btn_reduce = types.InlineKeyboardButton('➖', callback_data=f'r_{number_of_table}_{guest}')
    btn_delete = types.InlineKeyboardButton('🗑', callback_data=f'd_{number_of_table}_{guest}')
    btn_comment = types.InlineKeyboardButton('✏️', callback_data=f'cm_{number_of_table}_{guest}')
    btn_compound = types.InlineKeyboardButton('📕', callback_data=f'c_{number_of_table}_{guest}')
    btn_taken = types.InlineKeyboardButton('✅', callback_data=f't_{number_of_table}_{guest}')

    if is_draft:
        btns = [btn_add, btn_reduce, btn_delete, btn_comment, btn_compound]
    else:
        btns = [btn_add, btn_compound, btn_taken]

    markup.row(*btns)

    return markup

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
        good = cur.fetchall()

        cur.close()
        conn.close()
        
        if good:
            good = good[0]
            # bot.send_message(message.chat.id, f'Товар найден\n{good}')
            if int(good[7]):
                return chose_variative_good(message, number_of_table, number_of_guest, good)
            else:
                add_good_to_order(message, number_of_table, number_of_guest, good) 
                return chose_goods(message, number_of_table, number_of_guest, categories)
        else:
            # bot.send_message(message.chat.id, f'Товар не найден')
            return chose_order(message, number_of_table, number_of_guest)

#Создание шаблона вариативных товаров
def make_markup_variative_goods(good):
    markup = types.ReplyKeyboardMarkup()

    btns = [[]]
    for variant in good[8].split(', '):
        if len(btns[-1]) == 2:
            btns.append([])
        btns[-1].append( types.KeyboardButton(variant) )
    
    for row in btns:
        markup.row( *row )
    
    markup.row( 'Назад' )

    return markup         
#Выбор вариативных блюд
def chose_variative_good(message, number_of_table, number_of_guest, good):
    bot.send_message(message.chat.id, 'Выбери вариацию', reply_markup=make_markup_variative_goods(good))
    bot.register_next_step_handler(message, correct_variative_good, number_of_table, number_of_guest, good)
#Обработка выбранной кнопки
def correct_variative_good(message, number_of_table, number_of_guest, good):
    text = message.text

    if text in good[8].split(', '):
        add_good_to_order(message, number_of_table, number_of_guest, good, text)
    # elif text != 'Назад':
    #     pass
    #     bot.send_message(message.chat.id, 'вариация не найдена')
    
    return chose_goods(message, number_of_table, number_of_guest, good[2])


#ПОЛУЧЕНИЕ ФОТО
# @bot.message_handler(content_types=['photo'])
# def set_photo(message):
#     bot.send_message(message.chat.id, 'Фото установлено!')

#СОЗДАНИИЕ ФУНКЦИИ ДЛЯ КНОПОК
@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
    name = callback.message.text.split(',')[0]

    is_draft = False
    if name.startswith('🔄'):
        is_draft = True
        name = name[2:]

    command, table, guest = callback.data.split('_')

    if command == 'a': #ДОБАВИТЬ ЕДИНИЦУ ТОВАРА
        conn = sqlite3.connect('DNK.db')
        cur = conn.cursor()

        cur.execute(f''' SELECT is_varitive FROM goods WHERE name = '{name}' ''')
        is_varitive = cur.fetchall()[0][0]
                
        if is_varitive:
            name = name + '_' + callback.message.text.split('\n')[1]
        
        cur.execute(f''' SELECT json_draft FROM waiters where id_chat = {callback.message.chat.id} ''')
        draft = json.loads(cur.fetchall()[0][0])

        draft['order'][table][guest][name]['quantity'] += 1

        bot.edit_message_text(f"{'🔄 ' if is_draft else ''}{name.split('_')[0]}, {draft['order'][table][guest][name]['quantity']} шт\n{draft['order'][table][guest][name]['comment']}", 
                                callback.message.chat.id, callback.message.message_id, 
                                reply_markup=make_buttons_for_good(True, table, guest))

        cur.execute(f''' UPDATE waiters SET json_draft = '{json.dumps(draft, ensure_ascii=False)}' WHERE id_chat = '{callback.message.chat.id}' ''')
        conn.commit()

        cur.close()
        conn.close()

        # chose_category_menu(callback.message, table, guest)

    elif command == 'r': #УБРАТЬ ЕДИНИЦУ ТОВАРА
        conn = sqlite3.connect('DNK.db')
        cur = conn.cursor()

        cur.execute(f''' SELECT json_draft FROM waiters where id_chat = {callback.message.chat.id} ''')
        draft = json.loads(cur.fetchall()[0][0])

        cur.execute(f''' SELECT is_varitive FROM goods WHERE name = '{name}' ''')
        is_varitive = cur.fetchall()[0][0]
        
        if is_varitive:
            name = name + '_' + callback.message.text.split('\n')[1]
        
        if draft['order'][table][guest][name]['quantity'] == 1:
            del draft['order'][table][guest][name]
            bot.delete_message(callback.message.chat.id, callback.message.message_id)
        else:
            draft['order'][table][guest][name]['quantity'] -= 1
            bot.edit_message_text(f"{'🔄 ' if is_draft else ''}{name.split('_')[0]}, {draft['order'][table][guest][name]['quantity']} шт\n{draft['order'][table][guest][name]['comment']}", 
                        callback.message.chat.id, callback.message.message_id, 
                        reply_markup=make_buttons_for_good(True, table, guest))


        cur.execute(f''' UPDATE waiters SET json_draft = '{json.dumps(draft, ensure_ascii=False)}' where id_chat = {callback.message.chat.id}  ''')
        conn.commit()

        cur.close()
        conn.close()

    elif command == 'd': #УДАЛИТЬ ТОВАР ИЗ ЗАКАЗА
        conn = sqlite3.connect('DNK.db')
        cur = conn.cursor()

        cur.execute(f''' SELECT json_draft FROM waiters where id_chat = {callback.message.chat.id} ''')
        draft = json.loads(cur.fetchall()[0][0])

        cur.execute(f''' SELECT is_varitive FROM goods WHERE name = '{name}' ''')
        is_varitive = cur.fetchall()[0][0]
        
        if is_varitive:
            name = name + '_' + callback.message.text.split('\n')[1]
        
        del draft['order'][table][guest][name]
        bot.delete_message(callback.message.chat.id, callback.message.message_id)

        cur.execute(f''' UPDATE waiters SET json_draft = '{json.dumps(draft, ensure_ascii=False)}' where id_chat = {callback.message.chat.id}  ''')
        conn.commit()

        cur.close()
        conn.close()

    elif command == 'cm': #ОСТАВИТЬ КОММЕНТАРИЙ К БЛЮДУ
        conn = sqlite3.connect('DNK.db')
        cur = conn.cursor()

        cur.execute(f''' SELECT is_varitive FROM goods WHERE name = '{name}' ''')
        is_varitive = cur.fetchall()[0][0]

        cur.close()
        conn.close()
        
        if is_varitive:
            name = name + callback.message.text.split('\n')[1]

        def make_markup_for_comment():
            markup = types.ReplyKeyboardMarkup()

            btn_cancel = types.KeyboardButton('Отмена')

            markup.row(btn_cancel)

            return markup
        def write_comment(message, name, table, guest):
            bot.send_message(message.chat.id, f'Напиши комменатрий к {name} гостю {guest} за столом {table}', reply_markup=make_markup_for_comment())
            bot.register_next_step_handler(message, correct_comment, name, table, guest)
        def correct_comment(message, name, table, guest):
            text = message.text

            if text != 'Отмена':
                conn = sqlite3.connect('DNK.db')
                cur = conn.cursor()

                cur.execute(f''' SELECT json_draft FROM waiters where id_chat = {message.chat.id} ''')
                draft = json.loads(cur.fetchall()[0][0])
                
                draft['order'][table][guest][name]['comment'] += f'\n{text}'

                cur.execute(f''' UPDATE waiters SET json_draft = '{json.dumps(draft, ensure_ascii=False)}' where id_chat = {message.chat.id}  ''')
                conn.commit()

                cur.close()
                conn.close()

                display_order(message, table, guest)
            else:
                chose_category_menu(message, table, guest)
        
        write_comment(callback.message, name, table, guest)

    elif command == 'c': #ВЫВЕСТИ СОСТАВ БЛЮДА
        conn = sqlite3.connect('DNK.db')
        cur = conn.cursor()

        cur.execute(f''' SELECT compound FROM goods WHERE name = '{name}' ''')
        compound = cur.fetchall()[0][0]
        
        bot.send_message(callback.message.chat.id, f'Состав {name.split("_")[0]}:\n{compound}')

        cur.close()
        conn.close()

        chose_guest(callback.message, table)

    elif command == 't':
        chose_guest(callback.message, table)

bot.polling(non_stop=True)