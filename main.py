import logging
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler, ConversationHandler, CallbackQueryHandler
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
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
    global lat, lon, ch_id
    ch_id = update.message.from_user.id
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
         InlineKeyboardButton("Развлечения", callback_data='4')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        f"{locality}? Красивое место! Что именно тебя интересует?", reply_markup=reply_markup)
    return 2


def button(update, context):
    query = update.callback_query
    query.answer()
    keyboard = []
    match query.data:
        case '1':
            keyboard = [
                [InlineKeyboardButton("Бары", callback_data='bar'),
                 InlineKeyboardButton("Барбекью", callback_data='barbecue')],
                [InlineKeyboardButton("Бистро", callback_data='bistro'),
                 InlineKeyboardButton("Русская кухня", callback_data='russian')],
                [InlineKeyboardButton("Фаст-фуд", callback_data='fast food'),
                 InlineKeyboardButton("Итальянская кухня", callback_data='italian')]
            ]
        case '2':
            keyboard = [
                [InlineKeyboardButton("Амфитеатры", callback_data='amphitheater'),
                 InlineKeyboardButton("Музеи", callback_data='museum')],
                [InlineKeyboardButton("Выставочные комплексы", callback_data='exhibition convention center'),
                 InlineKeyboardButton("Памятники", callback_data='monument')]
            ]
        case '3':
            keyboard = [
                [InlineKeyboardButton("Сувениры", callback_data='gifts, cards, novelties souvenirs'),
                 InlineKeyboardButton("Салоны красоты", callback_data='beauty salon')],
                [InlineKeyboardButton("Мужская одежда", callback_data='clothing accessories: men'),
                 InlineKeyboardButton("Женская одежда", callback_data='clothing accessories: women')]
            ]
        case '4':
            keyboard = [
                [InlineKeyboardButton("Амфитеатры", callback_data='amphitheater'),
                 InlineKeyboardButton("Игровые автоматы", callback_data='amusement arcade')],
                [InlineKeyboardButton("Парки развлечений", callback_data='amusement park'),
                 InlineKeyboardButton("Ботанические сады", callback_data='arboreta botanical gardens')],
                [InlineKeyboardButton("Воздушные шары", callback_data='balloonport'),
                 InlineKeyboardButton("Пляжи", callback_data='beach')],
                [InlineKeyboardButton("Боулинг", callback_data='bowling'),
                 InlineKeyboardButton("Пляжи", callback_data='beach')]
            ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.callback_query.message.edit_text("А более точно?", reply_markup=reply_markup)
    query2 = update.callback_query
    query2.answer()
    poi_type = query2.data
    flag = True
    while flag:
        keyboard = [
            [InlineKeyboardButton("Дальше", callback_data='True'),
             InlineKeyboardButton("Стоп", callback_data='False')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        img = ''
        message = ''
        context.bot.send_photo(update.message.chat_id, img, caption=message, reply_markup=reply_markup)
        query3 = update.callback_query
        query3.answer()
        flag = query2.data


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
            2: [MessageHandler(Filters.text & ~Filters.command, button)]
        },
        fallbacks=[CommandHandler('stop', stop)]
    )

    dp.add_handler(conv_handler)
    dp.add_handler(CallbackQueryHandler(button))
    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
