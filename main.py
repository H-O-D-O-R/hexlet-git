import telebot
from telebot import types
import sqlite3
import json
import re

bot = telebot.TeleBot('6554881247:AAE0GVjHxGdwjwmCWeDYkhT_r-EweXhhtgU')

# ЗАПУСК БОТА
@bot.message_handler(commands=['start'])
def start(message: telebot.types.Message):
    return chose_table(message.chat.id)

#ЗАЛ
#Создание шаблона кнопок столов зала
def make_markup_tables(chat_id:int): 
    conn = sqlite3.connect('DNK.db')
    cur = conn.cursor()

    cur.execute(f''' SELECT active_tables, id_chat FROM waiters ''')
    tables_and_id_chats = {id_chat : (active_table.split(', ') if active_table else []) for active_table, id_chat in cur.fetchall()}

    client_active_tables = set(tables_and_id_chats[chat_id])
    active_tables = set()
    for tables in tables_and_id_chats.values():
        active_tables.update(tables)
    active_tables = active_tables - client_active_tables

    cur.execute(f''' SELECT json_draft FROM waiters WHERE id_chat = '{chat_id}' ''')
    draft = cur.fetchall()[0][0]
    if draft:
        draft = json.loads(draft)
        client_draft_tables = set(draft['order'])
    else:
        client_draft_tables = set()

    def is_active_table(table):
        if table in client_draft_tables:
            return f'{table} 🔄'
        if table in client_active_tables:
            return f'{table} 🟩'
        elif table in active_tables:
            return f'{table} 🟦'
        return table
    
    markup = types.ReplyKeyboardMarkup()

    cur.execute(f''' SELECT markup FROM markups WHERE name='зал' ''')
    rows = json.loads( cur.fetchall()[0][0] )

    cur.close()
    conn.close()
    
    btns = []
    for row in rows:
        btns.append([])
        for table in row:
            btns[-1].append( types.KeyboardButton(is_active_table(table)) )
    
        markup.row( *btns[-1] )

    return markup
#Выбор стола пользователем
def chose_table(chat_id:int):
    bot.send_message(chat_id, 'Выбери стол', reply_markup=make_markup_tables(chat_id))
    bot.register_next_step_handler_by_chat_id(chat_id, correct_table)
#Обработка выбранной кнопки
def correct_table(message:telebot.types.Message):
    text = message.text.split()[0]

    conn = sqlite3.connect('DNK.db')
    cur = conn.cursor()

    cur.execute(''' SELECT name FROM markups ''')
    numbers = set(number[0] for number in cur.fetchall())

    if text.isdigit() and text in numbers:
        number_of_table = text
        return chose_guest(message.chat.id, number_of_table)
    else:
        return chose_table(message.chat.id)

#ГОСТИ
#Создание шаблона кнопок гостей за столом
def make_markup_guests(chat_id:int, number_of_table:int):
    conn = sqlite3.connect('DNK.db')
    cur = conn.cursor()

    cur.execute(f''' SELECT json_draft FROM waiters WHERE id_chat = '{chat_id}' ''')
    draft = cur.fetchall()[0][0]

    is_draft = False
    is_active = False

    if draft:
        draft = json.loads(draft)
        draft.setdefault('order', {}).setdefault(number_of_table, {})
        if draft['order'][number_of_table]:
            is_draft = True
        else:
            cur.execute(f''' SELECT * FROM moving_of_tables WHERE active = '1' and number_of_table = '{number_of_table}' ''')
            is_active = cur.fetchall()
            if is_active:
                is_active = True

        
    markup = types.ReplyKeyboardMarkup()
    
    btn_pass = types.KeyboardButton('.')
    btn_table = types.KeyboardButton('###')
    btn_tables = types.KeyboardButton('Зал')
    btn_order = types.KeyboardButton('Заказ')

    if is_draft:
        btn_place_order_or_bill = types.KeyboardButton('Печать')
    elif is_active:
        btn_place_order_or_bill = types.KeyboardButton('Счет')
    else:
        btn_place_order_or_bill = btn_pass

    def make_button_for_table(name):
        if name.isdigit():
            return types.KeyboardButton(name)
        elif name == 'btn_pass':
            return btn_pass
        elif name == 'btn_table':
            return btn_table
        elif name == 'btn_tables':
            return btn_tables
        elif name == 'btn_order':
            return btn_order
        return btn_place_order_or_bill

    cur.execute(f''' SELECT markup FROM markups WHERE name='{number_of_table}' ''')
    data = json.loads(cur.fetchall()[0][0])

    btns = []
    for row in data:
        btns.append([])
        for name in row:
            btns[-1].append(make_button_for_table(name))
        
        markup.row(*btns[-1])
    
    return markup
