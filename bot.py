# -*- coding: utf-8 -*-
from config import bot_token
import telebot
import time
import re
from eng import download_by_link
from eng import convert_to_mp3

bot = telebot.TeleBot(bot_token)
@bot.message_handler(commands=['start'])
def start(message):
    message.text = 'Привет. Я простой бот который может скачать твой любимый трек с youtube. Для того чтоб научиться мной пользоваться \
        введи /help.'
    bot.send_message(message.chat.id, message.text)

@bot.message_handler(commands=['help'])
def start(message):
    message.text = "На самом деле все очень просто пока что. Надо всего лишь.... отпавить мне ссылку на видео из которого ты хочешь достать \
        аудиодорожку и ждать) да, пока что сервис работает не очень быстро но в дальнейшем разработчик все поправит"
    bot.send_message(message.chat.id, message.text)

@bot.message_handler(content_types=["text"])
def get_music(message):
    name = re.findall('https://www.youtube.com/watch?v=[a-zA-Z0-9-_()]',message.text)
    print(name, message.text)
    if len(name) == 0:
        message.text = "can't download in this url"
        bot.send_message(message.chat.id,message.text)
    else:
        url = message.text
        fake_name, title = download_by_link(url,message.chat.id)
        path = convert_to_mp3(fake_name, title)
        f = open(path, 'rb')
        msg = bot.send_audio(message.chat.id, f, None, timeout=20)
        bot.send_message(message.chat.id, msg.audio.file_id)
    time.sleep(3)

if __name__ == '__main__':
    bot.polling(none_stop=True)