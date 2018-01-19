from config import bot_token
from config import database_name
from telebot import types
from database import SQLighter
import telebot
import time
import re
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
    
# @bot.inline_handler(func=lambda query: len(query.query) is 0)
# def empty_query(query):
#     hint = "Введите ссылку на YouTube видео и я достану вам аудиодорожку из него."
#     try:
#         r = types.InlineQueryResultArticle(
#             id='1',
#             description=hint,
#             title='Music_kek_bot',
#             input_message_content=types.InputTextMessageContent(
#             message_text="Могу качать, могу не качать, все сучечка от тебя зависит.")
#         )
#         bot.answer_inline_query(query.id, [r])
#     except Exception as e:
#         print(e)

# @bot.inline_handler(func=lambda query: len(query.query) > 0)
# def query_text(query):
#     url = re.findall('https://www.youtube.com/watch\?v\=[0-9A-Za-z\_\-]{11}|https://youtu.be/[0-9A-Za-z\_\-]{11}',query.query)
#     if len(url) == 0:
#         worse_key = "Не могу скачать по этой ссылке."
#         try:
#             ans = types.InlineQueryResultArticle(
#                 id='1',
#                 title='Music_kek_bot',
#                 description=worse_key,
#                 input_message_content=types.InputTextMessageContent(
#                 message_text="can't download this link")
#             )
#             bot.answer_inline_query(query.id, [ans])
#         except Exception as e:
#             print(e)
#     else:
#         url = query.query
#         if db.check_exist_file(url):
#             fileid = db.select_by_url(url)
#             try:
#                 ans = types.InlineQueryResultCachedAudio(
#                     id='1',
#                     audio_file_id=fileid[0],
#                 )
#                 bot.answer_inline_query(query.id, [ans],cache_time=2147483646)
#             except Exception as e:
#                 print(e)
#         else:
#             print(query.id)
#             didnt_download = 'У меня нет такого файла, для того чтоб это исправить пишите в личку мне @Music_kek_bot.'
#             try:
#                 ans = types.InlineQueryResultArticle(
#                     id='1',
#                     description=didnt_download,
#                     title='Music_kek_bot',
#                     input_message_content=types.InputTextMessageContent(
#                     message_text=didnt_download)
#                 )
#                 bot.answer_inline_query(query.id, [ans])
#             except Exception as e:
#                 print(e)


@bot.message_handler(content_types=["text"])
def get_music(message):
    i = 2
    url = re.findall('https://www.youtube.com/watch\?v\=[0-9A-Za-z\_\-]{11}|https://youtu.be/[0-9A-Za-z\_\-]{11}',message.text)
    if len(url) == 0:
        message.text = 'Умею только в Ютуб.'
        bot.send_message(message.chat.id, message.text)
    else:
        url = message.text
        if db.check_exist_file(url):
            fileid = db.select_by_url(url)
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
                bot.edit_message_text('Слишком большой файл!',chat_id=message.chat.id,message_id=t1.message_id)
                pass
            eng.remove_file(path)
    time.sleep(3)

if __name__ == '__main__':
    bot.polling(none_stop=True)