#Выбор гостя пользователем
def chose_guest(chat_id:int, number_of_table:int):
    bot.send_message(chat_id, 'Выбери гостя', reply_markup=make_markup_guests(chat_id, number_of_table))
    bot.register_next_step_handler_by_chat_id(chat_id, correct_guest, number_of_table)
#Обработка выбранной кнопки
def correct_guest(message: telebot.types.Message, number_of_table:int):
    text = message.text

    if text.isdigit():
        number_of_guest = text
        return chose_order(message.chat.id, number_of_table, number_of_guest, [], 0)
    elif text == 'Зал':
        return chose_table(message.chat.id)
    elif text == 'Заказ':
        display_order(message.chat.id, number_of_table)
        return chose_guest(message.chat.id, number_of_table)
    elif text == 'Печать':
        return place_order(message.chat.id, number_of_table)
    elif text == 'Счет':
        bill(message.chat.id, number_of_table)
    else:
        return chose_guest(message.chat.id, number_of_table)


#Печать
def place_order(chat_id:int, number_of_table:int, is_bill:bool=False):
    conn = sqlite3.connect('DNK.db')
    cur = conn.cursor()

    cur.execute(f''' SELECT id_waiter, active_tables, json_draft FROM waiters where id_chat = '{chat_id}' ''')
    id_waiter, active_tables, draft = cur.fetchall()[0]
    draft = json.loads(draft)

    if not number_of_table in draft['order']:
        bot.send_message(chat_id, 'Ничего не заказано')
        return chose_guest(chat_id, number_of_table)

    active_tables = (active_tables.split(', ') if active_tables else [])

    if not number_of_table in active_tables:
        active_tables.append(number_of_table)
    
    active_tables = ', '.join(active_tables)
    cur.execute(f''' UPDATE waiters SET active_tables = '{active_tables}' WHERE id_waiter = '{id_waiter}' ''')
    conn.commit()

    order_for_table = draft['order'][number_of_table]

    cur.execute(f''' SELECT id_bill, summary, json_detailed_order FROM moving_of_tables WHERE active = '1' and number_of_table = '{number_of_table}' ''')
    item = cur.fetchall()

    if item:
        id_bill, summary, detailed_order = item[0]
        detailed_order = json.loads(detailed_order)
        summary = summary
    else:
        cur.execute(f''' INSERT INTO moving_of_tables (	"number_of_table", "active", "id_waiter", "summary", "json_detailed_order", "payment_method") 
                    VALUES ({number_of_table}, '1', '{id_waiter}', '{0}', '', '') ''')
        conn.commit()

        cur.execute(f''' SELECT id_bill FROM moving_of_tables WHERE active = '1' and number_of_table = '{number_of_table}' ''')
        id_bill = cur.fetchall()[0][0]
        summary, detailed_order = 0, {}
    
    for guest, order_for_guest in order_for_table.items():
        detailed_order[guest] = detailed_order.get(guest, {})
        for good, item in order_for_guest.items():
            detailed_order[guest][good] = detailed_order[guest].get(good, {})
            detailed_order[guest][good]['quantity'] = detailed_order[guest][good].get('quantity', 0) + item['quantity']            

            cur.execute(f''' SELECT id_good, is_varitive, cost FROM goods WHERE name = '{good.split('_')[0]}' ''')
            id_good, is_varitive, cost = cur.fetchall()[0]
            cost = int(cost)
            
            comments = item['comment']
            if is_varitive:
                comments = comments.split('\n')
                varitive  = f'<i>{comments[0]}</i>'
                comments = '\n'.join(comments[1:])
            else:
                varitive = ''

            detailed_order[guest][good]['comment'] = detailed_order[guest][good].get('comment', varitive)
            if comments:
                new_line = "\n"
                detailed_order[guest][good]['comment'] += f'{new_line if detailed_order[guest][good]["comment"] else ""}{item["quantity"]} шт : <i>{comments}</i>'

            summary += cost
            for _ in range(item['quantity']):
                cur.execute(f''' INSERT INTO moving_of_goods (id_bill, number_of_guest, id_good, comment )
                            VALUES ('{id_bill}', '{guest}', '{id_good}', '{item['comment']}')  ''')
                conn.commit()
    
    cur.execute(f''' UPDATE moving_of_tables SET summary = '{summary}', json_detailed_order = '{json.dumps(detailed_order, ensure_ascii=False)}'
                 WHERE active = '1' and number_of_table = '{number_of_table}' ''')
    conn.commit()

    del draft['order'][number_of_table]
    cur.execute(f''' UPDATE waiters SET json_draft = '{json.dumps(draft, ensure_ascii=False)}' WHERE id_waiter = '{id_waiter}' ''')
    conn.commit()

    cur.close()
    conn.close()

    if is_bill:
        return None
    return chose_table(chat_id)

