import telebot
import time
import re
from os.path import getsize
import eng
from data.config import bot_token
from data.config import database_name
from telebot import types
from database import SQLighter

bot = telebot.TeleBot(bot_token)
db = SQLighter(database_name)

@bot.message_handler(commands=['start'])
def start(message):
	print(f"start message - {message}")
	message.text = f"Привет. Я простой бот который может скачать\
				твой любимый трек с youtube. Для того чтоб научиться мной\
				пользоваться введи /help."
	bot.send_message(message.chat.id, message.text)

@bot.message_handler(commands=['help'])
def start(message):
	message.text = f"На самом деле все очень просто пока что. Надо всего лишь\
		....отправить мне ссылку на видео из которого ты хочешь достать\
		аудиодорожку и ждать) да, пока что сервис работает не очень\
		быстро, но в дальнейшем разработчик все поправит"
	bot.send_message(message.chat.id, message.text)

@bot.message_handler(commands=['url'])
def get_url(message):
	new_message = message
	new_message.message_id = message.message_id + 1
	download_music(new_message)

@bot.message_handler(commands=['dw'])
def test_method(message):
	keyboard = types.InlineKeyboardMarkup()
	full = types.InlineKeyboardButton(text="Full video?", callback_data=message.text)
	part = types.InlineKeyboardButton(text="Part video?", callback_data="part")
	keyboard.add(full)
	keyboard.add(part)
	bot.send_message(message.chat.id, "test_method", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
	if call.message:
		print(f"call.message - {call.data}\ncall - {call}")
		if call.data == "part":
			keyboard = types.InlineKeyboardMarkup()
			start = types.InlineKeyboardButton(text="start", callback_data=f"start_{call.message.text}")
			finnish = types.InlineKeyboardButton(text="finnish", callback_data=f"fin_{call.message.text}")
			keyboard.add(start)
			keyboard.add(finnish)
			bot.send_message(call.message.chat.id, "don't work)", reply_markup=keyboard)
		url = re.findall(r'https://www.youtube.com/watch\?v\=[0-9A-Za-z\_\-]{11}|https://youtu.be/[0-9A-Za-z\_\-]{11}', call.data)
		if len(url) != 0:
				bot.send_message(call.message.chat.id, "ok")
				download_music(call.message, url)
				time.sleep(3)

#@bot.message_handler(content_types=["text"])
#def get_music(message):
	#download_music(message)
	#time.sleep(3)

def download_music(message, url):
	url_for_download = url[0]
	if db.check_exist_file(url_for_download):
		fileid = db.select_by_url(url_for_download)
		bot.send_audio(message.chat.id, fileid[0], None, timeout = 5)
	else:
		t1 = bot.send_message(message.chat.id, f"0%")
		bot.edit_message_text(f"25%", chat_id=message.chat.id, message_id=t1.message_id)
		fake_name, title = eng.download_by_link(url_for_download, message.chat.id)
		bot.edit_message_text(f"50%", chat_id=message.chat.id, message_id=t1.message_id) 
		path = eng.convert_to_mp3(fake_name, title, None, None)
		size = getsize(path) / 1024 / 1024
		if size > 30:
			bot.edit_message_text(f"Can't load this song.", chat_id=message.chat.id, message_id=t1.message_id)
		else:
			f = open(path, 'rb')
			bot.edit_message_text(f"75%", chat_id=message.chat.id, message_id=t1.message_id)
			try:
				msg = bot.send_audio(message.chat.id, f, None, timeout = 60)
				bot.edit_message_text(f"100%", chat_id=message.chat.id, message_id=t1.message_id)
				db.add_file(file_id=msg.audio.file_id, file_name=path, url=url)
				pass
			except Exception:
				bot.edit_message_text(f"TimeOut.", chat_id=message.chat.id, message_id=t1.message_id)
				pass
			eng.remove_file(path)

if __name__ == '__main__':
	try:
		bot.polling(none_stop = True)
	except Exception as e :
		print(f"bot has been falling {e}")
		time.sleep(5)
