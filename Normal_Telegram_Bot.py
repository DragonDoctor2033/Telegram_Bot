import logging
import random
import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, ConversationHandler, \
    MessageHandler, Filters

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

FIRST, SECOND, THREE = range(3)



def generate_password():
    words_text = open('enlist_words.txt', 'r')
    words_list, symbols, a = words_text.read().split(), '-+=*_.,:;', ''
    words_text.close()
    random_symbol = random.choice(symbols)
    for _ in range(4):
        if random.randint(0, 1) == 1:
            a += random.choice(words_list) + random_symbol
        else:
            a += random.choice(words_list).upper() + random_symbol
    return a + str(random.randrange(1000, 10000))


def get_ip():
    response = requests.get('https://api.ipify.org/?format=json')
    return response.json()['ip']


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
    keyboard = [
        [
            InlineKeyboardButton(text='Камень.', callback_data='Rock'),
            InlineKeyboardButton(text='Ножницы.', callback_data='Scissors'),
            InlineKeyboardButton(text='Бумага.', callback_data='Paper')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="Выбери Камень, Ножницы или Бумагу: ", reply_markup=reply_markup)
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
    item,  play_item = generate_item(0), play_item
    query = update.callback_query
    query.answer()
    keyboard_choose = [
        [
            InlineKeyboardButton(text='Да.', callback_data='Y'),
            InlineKeyboardButton(text='Нет.', callback_data='N')
        ]
    ]
    reply_mark = InlineKeyboardMarkup(keyboard_choose)
    if play_item[0] == item[0]:
        query.edit_message_text(text=f"{item[0]}\nНичья. Хочешь ещё? ", reply_markup=reply_mark)
        return THREE
    elif (play_item[1] == 0 and item[1] == 2) or (play_item[1] > item[1] and not (play_item[1] == 2 and item[1] == 0)):
        query.edit_message_text(text=f"{item[0]}\nВыиграл. Хочешь ещё? ", reply_markup=reply_mark)
        return THREE
    else:
        query.edit_message_text(text=f"{item[0]}\nПроиграл. Хочешь ещё? ", reply_markup=reply_mark)
        return THREE


def start(update: Update, context: CallbackContext):
    """Отправляет приветсвие с разными кнопками."""
    user = update.message.from_user
    logger.info("User %s started the conversation.", user.first_name)
    keyboard = [
        [
            InlineKeyboardButton(text='Get_iP.', callback_data='Get_iP'),
            InlineKeyboardButton(text='Узнай.', callback_data='Huj'),
            InlineKeyboardButton(text='Пароль.', callback_data='password')
        ],
        [
            InlineKeyboardButton(text='Wanna Play? ', callback_data='game')
        ],
        [
            InlineKeyboardButton(text='Исходный кот этого бота.', url='')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(text='Выбери, что хочешь: ', reply_markup=reply_markup)
    return FIRST


def send_ip(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.edit_message_text(get_ip())  # Шлёт айпишник


def huj(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.edit_message_text('Хуй')  # Не поверишь


def password(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.edit_message_text(generate_password())  # Генерирует и шлёт пароль


def help_command(update: Update, context: CallbackContext):
    """Комманда /help"""
    update.message.reply_text('У Бота имеются разные функции. Тыры-пыры *расписать*')


def end(update: Update, context: CallbackContext):
    """Returns `ConversationHandler.END`, which tells the
    ConversationHandler that the conversation is over.
    """
    query = update.callback_query
    query.answer()
    query.edit_message_text(text="Спасибо за игру. До скорого!")
    return ConversationHandler.END


def not_recognize(update: Update, context: CallbackContext):
    context.bot.sendMessage(chat_id=update.effective_chat.id,
                            text='Не понял тебя. Можешь нажать /help, чтобы показать доступные команды')


def main():
    updater = Updater("Your_Token_Here")
    dispatcher = updater.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            FIRST: [
                CallbackQueryHandler(send_ip, pattern='^' + 'Get_iP' + '$'),
                CallbackQueryHandler(huj, pattern='^' + 'Huj' + '$'),
                CallbackQueryHandler(password, pattern='^' + 'password' + '$'),
                CallbackQueryHandler(choose_player, pattern='^' + 'game' + '$')
            ],
            SECOND: [
                CallbackQueryHandler(game)
            ],
            THREE: [
                CallbackQueryHandler(end, pattern='^' + 'N' + '$'),
                CallbackQueryHandler(choose_player, pattern='^' + 'Y' + '$'),
            ]
        },
        fallbacks=[CommandHandler('start', start)]
    )
    dispatcher.add_handler(CommandHandler('help', help_command))
    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(MessageHandler(Filters.text, not_recognize))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