#Создание шаблона кнопок способа оплаты
def make_markup_payment_method():
    markup = types.ReplyKeyboardMarkup()

    btn_card = types.KeyboardButton('Карта')
    btn_cash = types.KeyboardButton('Наличка')
    markup.row(btn_card, btn_cash)

    btn_cancel = types.KeyboardButton('Отмена')
    markup.row(btn_cancel)

    return markup
#Способ оплаты
def payment_method(chat_id:int, number_of_table:int):
    bot.send_message(chat_id, 'Выбери способ оплаты', reply_markup=make_markup_payment_method())
    bot.register_next_step_handler_by_chat_id(chat_id, correct_payment_method, number_of_table)
#Обработка выбранной кнопки
def correct_payment_method(message:telebot.types.Message, number_of_table:int):
    text = message.text

    if text == 'Карта' or text == 'Наличка':
        conn = sqlite3.connect('DNK.db')
        cur = conn.cursor()

        cur.execute(f''' UPDATE moving_of_tables SET active = '0', payment_method = '{text}'
                    WHERE active = '1' and number_of_table = '{number_of_table}' ''')
        conn.commit()

        cur.execute(f''' SELECT active_tables FROM waiters WHERE id_chat = '{message.chat.id}' ''')
        active_tables = cur.fetchall()[0][0].split(', ')
        active_tables.remove(number_of_table)
        active_tables = ', '.join(active_tables)
        cur.execute(f''' UPDATE waiters SET active_tables = '{active_tables}' WHERE id_chat = '{message.chat.id}' ''')
        conn.commit()

        cur.close()
        conn.close()

        chose_table(message.chat.id)
    elif text == 'Отмена':
        return chose_table(message.chat.id)
    else:
        return payment_method(message.chat.id)

#Счёт
def bill(chat_id:int, number_of_table:int):
    conn = sqlite3.connect('DNK.db')
    cur = conn.cursor()

    cur.execute(f''' SELECT json_draft FROM waiters WHERE id_chat = '{chat_id}' ''')
    draft = json.loads(cur.fetchall()[0][0])['order']

    if number_of_table in draft:
        place_order(chat_id, number_of_table, is_bill=True)

    cur.execute(f"SELECT summary, json_detailed_order from moving_of_tables where active = '1' and number_of_table = '{number_of_table}'")
    table_summary, last_data_of_guests = cur.fetchall()[0]
    last_data_of_guests = json.loads(last_data_of_guests)

    text = f" {'-' * 67}\n{' ' * 30}СТОЛ {number_of_table}\n{'-'*67}"
    
    guests = last_data_of_guests.keys()

    for guest in guests:
        text += f'\n{"-" * 67}\n{" " * 30}ГОСТЬ {guest}\n{"-" * 67}'

        summary = 0
        for name, value in last_data_of_guests.get(guest, {}).items():
            name = name.split('_')[0]

            cur.execute(f''' SELECT cost FROM goods WHERE name = '{name}' ''')
            cost = cur.fetchall()[0][0]
            summary += cost
            
            new_line = '\n'
            text += f"\n<b>{name}</b>, {value['quantity']} шт\n{value['comment']}{new_line if value['comment'] else ''}{cost} ₽ * {value['quantity']} = {cost * value['quantity']} ₽\n"
        text += f'\n{"-" * 67}\n<b>ИТОГО У ГОСТЯ {guest}:  {summary} ₽</b>\n'
    
    
    text += f'\n{"#" * 30}\n<b>ИТОГО:  {table_summary} ₽</b>'

    bot.send_message(chat_id, text, parse_mode='HTML')
                   
    cur.close()
    conn.close()

    return payment_method(chat_id, number_of_table)


