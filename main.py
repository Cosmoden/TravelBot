import logging
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler, ConversationHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from geocode import get_coordinates
from poi_search import find_subcategories, find_poi
from json import load
from translate import en_ru

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)

TOKEN = '5165015893:AAGYCc1P8pRUSmI2iQLGvwbrebjHwyiNvhA'
lat = 0.0
lon = 0.0
r = 0
cont = False
poi_generator = None
with open("categories.json", 'r') as jsonfile:
    categories = load(jsonfile)["poiCategories"]


def start(update, context):
    update.message.reply_text(
        "Привет!\nДавай вместе разнообразим твоё путешествие.\nГде ты находишься? Напиши свой адрес.")
    return 1


def place(update, context):
    global lat, lon
    address = update.message.text
    lon, lat = get_coordinates(address).split()
    update.message.reply_text(
        f"{address}? Отличное место! Укажи радиус поиска в км")
    return 2


def radius(update, context):
    global r
    r = float(update.message.text)
    keyboard = [
        [InlineKeyboardButton("Рестораны и кафе", callback_data='1'),
         InlineKeyboardButton("Достопримечательности", callback_data='2')],
        [InlineKeyboardButton("Шоппинг", callback_data='3'),
         InlineKeyboardButton("Развлечения", callback_data='4')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Что именно тебя интересует?", reply_markup=reply_markup)
    return 3


def category(update, context):
    global lat, lon, r
    query = update.callback_query
    query.answer()
    keyboard = []
    categories_dict = {
        '1': ['7315', '9376'],
        '2': ['7376', '7339'],
        '3': ['9361'],
        '4': ['9927', '7318', '9362']
    }
    subcategories = find_subcategories(categories_dict[query.data], lat, lon, r)
    if not subcategories:
        update.callback_query.message.edit_text("К сожалению, в этой зоне поиска нет подходящих мест.\n"
                                                "Попробуем еще раз? Введи адрес")
        return 1
    for i in range(0, len(subcategories), 2):
        name1 = ""
        id1 = subcategories[i]
        if i + 1 < len(subcategories):
            id2 = subcategories[i + 1]
            name2 = ""
            for cat in categories:
                if cat["id"] == id1:
                    name1 = cat["name"]
                elif cat["id"] == id2:
                    name2 = cat["name"]
            name1 = en_ru(name1).lower().capitalize()
            name2 = en_ru(name2).lower().capitalize()
            keyboard.append([InlineKeyboardButton(name1, callback_data=id1),
                             InlineKeyboardButton(name2, callback_data=id2)])
        else:
            for cat in categories:
                if cat["id"] == id1:
                    name1 = cat["name"]
            name1 = en_ru(name1).lower().capitalize()
            keyboard.append([InlineKeyboardButton(name1, callback_data=id1)])
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.callback_query.message.edit_text("А более точно?", reply_markup=reply_markup)
    return 4


def subcategory(update, context):
    global cont, poi_generator
    query = update.callback_query
    query.answer()
    poi_id = query.data
    cont = True
    poi_generator = find_poi(poi_id, lon, lat, r)
    poi = next(poi_generator)
    keyboard = [
        [InlineKeyboardButton("Дальше", callback_data='1'),
         InlineKeyboardButton("Стоп", callback_data='0')]
    ]
    desc = f"""{poi["name"]} \n
               Телефон: {poi["phone"]} \n
               Сайт: {poi["url"]} \n"""
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.callback_query.message.edit_text(desc, reply_markup=reply_markup)
    return 5


def choice(update, context):
    global cont, poi_generator
    query = update.callback_query
    query.answer()
    cont = bool(int(query.data))
    if not cont:
        update.callback_query.message.edit_text("Хороший выбор!")
        return 1
    poi = next(poi_generator)
    desc = f"""{poi["name"]} \n
                   Телефон: {poi["phone"]} \n
                   Сайт: {poi["url"]} \n"""
    keyboard = [
        [InlineKeyboardButton("Дальше", callback_data='1'),
         InlineKeyboardButton("Стоп", callback_data='0')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.callback_query.message.edit_text(desc, reply_markup=reply_markup)
    return 5


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
            2: [MessageHandler(Filters.text & ~Filters.command, radius)],
            3: [CallbackQueryHandler(category)],
            4: [CallbackQueryHandler(subcategory)],
            5: [CallbackQueryHandler(choice)]
        },
        fallbacks=[CommandHandler('stop', stop)]
    )

    dp.add_handler(conv_handler)
    dp.add_handler(CallbackQueryHandler(category))
    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
