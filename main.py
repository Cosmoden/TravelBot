import logging
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler, ConversationHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from requests import get

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)

TOKEN = '5165015893:AAGYCc1P8pRUSmI2iQLGvwbrebjHwyiNvhA'
global lat, lon


def start(update, context):
    update.message.reply_text(
        "Привет!\nДавай вместе разнообразим твоё путешествие.\nКуда планируешь поехать? Напиши название города.")
    return 1


def place(update, context):
    global lat, lon
    locality = update.message.text
    request = f"https://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode={locality}&format=json"
    response = get(request)
    json_response = response.json()
    toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
    toponym_coordinates = toponym["Point"]["pos"]
    lat, lon = toponym_coordinates.split()
    keyboard = [
        [InlineKeyboardButton("Рестораны и кафе", callback_data='1'),
         InlineKeyboardButton("Достопримечательности", callback_data='2')],
        [InlineKeyboardButton("Шоппинг", callback_data='3'),
         InlineKeyboardButton("Развлекательные заведения", callback_data='4')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(f"{locality}? Красивое место! Что именно тебя интересует?", reply_markup=reply_markup)
    return 2


def button(update, context):
    query = update.callback_query
    query.answer()
    match query.data:
        case '1':
            search_food()
        case '2':
            search_sights()
        case '3':
            search_shopping()
        case '4':
            search_entertainment()


def search_food():
    pass


def search_sights():
    pass


def search_shopping():
    pass


def search_entertainment():
    pass


def result(update, context):
    # надо настроить вывод результата

    return ConversationHandler.END


def stop(update, context):
    update.message.reply_text("Удачного путешествия!")
    return ConversationHandler.END


def main():
    updater = Updater(TOKEN)

    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            1: [MessageHandler(Filters.text & ~Filters.command, place)],
            2: [MessageHandler(Filters.text & ~Filters.command, search)],
            3: [MessageHandler(Filters.text & ~Filters.command, result)]
        },
        fallbacks=[CommandHandler('stop', stop)]
    )

    dp.add_handler(conv_handler)
    dp.add_handler(CallbackQueryHandler(button))
    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
