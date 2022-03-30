import telebot
from random import shuffle
from telebot import types
import pymorphy2

from config import TOKEN

bot = telebot.TeleBot(TOKEN)
morph = pymorphy2.MorphAnalyzer()
word = morph.parse('вопрос')[0]


@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    item1 = types.KeyboardButton('🎓 Начать тестирование')
    item2 = types.KeyboardButton('💬 Доп информация')
    item3 = types.KeyboardButton('❓ Помощь')
    markup.add(item1, item2, item3)
    bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name} 👋\n'
                                      f'В этом боте вы можете пройти тест на тему *День Космонавтики* 🚀\n'
                                      f'В нём содержится {len(items)} {word.make_agree_with_number(len(items)).word}'
                                      f'\n\n\n_Бот создан для IT-Fest Chita 2022_', reply_markup=markup,
                     parse_mode='Markdown')


@bot.message_handler(commands=['main'])
def main(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    item1 = types.KeyboardButton('🎓 Начать тестирование')
    item2 = types.KeyboardButton('💬 Доп информация')
    item3 = types.KeyboardButton('❓ Помощь')
    markup.add(item1, item2, item3)
    bot.send_message(message.chat.id, f'Возвращаем вас в главное меню 😎', reply_markup=markup)


@bot.message_handler(content_types=['text'])
def get_user_text(message):
    if message.text == '🎓 Начать тестирование':
        markup = types.InlineKeyboardMarkup(row_width=2)
        item1 = types.InlineKeyboardButton('👍 Да', callback_data='yes_q')
        item2 = types.InlineKeyboardButton('👎 Нет', callback_data='no')
        markup.add(item1, item2)
        bot.send_message(message.chat.id,
                         f'Начинаем тестирование 📖\nТема тестирования: День космонавтики 👩‍🚀\n\n '
                         f'Количество вопросов: {len(items)}\n\n\n\nВы готовы пройти тестирование🤨?',
                         reply_markup=markup)

    elif message.text == '💬 Доп информация':
        bot.send_message(message.chat.id, f'Данный бот создан для тестирования пользователей на тему'
                                          f' *День Космонавтики* 🚀\n\nКоличество вопросов: {len(items)}',
                         parse_mode='Markdown')

    elif message.text == '❓ Помощь':
        bot.send_message(message.chat.id, f'Чтобы получить помощь, воспользуйте google.com')

    elif message.text == '❌ Отменить тест':
        users[message.chat.id] = {'num_question': 0, 'started': False, 'correct_answer': 0, 'wrong_answer': 0}
        bot.send_message(message.chat.id, f'Вы отменили тест')
        start(message)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    global users
    try:
        if call.message:
            if call.data == 'yes_q':
                users[call.message.chat.id] = {'num_question': 0, 'started': True, 'correct_answer': 0,
                                               'wrong_answer': 0}

                markup = types.ReplyKeyboardRemove()

                bot.send_message(call.message.chat.id, f'Загружаем вопросы... 🧐', reply_markup=markup)

                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                markup.add(types.KeyboardButton('❌ Отменить тест'))

                bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
                bot.send_message(call.message.chat.id, f'Начинаем тестирование 🔎', reply_markup=markup)

                shuffle(items[users[call.message.chat.id]['num_question']]['options'])
                a, b, c, d = [x for x in items[users[call.message.chat.id]['num_question']]['options']]

                markup2 = types.InlineKeyboardMarkup(row_width=2)
                markup2.add(types.InlineKeyboardButton(text=f'1️⃣ {a}', callback_data=f'{a}'),
                            types.InlineKeyboardButton(text=f'2️⃣ {b}', callback_data=f'{b}'),
                            types.InlineKeyboardButton(text=f'3️⃣ {c}', callback_data=f'{c}'),
                            types.InlineKeyboardButton(text=f'4️⃣ {d}', callback_data=f'{d}'))

                bot.send_message(call.message.chat.id,
                                 f'{users[call.message.chat.id]["num_question"] + 1} '
                                 f'вопрос 📖\n'
                                 f'\n*{items[users[call.message.chat.id]["num_question"]]["question"]}*',
                                 reply_markup=markup2, parse_mode='Markdown')

            elif call.data == 'no':
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text='Ничего страшного, мы подождём 😁', reply_markup=None)
            elif call.data == 'no_q':
                bot.edit_message_text(message_id=call.message.id, chat_id=call.message.chat.id,
                                      text=f'Поздравляем вы завершили тест🥳\n'
                                           f'Вот ваши результаты\n\n'
                                           f' ✅ Вы ответили правильно на '
                                           f'{users[call.message.chat.id]["correct_answer"]} из {len(items)}\n'
                                           f' ❌ Вы ответили неправльно на '
                                           f'{users[call.message.chat.id]["wrong_answer"]} из {len(items)}\n\n'
                                           f'Хорошего вам дня 😉', reply_markup=None)
                main(call.message)

            else:

                if call.data == items[users[call.message.chat.id]["num_question"]]["answer"] and \
                        users[call.message.chat.id]['started']:
                    users[call.message.chat.id]['correct_answer'] += 1

                    users[call.message.chat.id]['num_question'] += 1

                    if users[call.message.chat.id]['num_question'] < len(items):
                        shuffle(items[users[call.message.chat.id]['num_question']]['options'])

                        a, b, c, d = [x for x in items[users[call.message.chat.id]['num_question']]['options']]

                        markup2 = types.InlineKeyboardMarkup(row_width=2)
                        markup2.add(types.InlineKeyboardButton(text=f'1️⃣ {a}', callback_data=f'{a}'),
                                    types.InlineKeyboardButton(text=f'2️⃣ {b}', callback_data=f'{b}'),
                                    types.InlineKeyboardButton(text=f'3️⃣ {c}', callback_data=f'{c}'),
                                    types.InlineKeyboardButton(text=f'4️⃣ {d}', callback_data=f'{d}'))

                        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                              text=f'{users[call.message.chat.id]["num_question"] + 1} '
                                                   f'вопрос 📖\n\n*'
                                                   f'{items[users[call.message.chat.id]["num_question"]]["question"]}*',
                                              reply_markup=markup2, parse_mode='Markdown')

                elif users[call.message.chat.id]['started']:

                    users[call.message.chat.id]['wrong_answer'] += 1

                    users[call.message.chat.id]['num_question'] += 1

                    if users[call.message.chat.id]['num_question'] < len(items):
                        shuffle(items[users[call.message.chat.id]['num_question']]['options'])

                        a, b, c, d = [x for x in items[users[call.message.chat.id]['num_question']]['options']]

                        markup2 = types.InlineKeyboardMarkup(row_width=2)
                        markup2.add(types.InlineKeyboardButton(text=f'1️⃣ {a}', callback_data=f'{a}'),
                                    types.InlineKeyboardButton(text=f'2️⃣ {b}', callback_data=f'{b}'),
                                    types.InlineKeyboardButton(text=f'3️⃣ {c}', callback_data=f'{c}'),
                                    types.InlineKeyboardButton(text=f'4️⃣ {d}', callback_data=f'{d}'))

                        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                              text=f'{users[call.message.chat.id]["num_question"] + 1} '
                                                   f'вопрос 📖\n\n*'
                                                   f'{items[users[call.message.chat.id]["num_question"]]["question"]}*',
                                              reply_markup=markup2, parse_mode='Markdown')

                if users[call.message.chat.id]["num_question"] == len(items) and users[call.message.chat.id]['started']:
                    users[call.message.chat.id]['started'] = False

                    markup = types.InlineKeyboardMarkup()
                    markup.add(types.InlineKeyboardButton('👍 Да', callback_data='yes_q'),
                               types.InlineKeyboardButton('👎 Нет', callback_data='no_q'))

                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                          text=f'Поздравляем вы завершили тест🥳\n'
                                               f'Вот ваши результаты\n\n'
                                               f'✅ Вы ответили правильно на '
                                               f'{users[call.message.chat.id]["correct_answer"]} из {len(items)}\n'
                                               f'❌ Вы ответили неправльно на '
                                               f'{users[call.message.chat.id]["wrong_answer"]} из {len(items)}\n\n'
                                               f'Хотите ли вы пройти тест заново?', reply_markup=markup)
    except Exception as es:
        print(repr(es))


with open('question.txt', 'r', encoding='utf-8') as e:
    items = eval(e.read())
users = dict()
bot.infinity_polling()