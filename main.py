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
from weather import current_weather, forecast
from airlines import get_flights

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)

TOKEN = '5165015893:AAGYCc1P8pRUSmI2iQLGvwbrebjHwyiNvhA'
with open("categories.json", 'r') as jsonfile:
    categories = load(jsonfile)["poiCategories"]


def start(update, context):
    context.bot.send_photo(update.message.chat_id,
                           "https://s.inyourpocket.com/img/figure/2019-10/mariacki_old-square_adobestock_rh2010.jpeg",
                           caption="Привет!\nДавай вместе разнообразим твоё путешествие.\n")
    update.message.reply_text(
        "Куда ты хочешь поехать? Напиши адрес, начиная с города")
    return 1


def location(update, context):
    context.user_data["address"] = update.message.text
    context.user_data["lon"], context.user_data["lat"] = get_coordinates(
        context.user_data["address"]).split()
    keyboard = [
        [InlineKeyboardButton("Найти интересные места", callback_data='1'),
         InlineKeyboardButton("Посмотреть погоду", callback_data='2')],
        [InlineKeyboardButton("Информация о авиарейсах", callback_data='3')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        "Отличное место! Что тебя интересует?", reply_markup=reply_markup)
    return 2


def menu(update, context):
    query = update.callback_query
    query.answer()
    if query.data == '1':
        update.callback_query.message.edit_text("Напиши радиус поиска в км")
        return 3
    if query.data == '2':
        keyboard = [
            [InlineKeyboardButton("Погода в данный момент", callback_data='1'),
             InlineKeyboardButton("Погода на ближайшие 7 дней", callback_data='2')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.callback_query.message.edit_text(
            "Какая информация о погоде тебе нужна?", reply_markup=reply_markup)
        return 7
    if query.data == '3':
        update.callback_query.message.edit_text("Введи город отправления и дату вылета (в формате"
                                                " 'гггг-мм-чч') через пробел. "
                                                "Обязательно соблюди формат даты!")
        return 8


def radius(update, context):
    context.user_data["r"] = float(update.message.text)
    keyboard = [
        [InlineKeyboardButton("Рестораны и кафе", callback_data='1'),
         InlineKeyboardButton("Достопримечательности", callback_data='2')],
        [InlineKeyboardButton("Шоппинг", callback_data='3'),
         InlineKeyboardButton("Развлечения", callback_data='4')],
        [InlineKeyboardButton("Отели и гостиницы", callback_data='5'),
         InlineKeyboardButton("Аэропорты и вокзалы", callback_data='6')],
        [InlineKeyboardButton("Заправки", callback_data='7'),
         InlineKeyboardButton("Паркинги", callback_data='8')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Начнем подбор мест. Что именно тебя интересует?",
                              reply_markup=reply_markup)
    return 4


def category(update, context):
    query = update.callback_query
    query.answer()
    keyboard = []
    categories_dict = {
        '1': ['7315', '9376'],
        '2': ['7376', '7339'],
        '3': ['9361'],
        '4': ['9927', '7318', '9362'],
        '5': ['7314'],
        '6': ['7380', '7383', '7389'],
        '7': ['7309', '7311'],
        '8': ['7369', '7313']
    }
    subcategories = find_subcategories(categories_dict[query.data], context.user_data["lat"], context.user_data["lon"],
                                       context.user_data["r"])
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
    update.callback_query.message.edit_text(
        "А более точно?", reply_markup=reply_markup)
    return 5


def subcategory(update, context):
    query = update.callback_query
    query.answer()
    poi_id = query.data
    context.user_data["cont"] = True
    context.user_data["poi_generator"] = find_poi(poi_id, context.user_data["lon"], context.user_data["lat"],
                                                  context.user_data["r"])
    context.user_data["poi"] = next(context.user_data["poi_generator"])
    poi_info = info(context.user_data["poi"]["name"], context.user_data["lon"], context.user_data["lat"],
                    context.user_data["r"])
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
    return 6


def choice(update, context):
    query = update.callback_query
    query.answer()
    context.user_data["cont"] = bool(int(query.data))
    if query.data == '2':
        db_sess = db_session.create_session()
        place_info = info(context.user_data["poi"]["name"], context.user_data["lon"], context.user_data["lat"],
                          context.user_data["r"])
        keyboard = [
            [InlineKeyboardButton("Дальше", callback_data='1'),
             InlineKeyboardButton("Стоп", callback_data='0')],
            [InlineKeyboardButton("Сохранить в закладки", callback_data='2'),
             InlineKeyboardButton("Посмотреть закладки", callback_data='3')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        if db_sess.query(Place).filter(Place.name == place_info[0]).first():
            update.callback_query.message.edit_text(
                "Место уже в закладках", reply_markup=reply_markup)
            return 6
        place = Place()
        place.name = place_info[0]
        place.description = place_info[1]
        place.phone = place_info[2]
        place.opening_hours = place_info[3]
        place.website = place_info[4]
        place.map_link = place_info[5]
        db_sess.add(place)
        db_sess.commit()
        update.callback_query.message.edit_text(
            "Место добавлено в закладки", reply_markup=reply_markup)
        return 6
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
        update.callback_query.message.edit_text(
            text, reply_markup=reply_markup)
        return 6
    if not context.user_data["cont"]:
        poi_info = info(context.user_data["poi"]["name"], context.user_data["lon"], context.user_data["lat"],
                        context.user_data["r"])
        desc = f"""{poi_info[0]}\n
        {poi_info[1]}
        Телефон: {poi_info[2]}
        Часы работы: {poi_info[3]}
        {poi_info[4]}
        Посмотреть на карте: {poi_info[5]}"""
        keyboard = [
            [InlineKeyboardButton("Найти интересные места", callback_data='1'),
             InlineKeyboardButton("Посмотреть погоду", callback_data='2')],
            [InlineKeyboardButton(
                "Информация о авиарейсах", callback_data='3')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.callback_query.message.edit_text(
            desc + '\n' + "Хороший выбор!", reply_markup=reply_markup)
        return 2
    context.user_data["poi"] = next(context.user_data["poi_generator"])
    poi_info = info(context.user_data["poi"]["name"], context.user_data["lon"], context.user_data["lat"],
                    context.user_data["r"])
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
    return 6


def weather(update, context):
    query = update.callback_query
    query.answer()
    data = ""
    if query.data == '1':
        data = current_weather(
            context.user_data["lon"], context.user_data["lat"])
    elif query.data == '2':
        data = forecast(context.user_data["lon"], context.user_data["lat"])
    keyboard = [
        [InlineKeyboardButton("Найти интересные места", callback_data='1'),
         InlineKeyboardButton("Посмотреть погоду", callback_data='2')],
        [InlineKeyboardButton("Информация о авиарейсах", callback_data='3')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.callback_query.message.edit_text(data, reply_markup=reply_markup)
    return 2


def flights(update, context):
    flight_info = update.message.text
    city = flight_info[:-10]
    date = flight_info[-10:]
    text = get_flights(city, context.user_data["address"].split(', ')[0], date)
    keyboard = [
        [InlineKeyboardButton("Найти интересные места", callback_data='1'),
         InlineKeyboardButton("Посмотреть погоду", callback_data='2')],
        [InlineKeyboardButton("Информация о авиарейсах", callback_data='3')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(text, reply_markup=reply_markup)
    return 2


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
            2: [CallbackQueryHandler(menu)],
            3: [MessageHandler(Filters.text & ~Filters.command, radius)],
            4: [CallbackQueryHandler(category)],
            5: [CallbackQueryHandler(subcategory)],
            6: [CallbackQueryHandler(choice)],
            7: [CallbackQueryHandler(weather)],
            8: [MessageHandler(Filters.text & ~Filters.command, flights)]
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