#УНИВЕРСАЛЬНАЯ ФУНКЦИЯ ДЛЯ ВЫВОДА РАЗДЕЛОВ И ТОВАРОВ
#Создание шаблона кнопок меню
def make_markup_order(names:list, number_of_guest:int, is_last:int, is_guests_button, is_guest_button, is_draft, is_active):
    markup = types.ReplyKeyboardMarkup()

    btns = [[]]
    for name in names:
        if len(btns[-1]) == 2:
            btns.append([])
        btns[-1].append( types.KeyboardButton( name ) )
    
    service_buttons = []
    if is_guest_button:
        service_buttons.append(f'Гость {number_of_guest}')
    if is_guests_button:
        service_buttons.append('Гости')
    service_buttons.append('Зал')
    service_buttons.append('Заказ')
    if is_draft:
        service_buttons.append('Печать')
    elif is_active:
        service_buttons.append('Счёт')
    service_buttons.append('Назад')

    btns.append([])

    for name in service_buttons:
        if len(btns[-1]) == 3:
            btns.append([])    
        btns[-1].append( types.KeyboardButton( name ) )
    
    for row in btns:
        markup.row( *row )

    return markup
#Выбор меню пользователем
def chose_order(chat_id:int, number_of_table:int, number_of_guest:int, categories:list, is_last:int):
    conn = sqlite3.connect('DNK.db')
    cur = conn.cursor()

    category = ' '.join(categories).lstrip()

    if is_last:
        cur.execute(f''' SELECT name, is_limit, limit_cnt, is_varitive, varities FROM goods WHERE category = '{category}' ''')
        data_for_correct = {}
        list_for_markup = []

        for name, is_limit, limit_cnt, is_varitive, varities in cur.fetchall():
            data_for_correct[name] = {'is_varitive': is_varitive, 'varities': varities}

            if is_limit:
                if limit_cnt == 0:
                    name = f'⛔️{name}'
                else:
                    name = f'❗️ {str(limit_cnt)} {name}'
            list_for_markup.append(name)
    else:
        cur.execute(f''' SELECT name FROM navigation WHERE categories = '{category}' ''')
        list_for_markup = [item[0] for item in cur.fetchall()]
        data_for_correct = list_for_markup

    cur.execute(f''' SELECT json_draft, active_tables FROM waiters WHERE id_chat = '{chat_id}' ''')
    draft, active_tables = cur.fetchall()[0]
    draft = (json.loads(draft) if draft else {})

    is_guests_button = len(categories) > 0
    is_guest_button = len(categories) > 1
    is_draft, is_active = False, False
    if draft and number_of_table in draft.setdefault('order', {}):
        is_draft = True
    elif number_of_table in active_tables.split(', '):
        is_active = True

    cur.close()
    conn.close()

    bot.send_message(chat_id, f'Выбери {"товар" if is_last else "раздел"}', reply_markup=make_markup_order(list_for_markup, number_of_guest, is_last, is_guests_button, is_guest_button, is_draft, is_active))
    bot.register_next_step_handler_by_chat_id(chat_id, correct_order, number_of_table, number_of_guest, data_for_correct, categories, is_last)
