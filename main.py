import logging
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler, ConversationHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from geocode import get_coordinates
from poi_search import find_subcategories, find_poi
from json import load
from translate import en_ru
from org_search import info
from data import db_session
from data.places import Place

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
poi = ""
with open("categories.json", 'r') as jsonfile:
    categories = load(jsonfile)["poiCategories"]


def start(update, context):
    update.message.reply_text(
        "Привет!\nДавай вместе разнообразим твоё путешествие.\nГде ты находишься? Напиши свой адрес.")
    return 1


def location(update, context):
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
    update.message.reply_text("Начнем подбор мест. Что именно тебя интересует?", reply_markup=reply_markup)
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
    global cont, poi_generator, poi
    query = update.callback_query
    query.answer()
    poi_id = query.data
    cont = True
    poi_generator = find_poi(poi_id, lon, lat, r)
    poi = next(poi_generator)
    poi_info = info(poi["name"], lon, lat, r)
    desc = f"""{poi_info[0]}\n
    {poi_info[1]}
    Телефон: {poi_info[2]}
    Часы работы: {poi_info[3]}
    {poi_info[4]}
    Посмотреть на карте: {poi_info[5]}"""
    keyboard = [
        [InlineKeyboardButton("Дальше", callback_data='1'),
         InlineKeyboardButton("Стоп", callback_data='0')],
        [InlineKeyboardButton("Сохранить в закладки", callback_data='2'),
         InlineKeyboardButton("Посмотреть закладки", callback_data='3')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.callback_query.message.edit_text(desc, reply_markup=reply_markup)
    return 5


def choice(update, context):
    global cont, poi_generator, poi
    query = update.callback_query
    query.answer()
    cont = bool(int(query.data))
    if query.data == '2':
        db_sess = db_session.create_session()
        place_info = info(poi["name"], lon, lat, r)
        keyboard = [
            [InlineKeyboardButton("Дальше", callback_data='1'),
             InlineKeyboardButton("Стоп", callback_data='0')],
            [InlineKeyboardButton("Сохранить в закладки", callback_data='2'),
             InlineKeyboardButton("Посмотреть закладки", callback_data='3')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        if db_sess.query(Place).filter(Place.name == place_info[0]):
            update.callback_query.message.edit_text("Место уже в закладках", reply_markup=reply_markup)
            return 5
        place = Place()
        place.name = place_info[0]
        place.description = place_info[1]
        place.phone = place_info[2]
        place.opening_hours = place_info[3]
        place.website = place_info[4]
        place.map_link = place_info[5]
        db_sess.add(place)
        db_sess.commit()
        update.callback_query.message.edit_text("Место добавлено в закладки", reply_markup=reply_markup)
        return 5
    if query.data == '3':
        db_sess = db_session.create_session()
        text = ""
        for place in db_sess.query(Place).all():
            desc = f"""{place.name}\n
            {place.description}
            Телефон: {place.phone}
            Часы работы: {place.opening_hours}
            {place.website}
            Посмотреть на карте: {place.map_link}"""
            text += desc + '\n\n'
        keyboard = [
            [InlineKeyboardButton("Дальше", callback_data='1'),
             InlineKeyboardButton("Стоп", callback_data='0')],
            [InlineKeyboardButton("Сохранить в закладки", callback_data='2'),
             InlineKeyboardButton("Посмотреть закладки", callback_data='3')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        if not text:
            text = "Закладок пока нет"
        update.callback_query.message.edit_text(text, reply_markup=reply_markup)
        return 5
    if not cont:
        poi_info = info(poi["name"], lon, lat, r)
        desc = f"""{poi_info[0]}\n
        {poi_info[1]}
        Телефон: {poi_info[2]}
        Часы работы: {poi_info[3]}
        {poi_info[4]}
        Посмотреть на карте: {poi_info[5]}"""
        update.callback_query.message.edit_text(desc + '\n' + "Хороший выбор!")
        return ConversationHandler.END
    poi = next(poi_generator)
    poi_info = info(poi["name"], lon, lat, r)
    desc = f"""{poi_info[0]}\n
    {poi_info[1]}
    Телефон: {poi_info[2]}
    Часы работы: {poi_info[3]}
    {poi_info[4]}
    Посмотреть на карте: {poi_info[5]}"""
    keyboard = [
        [InlineKeyboardButton("Дальше", callback_data='1'),
         InlineKeyboardButton("Стоп", callback_data='0')],
        [InlineKeyboardButton("Сохранить в закладки", callback_data='2'),
         InlineKeyboardButton("Посмотреть закладки", callback_data='3')]
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
            1: [MessageHandler(Filters.text & ~Filters.command, location)],
            2: [MessageHandler(Filters.text & ~Filters.command, radius)],
            3: [CallbackQueryHandler(category)],
            4: [CallbackQueryHandler(subcategory)],
            5: [CallbackQueryHandler(choice)]
        },
        fallbacks=[CommandHandler('stop', stop)]
    )

    dp.add_handler(conv_handler)
    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    db_session.global_init("db/places.db")
    db_sess = db_session.create_session()
    db_sess.query(Place).delete()
    db_sess.commit()
    main()
