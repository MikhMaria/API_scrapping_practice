import requests
from bs4 import BeautifulSoup

import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

import random

from task4_1 import message

bot = telebot.TeleBot('')
url = 'https:h//um.spbstu.ru/news/practice_vshlip/'


class News:
  def __init__(self, title, pictures):
    self.title = title
    self.pictures = pictures

@bot.message_handler(commands=["start","help"])
def help(message: telebot.types.Message):
    bot.reply_to(message, "Привет! Хочешь вывести заголовок и изображения из новости?", reply_markup = user_reply_button(message))
    bot.register_next_step_handler(message, user_reply, answer = None)


def user_reply_button(message):
    markup = InlineKeyboardMarkup()
    button_yes = InlineKeyboardButton("Да", callback_data="yes")
    button_no = InlineKeyboardButton("Нет", callback_data="no")
    markup.add(button_yes, button_no)
    return markup

def random_image_button():
    markup = InlineKeyboardMarkup()
    random_yes = InlineKeyboardButton("Хочу", callback_data="random_yes")
    random_no = InlineKeyboardButton("Не хочу", callback_data="random_no")
    markup.add(random_yes, random_no)
    return markup


def user_reply(message,answer):
    bot.reply_to(message, "Отлично! Спасибо за ответ.", reply_markup=user_reply_button(message))
    if message.text == "Да":
        answer = message.text
        bot.reply_to(message, "Сейчас выведем на экран.")
        bot.register_next_step_handler(message, lambda msg: callback_inline(msg, call = None))
    elif message.text == "Нет":
        bot.send_message(message, "Ок. Если понадобимся - обращайтесь.")
    else:
        bot.reply_to(message, "Пожалуйста, выберите ответ из предложенных вариантов.")
        bot.register_next_step_handler(message, lambda msg: user_reply(msg, answer))


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.data == "yes":
        all_pictures = []
        data = requests.get(url)
        page = BeautifulSoup(data.content, 'html.parser')
        title = page.find(attrs={'class': 'media-page__heading'}).text
        main_picture = page.find(attrs={'class': 'media-page__cover'})
        pictures = page.find_all(attrs={'class': 'img-fw'})
        bot.send_message(call.message.chat.id, f"Заголовок: {title}.")
        bot.send_photo(call.message.chat.id, main_picture['src'])
        all_pictures.append(main_picture['src'])
        for picture in pictures:
            picture_src = picture['src']
            all_pictures.append(picture_src)
            bot.send_photo(call.message.chat.id, picture_src)

        bot_data[call.message.chat.id] = all_pictures

        bot.send_message(call.message.chat.id, 'Хотите рандомную картинку с сайта?', reply_markup=random_image_button())

    elif call.data == "no":
        bot.send_message(call.message.chat.id, 'Ок. Если что - обращайтесь.')

    elif call.data == "random_yes":
        if call.message.chat.id in bot_data and bot_data[call.message.chat.id]:
            random_picture = random.choice(bot_data[call.message.chat.id])
            bot.send_photo(call.message.chat.id, random_picture)
    elif call.data == "random_no":
        bot.send_message(call.message.chat.id, 'Ну и не нужно. Пока.')


bot_data = {}
bot.polling()