#Обработка выбранной кнопки
def correct_order(message:telebot.types.Message, number_of_table:int, number_of_guest:int, data:dict|list, categories:list, is_last:int):
    text = message.text

    limit = 0
    if ord(text[0]) == 9940:
        bot.send_message(message.chat.id, 'Товар находится в стоп-листе')
        return chose_order(message.chat.id, number_of_table, number_of_guest, categories, is_last)
    elif ord(text[0]) == 10071:
        text = text.split()
        limit = int(text[1])
        text = ' '.join(text[2:])
    
    if text in data:
        if is_last:
            if limit:
                conn = sqlite3.connect('DNK.db')
                cur = conn.cursor()

                cur.execute(f''' UPDATE goods SET limit_cnt = '{limit - 1}' WHERE name = '{text}' ''')
                conn.commit()

                cur.close()
                conn.close()

            good = {'name': text, **data[text]}
            if good['is_varitive']:
                return chose_variative_good(message.chat.id, number_of_table, number_of_guest, good, categories, is_last)
            else:
                add_good_to_order(message.chat.id, number_of_table, number_of_guest, good)
                return chose_order(message.chat.id, number_of_table, number_of_guest, categories, is_last)
        
        conn = sqlite3.connect('DNK.db')
        cur = conn.cursor()

        category = ' '.join(categories).lstrip()
        cur.execute(f''' SELECT is_last FROM navigation WHERE categories = '{category}' and name = '{text}' ''')
        is_last = cur.fetchall()[0][0]
        categories.append( text.lower() )

        cur.close()
        conn.close()
        
        return chose_order(message.chat.id, number_of_table, number_of_guest, categories, is_last)
    elif text == 'Зал':
        return chose_table(message.chat.id)
    elif text == 'Гости':
        return chose_guest(message.chat.id, number_of_table)
    elif text == f'Гость {number_of_guest}':
        return chose_order(message.chat.id, number_of_table, number_of_guest, [], 0)
    elif text == 'Назад':
        if categories:
            return chose_order(message.chat.id, number_of_table, number_of_guest, categories[:-1], 0)
        return chose_guest(message.chat.id, number_of_table)
    elif text == 'Заказ':
        display_order(message.chat.id, number_of_table, number_of_guest)
        return chose_order(message.chat.id, number_of_table, number_of_guest, categories, is_last)
    elif text == 'Печать':
        return place_order(message.chat.id, number_of_table)
    elif text == 'Счёт':
        return bill(message.chat.id, number_of_table)
    else:
        bot.send_message(message.chat.id, f'{"Товар" if is_last else "Раздел"} не найден')
        return chose_order(message.chat.id, number_of_table, number_of_guest, categories, is_last)


#ДОБАВИТЬ ТОВАР В ЗАКАЗ
def add_good_to_order(chat_id:int, number_of_table:int, number_of_guest:int, good:dict, variant:str=''):
    conn = sqlite3.connect('DNK.db')
    cur = conn.cursor()

    cur.execute(f"SELECT json_draft from waiters where id_chat = '{chat_id}'")
    data = cur.fetchall()[0][0]
    data = (json.loads(data) if data else {})
    
    data.setdefault('order', {}).setdefault(number_of_table, {}).setdefault(number_of_guest, {})

    data_of_guest = data['order'][number_of_table][number_of_guest]

    if variant:
        name = good['name'] + '_' + variant
    else:
        name = good['name']

    data_of_guest[name] = data_of_guest.get(name, {'quantity': 0, 'comment': variant})
    data_of_guest[name]['quantity'] += 1
     
    data = json.dumps(data, ensure_ascii=False)

    cur.execute(f'''UPDATE waiters SET json_draft = '{data}' where id_chat = '{chat_id}' ''')
    conn.commit()

    cur.close()
    conn.close()

    display_order(chat_id, number_of_table, number_of_guest)

#Вывод заказа стола
def display_order(chat_id:int, number_of_table:int, number_of_guest:int=None):
    conn = sqlite3.connect('DNK.db')
    cur = conn.cursor()
    
    cur.execute(f"SELECT json_draft from waiters where id_chat = '{chat_id}'")
    data = cur.fetchall()[0][0]
    if data and number_of_table in json.loads(data)['order']:
        new_data_of_guests = json.loads(data)['order'][number_of_table]
    else:
        new_data_of_guests = {}

    cur.execute(f"SELECT json_detailed_order from moving_of_tables where active = '1' and number_of_table = '{number_of_table}'")
    last_data_of_guests = cur.fetchall()

    if last_data_of_guests:
        last_data_of_guests = json.loads(last_data_of_guests[0][0])
    else:
        last_data_of_guests = {}
    
    if not last_data_of_guests and not new_data_of_guests:
        bot.send_message(chat_id, 'Ничего не заказано')
        return None
    
    bot.send_message(chat_id, f" {'-' * 60}\n{' ' * 25}СТОЛ {number_of_table}\n{'-'*60}")
    
    guests = set( list(last_data_of_guests.keys()) + list(new_data_of_guests.keys()) )
    if number_of_guest:
        guests = sorted(guests  - {number_of_guest}) + [number_of_guest]

    for guest in guests:
        if not last_data_of_guests.get(guest, False) and not new_data_of_guests.get(guest, False):
            continue

        bot.send_message(chat_id, f'{"-" * 60}\n{" " * 25}ГОСТЬ {guest}\n{"-" * 60}')

        markup = make_buttons_for_good(False, number_of_table, guest)
        for name, value in last_data_of_guests.get(guest, {}).items():
            bot.send_message(chat_id, f"<b>{name.split('_')[0]}</b>, {value['quantity']} шт\n<i>{value['comment']}</i>", reply_markup=markup, parse_mode='HTML')
        
        markup = make_buttons_for_good(True, number_of_table, guest)
        for name, value in new_data_of_guests.get(guest, {}).items():
            bot.send_message(chat_id, f"🔄 <b>{name.split('_')[0]}</b>, {value['quantity']} шт\n<i>{value['comment']}</i>", reply_markup=markup, parse_mode='HTML')
        
    cur.close()
    conn.close()

