import requests
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram import ReplyKeyboardMarkup
import datetime


def time(update, context):
    update.message.reply_text(str(datetime.datetime.now().time()))


def date(update, context):
    update.message.reply_text(str(datetime.datetime.now().date()))


def anecdote(update, context):
    # TODO: норм url вставить
    response = requests.get("http://127.0.0.2:5000/anecdote")
    if response.status_code != 200:
        update.message.reply_text("Анекдота не будет, БД приняла ислам(ничего не найдено)")
    anec = response.json()["anecdote"]
    update.message.reply_text(f"Название: {anec['name']}    Жанр: {anec['category']}\n"
                              f"Автор: {anec['user.name']}\n"
                              f"{anec['text']}\n"
                              f"Дата создания: {anec['created_date']}\n"
                              f"Рейтинг: {anec['rating']}")


def top(update, context):
    update.message.reply_text(
        "За какой промежуток времени ты хочешь получить топ анекдотов?",
        reply_markup=markup
    )


def day(update, context):
    response = requests.get("http://127.0.0.2:5000/anecdotes/top", json={"period": "day"})
    if response.status_code != 200:
        update.message.reply_text("Топа не будет, БД приняла ислам")

    anecdotes = response.json()["anecdotes"]
    res = "\n\n".join(f"{i[0] + 1}. {i[1].text}" for i in enumerate(anecdotes))
    update.message.reply_text(res)


def week(update, context):
    response = requests.get("http://127.0.0.2:5000/anecdotes/top", json={"period": "week"})
    if response.status_code != 200:
        update.message.reply_text("Топа не будет, БД приняла ислам")

    anecdotes = response.json()["anecdotes"]
    res = "\n\n".join(f"{i[0] + 1}. {i[1].text}" for i in enumerate(anecdotes))
    update.message.reply_text(res)


def month(update, context):
    response = requests.get("http://127.0.0.2:5000/anecdotes/top", json={"period": "month"})
    if response.status_code != 200:
        update.message.reply_text("Топа не будет, БД приняла ислам")

    anecdotes = response.json()["anecdotes"]
    res = "\n\n".join(f"{i[0] + 1}. {i[1].text}" for i in enumerate(anecdotes))
    update.message.reply_text(res)


def year(update, context):
    response = requests.get("http://127.0.0.2:5000/anecdotes/top", json={"period": "year"})
    if response.status_code != 200:
        update.message.reply_text("Топа не будет, БД приняла ислам")

    anecdotes = response.json()["anecdotes"]
    res = "\n\n".join(f"{i[0] + 1}. {i[1].text}" for i in enumerate(anecdotes))
    update.message.reply_text(res)


def all_time(update, context):
    response = requests.get("http://127.0.0.2:5000/anecdotes/top")
    if response.status_code != 200:
        update.message.reply_text("Топа не будет, БД приняла ислам")

    anecdotes = response.json()["anecdotes"]
    res = "\n\n".join(f"{i[0] + 1}. {i[1].text}" for i in enumerate(anecdotes))
    update.message.reply_text(res)


def help(update, context):
    update.message.reply_text("/anecdote - вывод рандомного анекдота\n"
                              "/top - вывод топа анекдотов за определённый промежуток времени")


def main():
    # Вместо слова "TOKEN" надо разместить полученный от @BotFather токен
    updater = Updater(TOKEN, use_context=True)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("anecdote", anecdote))
    dp.add_handler(CommandHandler("top", top))
    dp.add_handler(CommandHandler("day", day))
    dp.add_handler(CommandHandler("week", week))
    dp.add_handler(CommandHandler("month", month))
    dp.add_handler(CommandHandler("year", year))
    dp.add_handler(CommandHandler("all_time", all_time))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    reply_keyboard = [['/all_time', '/year'],
                      ['/month', '/week', '/day']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    main()