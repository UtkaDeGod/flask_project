import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler


PERIODS = ["all_time", "year", "month", "week", "day"]


def anecdote(update, context):
    response = requests.get("http://rzhomba-rf.herokuapp.com/api/anecdote")
    if response.status_code != 200:
        update.message.reply_text("Анекдота не будет, БД приняла ислам(ничего не найдено)")
        return
    anec = response.json()["anecdote"]
    update.message.reply_text(f"Название: {anec['name']}    Жанр: {anec['category']}\n"
                              f"Автор: {anec['user.name']}\n"
                              f"{anec['text']}\n"
                              f"Дата создания: {anec['created_date']}\n"
                              f"Рейтинг: {anec['rating']}")


def top(update, context):
    keyboard = [
        [
            InlineKeyboardButton("all_time", callback_data='0'),
            InlineKeyboardButton("year", callback_data='1'),
        ],
        [InlineKeyboardButton("month", callback_data='2'),
         InlineKeyboardButton("week", callback_data='3'),
         InlineKeyboardButton("day", callback_data='4')],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard, one_time_keyboard=True)
    update.message.reply_text(
        "За какой промежуток времени вы хотите получить топ анекдотов?",
        reply_markup=reply_markup
    )


def top_request(update, context):
    query = update.callback_query
    query.answer()
    if not query.data:
        response = requests.get("http://rzhomba-rf.herokuapp.com/api/anecdotes/top")
    else:
        response = requests.get("http://rzhomba-rf.herokuapp.com/api/anecdotes/top",
                                json={"period": PERIODS[int(query.data)]})
    if response.status_code != 200:
        query.edit_message_text(text="Топа не будет, БД приняла ислам")
        return
    anecdotes = response.json()["anecdotes"]
    res = "\n\n".join(f"{i[0] + 1}. {i[1].text}" for i in enumerate(anecdotes))
    query.edit_message_text(text=f"{res}")


def help(update, context):
    update.message.reply_text("/anecdote - вывод рандомного анекдота\n"
                              "/top - вывод топа анекдотов за определённый промежуток времени")


def main():
    # Вместо слова "TOKEN" надо разместить полученный от @BotFather токен
    updater = Updater('TOKEN', use_context=True)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("anecdote", anecdote))
    dp.add_handler(CommandHandler("top", top))
    updater.dispatcher.add_handler(CallbackQueryHandler(top_request))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