#Создание шаблона кнопок для товаров заказа
def make_buttons_for_good(is_draft:bool, number_of_table:int, guest:int):
    markup = types.InlineKeyboardMarkup()

    btn_add = types.InlineKeyboardButton('➕', callback_data=f"a_{number_of_table}_{guest}")    
    btn_reduce = types.InlineKeyboardButton('➖', callback_data=f'r_{number_of_table}_{guest}')
    btn_delete = types.InlineKeyboardButton('🗑', callback_data=f'd_{number_of_table}_{guest}')
    btn_comment = types.InlineKeyboardButton('✏️', callback_data=f'cm_{number_of_table}_{guest}')
    btn_compound = types.InlineKeyboardButton('📕', callback_data=f'c_{number_of_table}_{guest}')

    if is_draft:
        btns = [btn_add, btn_reduce, btn_delete, btn_comment, btn_compound]
    else:
        btns = [btn_add, btn_compound]

    markup.row(*btns)

    return markup


#Создание шаблона вариативных товаров
def make_markup_variative_goods(good:dict):
    markup = types.ReplyKeyboardMarkup()

    btns = [[]]
    for variant in good['varities'].split(', '):
        if len(btns[-1]) == 2:
            btns.append([])
        btns[-1].append( types.KeyboardButton(variant) )
    
    for row in btns:
        markup.row( *row )
    
    markup.row( 'Назад' )

    return markup         
#Выбор вариативных блюд
def chose_variative_good(chat_id:int, number_of_table:int, number_of_guest:int, good:dict, categories:list, is_last:int):
    bot.send_message(chat_id, 'Выбери вариацию', reply_markup=make_markup_variative_goods(good))
    bot.register_next_step_handler_by_chat_id(chat_id, correct_variative_good, number_of_table, number_of_guest, good, categories, is_last)
#Обработка выбранной кнопки
def correct_variative_good(message:telebot.types.Message, number_of_table:int, number_of_guest:int, good:dict, categories:list, is_last:int):
    text = message.text

    if text in good['varities'].split(', '):
        add_good_to_order(message.chat.id, number_of_table, number_of_guest, good, text)
    
    return chose_order(message.chat.id, number_of_table, number_of_guest, categories, is_last)


