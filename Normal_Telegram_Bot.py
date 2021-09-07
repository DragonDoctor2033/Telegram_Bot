import logging
import random
import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, ConversationHandler, \
    MessageHandler, Filters
from Token_Bot import Token
from bs4 import BeautifulSoup

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

FIRST, SECOND, THREE = range(3)
dictionary = {
    0: 'Дата данных: ',
    1: 'За последний день: ',
    2: 'Всего: ',
    3: 'За последние 14 дней: ',
    4: 'На 100 тыс человек: '
}

keyboard = [
    [
        InlineKeyboardButton(text='Узнай.', callback_data='Huj'),
        InlineKeyboardButton(text='Пароль.', callback_data='password'),
        InlineKeyboardButton(text='Исходный код этого бота.', url='https://github.com/DragonDoctor2033'
                                                                  '/Telegram_Bot/blob/main/Normal_Telegram_Bot.py')
    ],
    [
        InlineKeyboardButton(text='Wanna Play? ', callback_data='game')
    ],
    [
        InlineKeyboardButton(text='Закончить общение с ботом.', callback_data='end')
    ]
]
reply_markup = InlineKeyboardMarkup(keyboard)


def generate_password():
    words_text = open('enlist_words.txt', 'r')
    words_list, symbols, password_end = words_text.read().split(), '-+=*_.,:;', ''
    words_text.close()
    random_symbol = random.choice(symbols)
    for _ in range(4):
        if random.randint(0, 1) == 1:
            password_end += random.choice(words_list) + random_symbol
        else:
            password_end += random.choice(words_list).upper() + random_symbol
    return password_end + str(random.randrange(1000, 10000))


def get_respond_delivery(update: Update, context: CallbackContext):
    result = ''
    respond = requests.get(f'https://www.omniva.ee/api/search.php?search_barcode={update.message.text}')
    soup = BeautifulSoup(respond.text, 'html.parser')
    text = soup.find_all('tbody')
    for texts in text:
        texts = list(texts.find_all('td'))[0:3]
        for temp in texts:
            result += str(temp)[4:-5] + ' | '
    if result:
        update.message.reply_text(text=str(result[:-3]))
    else:
        update.message.reply_text(text='Посылки с таким номером нет. '
                                       'Проверь, что правильно написал или что она вообще отслеживаемая.')


def generate_item(number):
    game_items = ['Камень', 'Бумага', 'Ножницы']
    if number != 0:
        items = game_items[number - 1]
        return [items, game_items.index(items)]
    items = game_items[random.randint(0, 2)]
    return [items, game_items.index(items)]


