from config import bot_token
from config import database_name
import telebot
import time
import re
from database import SQLighter
import eng

bot = telebot.TeleBot(bot_token)
db = SQLighter(database_name)

@bot.message_handler(commands=['start'])
def start(message):
    message.text = 'Привет. Я простой бот который может скачать твой любимый трек с youtube. Для того чтоб научиться мной пользоваться \
        введи /help.'
    bot.send_message(message.chat.id, message.text)

@bot.message_handler(commands=['help'])
def start(message):
    message.text = "На самом деле все очень просто пока что. Надо всего лишь.... отправить мне ссылку на видео из которого ты хочешь достать \
        аудиодорожку и ждать) да, пока что сервис работает не очень быстро, но в дальнейшем разработчик все поправит"
    bot.send_message(message.chat.id, message.text)

@bot.message_handler(content_types=["text"])
def get_music(message):
    i = 2
    name = re.findall('https://www.youtube.com/watch\?v\=|https://youtu.be/',message.text)
    print(name, message.text)
    if len(name) == 0:
        message.text = "can't download in this url"
        bot.send_message(message.chat.id, message.text)
    else:
        url = message.text
        if db.check_exist_file(url):
            fileid = db.select_by_url(url)
            print(fileid)
            bot.send_audio(message.chat.id, fileid[0], None, timeout=5)
        else:
            t1 = bot.send_message(message.chat.id, '0%')
            bot.edit_message_text("25%",chat_id=message.chat.id,message_id=t1.message_id)
            fake_name, title = eng.download_by_link(url,message.chat.id)
            bot.edit_message_text("50%",chat_id=message.chat.id,message_id=t1.message_id) 
            path = eng.convert_to_mp3(fake_name, title)
            f = open(path, 'rb')
            bot.edit_message_text("75%",chat_id=message.chat.id,message_id=t1.message_id)
            try:
                msg = bot.send_audio(message.chat.id, f, None, timeout=60)
                bot.edit_message_text("100%",chat_id=message.chat.id,message_id=t1.message_id)
                db.add_file(file_id=msg.audio.file_id, file_name="0", url=url)
                pass
            except Exception:
                bot.edit_message_text("Can't load file. SUCH BIG, VERY FILE!!!",chat_id=message.chat.id,message_id=t1.message_id)
                pass
            eng.remove_file(path)
    time.sleep(3)

if __name__ == '__main__':
    bot.polling(none_stop=True)
