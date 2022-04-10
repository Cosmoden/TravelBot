import logging
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler, ConversationHandler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)

TOKEN = '5165015893:AAGYCc1P8pRUSmI2iQLGvwbrebjHwyiNvhA'


def start(update, context):
    update.message.reply_text(
        "Привет!\nДавай вместе разнообразим твоё путешествие.\nКуда планируешь поехать? Напиши название города.")
    return 1


def what(update, context):
    locality = update.message.text
    update.message.reply_text(
        f"{locality}? Хороший выбор!\nА что ты хочешь посмотреть?")
    return 2


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
            1: [MessageHandler(Filters.text & ~Filters.command, what)],
            2: [MessageHandler(Filters.text & ~Filters.command, result)]
        },
        fallbacks=[CommandHandler('stop', stop)]
    )

    dp.add_handler(conv_handler)
    dp.add_handler(conv_handler)
    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