def choose_player(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    keyboard_choose_player = [
        [
            InlineKeyboardButton(text='Камень.', callback_data='Rock'),
            InlineKeyboardButton(text='Ножницы.', callback_data='Scissors'),
            InlineKeyboardButton(text='Бумага.', callback_data='Paper')
        ]
    ]
    reply_markup_choose_player = InlineKeyboardMarkup(keyboard_choose_player)
    query.edit_message_text(text="Выбери Камень, Ножницы или Бумагу: ", reply_markup=reply_markup_choose_player)
    return SECOND


def game(update: Update, context: CallbackContext):
    global play_item
    query = update.callback_query
    if query.data == 'Scissors':
        play_item = generate_item(3)
    if query.data == 'Paper':
        play_item = generate_item(2)
    if query.data == 'Rock':
        play_item = generate_item(1)
    item, play_item = generate_item(0), play_item
    query = update.callback_query
    query.answer()
    keyboard_choose = [
        [
            InlineKeyboardButton(text='Да.', callback_data='game'),
            InlineKeyboardButton(text='Нет.', callback_data='Not_Repeat')
        ]
    ]
    reply_mark = InlineKeyboardMarkup(keyboard_choose)
    if play_item[0] == item[0]:
        query.edit_message_text(text=f"{item[0]}\nНичья. Хочешь ещё? ", reply_markup=reply_mark)
        return FIRST
    elif (play_item[1] == 0 and item[1] == 2) or (play_item[1] > item[1] and not (play_item[1] == 2 and item[1] == 0)):
        query.edit_message_text(text=f"{item[0]}\nВыиграл. Хочешь ещё? ", reply_markup=reply_mark)
        return FIRST
    else:
        query.edit_message_text(text=f"{item[0]}\nПроиграл. Хочешь ещё? ", reply_markup=reply_mark)
        return FIRST


def start(update: Update, context: CallbackContext):
    """Отправляет приветсвие с разными кнопками."""
    user = update.message.from_user
    logger.info("User %s started the conversation.", user.first_name)
    update.message.reply_text(text='Выбери, что хочешь: ', reply_markup=reply_markup)
    return FIRST


def start_over(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text='Выбери, что хочешь: ', reply_markup=reply_markup)
    return FIRST


def send_ip(update: Update, context: CallbackContext):
    update.message.reply_text(text=requests.get('https://api.ipify.org/?format=json').json()['ip'] + ':32400')


def huj(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    keyboard_choose = [
        [
            InlineKeyboardButton(text='Да.', callback_data='Huj'),
            InlineKeyboardButton(text='Нет.', callback_data='Not_Repeat')
        ]
    ]
    reply_mark = InlineKeyboardMarkup(keyboard_choose)
    query.edit_message_text(text="Хуй\nЕщё раз надо? ", reply_markup=reply_mark)
    return FIRST


def password(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    keyboard_choose = [
        [
            InlineKeyboardButton(text='Да.', callback_data='password'),
            InlineKeyboardButton(text='Нет.', callback_data='Not_Repeat')
        ]
    ]
    reply_mark = InlineKeyboardMarkup(keyboard_choose)
    query.edit_message_text(text=f"{generate_password()}\nЕщё один нужен? ", reply_markup=reply_mark)
    return FIRST


def help_command(update: Update, context: CallbackContext):
    """Команда /help"""
    update.message.reply_text('Команда /start запускает бота.\nКоманда /help вызывает этот текст.')


def not_recognize(update: Update, context: CallbackContext):
    context.bot.sendMessage(chat_id=update.effective_chat.id,
                            text='Не понял тебя. Можешь нажать /help, чтобы показать доступные команды.')


def send_statistic(update: Update, context: CallbackContext):
    answer = requests.get('https://opendata.digilugu.ee/opendata_covid19_tests_total.json').text.split()[-2].split(',')[
             1:]
    final_output = ''
    for i in range(5):
        if answer[i] == answer[0]:
            final_output += dictionary[i] + answer[i][answer[i].index(':') + 2: -1] + '\n'
            continue
        if answer[i] == answer[-1]:
            final_output += dictionary[i] + answer[i][answer[i].index(':') + 1:-1] + '\n'
            continue
        final_output += dictionary[i] + answer[i][answer[i].index(':') + 1:] + '\n'
    context.bot.sendMessage(chat_id=update.effective_chat.id, text=final_output)


def speech_to_text(update: Update, context: CallbackContext):
    query = update.callback_query
    print(query)


def end(update: Update, context: CallbackContext):
    query = update.callback_query
    print(query)
    query.answer()
    query.edit_message_text(text="Спасибо за уделённое время!")
    return ConversationHandler.END


def main():
    updater = Updater(Token)
    dispatcher = updater.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            FIRST: [
                CallbackQueryHandler(huj, pattern='^' + 'Huj' + '$'),
                CallbackQueryHandler(password, pattern='^' + 'password' + '$'),
                CallbackQueryHandler(choose_player, pattern='^' + 'game' + '$'),
                CallbackQueryHandler(end, pattern='^' + 'end' + '$'),
                CallbackQueryHandler(start_over, pattern='^' + 'Not_Repeat' + '$')
            ],
            SECOND: [
                CallbackQueryHandler(game)
            ]
        },
        fallbacks=[CommandHandler('start', start)]
    )
    dispatcher.add_handler(CommandHandler('Plex', send_ip, Filters.user(470529631)))
    dispatcher.add_handler(CommandHandler('Covid', send_statistic))
    dispatcher.add_handler(CommandHandler('help', help_command))
    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(MessageHandler(Filters.regex('^\w\w\d\d\d\d\d\d\d\d\d\w\w$'), get_respond_delivery))
    dispatcher.add_handler(MessageHandler(Filters.audio, speech_to_text))
    dispatcher.add_handler(MessageHandler(Filters.text, not_recognize))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