#СОЗДАНИИЕ ФУНКЦИИ ДЛЯ КНОПОК
@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback:telebot.types.CallbackQuery):
    name = callback.message.text.split(',')[0]
    chat_id = callback.message.chat.id

    is_draft = False
    if name.startswith('🔄'):
        is_draft = True
        name = name[2:]

    command, table, guest, *index = callback.data.split('_')

    if command == 'a': #ДОБАВИТЬ ЕДИНИЦУ ТОВАРА
        conn = sqlite3.connect('DNK.db')
        cur = conn.cursor()

        cur.execute(f''' SELECT is_varitive, is_limit, limit_cnt FROM goods WHERE name = '{name}' ''')
        is_varitive, is_limit, limit_cnt = cur.fetchall()[0]
        if is_limit:
            if limit_cnt == 0:
                bot.send_message(callback.message.chat.id, 'Товар находится в стоп-листе')
                return None
            
            cur.execute(f''' UPDATE goods SET limit_cnt = '{limit_cnt - 1}' WHERE name = '{name}' ''')
            conn.commit()            
                
        if is_varitive:
            name = name + '_' + callback.message.text.split('\n')[1]
        
        cur.execute(f''' SELECT json_draft FROM waiters where id_chat = {chat_id} ''')
        draft = json.loads(cur.fetchall()[0][0])

        draft.setdefault('order', {}).setdefault(table, {}).setdefault(guest, {}).setdefault(name, {'quantity': 0, 'comment': ''})
        draft['order'][table][guest][name]['quantity'] += 1
        if not is_draft and is_varitive and not draft['order'][table][guest][name]['comment']:
            draft['order'][table][guest][name]['comment'] = callback.message.text.split('\n')[1]
        
        cur.execute(f''' UPDATE waiters SET json_draft = '{json.dumps(draft, ensure_ascii=False)}' WHERE id_chat = '{chat_id}' ''')
        conn.commit()

        cur.close()
        conn.close()

        if is_draft:
            bot.edit_message_text(f"{'🔄 ' if is_draft else ''}<b>{name.split('_')[0]}</b>, {draft['order'][table][guest][name]['quantity']} шт\n<i>{draft['order'][table][guest][name]['comment']}</i>", 
                                chat_id, callback.message.message_id, 
                                reply_markup=make_buttons_for_good(True, table, guest), parse_mode='HTML')
        else:
            display_order(chat_id, table, guest)
        
    elif command == 'r': #УБРАТЬ ЕДИНИЦУ ТОВАРА
        conn = sqlite3.connect('DNK.db')
        cur = conn.cursor()

        cur.execute(f''' SELECT is_limit, limit_cnt, is_varitive FROM goods WHERE name = '{name}' ''')
        is_limit, limit_cnt, is_varitive = cur.fetchall()[0]

        if is_limit:
            cur.execute(f''' UPDATE goods SET limit_cnt = '{limit_cnt + 1}' WHERE name = '{name}' ''')
            conn.commit()

        cur.execute(f''' SELECT json_draft FROM waiters where id_chat = {chat_id} ''')
        draft = json.loads(cur.fetchall()[0][0])
        
        if is_varitive:
            name = name + '_' + callback.message.text.split('\n')[1]
        
        if draft['order'][table][guest][name]['quantity'] == 1:
            del draft['order'][table][guest][name]
            bot.delete_message(chat_id, callback.message.message_id)
            if not draft['order'][table][guest]:
                del draft['order'][table][guest]
                if not draft['order'][table]:
                    del draft['order'][table]
        else:
            draft['order'][table][guest][name]['quantity'] -= 1
            bot.edit_message_text(f"{'🔄 ' if is_draft else ''}<b>{name.split('_')[0]}</b>, {draft['order'][table][guest][name]['quantity']} шт\n<i>{draft['order'][table][guest][name]['comment']}</i>", 
                        chat_id, callback.message.message_id, 
                        reply_markup=make_buttons_for_good(True, table, guest), parse_mode='HTML')


        cur.execute(f''' UPDATE waiters SET json_draft = '{json.dumps(draft, ensure_ascii=False)}' where id_chat = {chat_id}  ''')
        conn.commit()

        cur.close()
        conn.close()

    elif command == 'd': #УДАЛИТЬ ТОВАР ИЗ ЗАКАЗА
        conn = sqlite3.connect('DNK.db')
        cur = conn.cursor()

        cur.execute(f''' SELECT is_limit, limit_cnt, is_varitive FROM goods WHERE name = '{name}' ''')
        is_limit, limit_cnt, is_varitive = cur.fetchall()[0]

        if is_limit:
            cnt = int(re.search(', (\d+) шт', callback.message.text).group(1))
            cur.execute(f''' UPDATE goods SET limit_cnt = '{limit_cnt + cnt}' WHERE name = '{name}' ''')
            conn.commit()

        cur.execute(f''' SELECT json_draft FROM waiters where id_chat = {chat_id} ''')
        draft = json.loads(cur.fetchall()[0][0])
        
        if is_varitive:
            name = name + '_' + callback.message.text.split('\n')[1]
        
        del draft['order'][table][guest][name]
        if not draft['order'][table][guest]:
                del draft['order'][table][guest]
                if not draft['order'][table]:
                    del draft['order'][table]

        bot.delete_message(chat_id, callback.message.message_id)

        cur.execute(f''' UPDATE waiters SET json_draft = '{json.dumps(draft, ensure_ascii=False)}' where id_chat = {chat_id}  ''')
        conn.commit()

        cur.close()
        conn.close()

    elif command == 'dc': #УДАЛИТЬ КОММЕНТАРИЙ К ТОВАРУ
        conn = sqlite3.connect('DNK.db')
        cur = conn.cursor()
        index = int(index[0])

        cur.execute(f''' SELECT json_draft FROM waiters where id_chat = '{chat_id}' ''')
        draft = json.loads(cur.fetchall()[0][0])

        name = draft['last_good_for_comment']
                
        comments = draft['order'][table][guest][name]['comment'].split('\n')
        del comments[index]
        draft['order'][table][guest][name]['comment'] = '\n'.join(comments)

        bot.delete_message(chat_id, callback.message.message_id)

        cur.execute(f''' UPDATE waiters SET json_draft = '{json.dumps(draft, ensure_ascii=False)}' where id_chat = '{chat_id}'  ''')
        conn.commit()

        cur.close()
        conn.close()

    elif command == 'cm': #ОСТАВИТЬ КОММЕНТАРИЙ К БЛЮДУ
        conn = sqlite3.connect('DNK.db')
        cur = conn.cursor()

        cur.execute(f''' SELECT is_varitive FROM goods WHERE name = '{name}' ''')
        is_varitive = cur.fetchall()[0][0]
        
        if is_varitive:
            name = name + '_' + callback.message.text.split('\n')[1]
            comments = callback.message.text.split('\n')[2:]
            start = 1
        else:
            comments = callback.message.text.split('\n')[1:]
            start = 0

        cur.execute(f''' SELECT json_draft from waiters where id_chat = '{chat_id}' ''')
        draft = json.loads(cur.fetchall()[0][0])

        draft['last_good_for_comment'] = name

        cur.execute(f''' UPDATE waiters SET json_draft = '{json.dumps(draft, ensure_ascii=False)}' WHERE id_chat = '{chat_id}' ''')
        conn.commit()

        cur.close()
        conn.close()

        def make_markup_for_comment():
            markup = types.ReplyKeyboardMarkup()
            btn_cancel = types.KeyboardButton('Отмена')
            markup.row(btn_cancel)

            return markup
        def make_inline_markup_for_comment(index:int):
            markup = types.InlineKeyboardMarkup()
            btn_delete = types.InlineKeyboardButton('Удалить', callback_data=f'dc_{table}_{guest}_{index}')
            markup.row(btn_delete)

            return markup
        def write_comment(chat_id:int, name:str, table:int, guest:int, comments:str, start:int):
            for index, comment in enumerate(comments, start):
                bot.send_message(chat_id, f'<i>{comment}</i>', reply_markup=make_inline_markup_for_comment(index), parse_mode='HTML')
            bot.send_message(chat_id, f"Напиши комменатрий к {name.split('_')[0]}", reply_markup=make_markup_for_comment())
            bot.register_next_step_handler_by_chat_id(chat_id, correct_comment, name, table, guest)
        def correct_comment(message:telebot.types.Message, name:str, table:int, guest:int):
            text = message.text

            if text != 'Отмена':
                conn = sqlite3.connect('DNK.db')
                cur = conn.cursor()

                cur.execute(f''' SELECT json_draft FROM waiters where id_chat = '{message.chat.id}' ''')
                draft = json.loads(cur.fetchall()[0][0])
                
                good_in_order = draft['order'][table][guest][name]
                good_in_order['comment'] += ("\n" + text if good_in_order["comment"] else text)

                cur.execute(f''' UPDATE waiters SET json_draft = '{json.dumps(draft, ensure_ascii=False)}' where id_chat = '{message.chat.id}'  ''')
                conn.commit()

                cur.close()
                conn.close()

                display_order(message.chat.id, table, guest)
        
        write_comment(chat_id, name, table, guest, comments, start)

    elif command == 'c': #ВЫВЕСТИ СОСТАВ БЛЮДА
        conn = sqlite3.connect('DNK.db')
        cur = conn.cursor()

        cur.execute(f''' SELECT compound FROM goods WHERE name = '{name}' ''')
        compound = cur.fetchall()[0][0]
        
        bot.send_message(chat_id, f'Состав {name.split("_")[0]}:\n{compound}')

        cur.close()
        conn.close()

bot.polling(non_stop=True)