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

@bot.message_handler(content_types=["text"])
def get_music(message):
	print(f"message - {message}")
	start_time = 0
	end_time = 0
	url = re.findall(r'https://www.youtube.com/watch\?v\=[0-9A-Za-z\_\-]{11}|https://youtu.be/[0-9A-Za-z\_\-]{11}', message.text)
	if len(url) == 0:
		message.text = f"Only youtube URLs."
		bot.send_message(message.chat.id, message.text)
	else:
		start = re.findall(r'\s(-старт|-с|-start|-s)\s(\d{1,2}\.\d{1,2}|\d{1,2})', message.text)
		finish = re.findall(r'\s(-конец|-к|-end|-e)\s(\d{1,2}\.\d{1,2}|\d{1,2})', message.text)
		if len(start) != 0:
			try:
				if start[0][1].find('.') == -1:
					start_time: int = int(start[1])    
				else:
					parsed_time = start[0][1].split('.')
					start_time = int(parsed_time[0]) * 60 + int(parsed_time[1])
			except IndexError:
				message.text = f"Error in arguments."
				bot.send_message(message.chat.id, message.text)
		else:
			start_time = None
		if len(finish) != 0:
			try:
				if finish[0][1].find('.') == -1:
					end_time: int = int(finish[0][1])
				else:
					parsed_time = finish[0][1].split('.')
					end_time = int(parsed_time[0]) * 60 + int(parsed_time[1])
			except IndexError:
				message.text = f"Error in arguments."
				bot.send_message(message.chat.id, message.text)
		else:
			end_time = None
		print(f"parsed args - start_time {start_time} end_time {end_time}")
		url = message.text
		if db.check_exist_file(url):
			fileid = db.select_by_url(url)
			bot.send_audio(message.chat.id, fileid[0], None, timeout = 5)
		else:
			t1 = bot.send_message(message.chat.id, f"0%")
			bot.edit_message_text(f"25%", chat_id=message.chat.id, message_id=t1.message_id)
			fake_name, title = eng.download_by_link(url, message.chat.id)
			bot.edit_message_text(f"50%", chat_id=message.chat.id, message_id=t1.message_id) 
			path = eng.convert_to_mp3(fake_name, title, start_time, end_time)
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
	time.sleep(3)

if __name__ == '__main__':
	while True:
		try:
			bot.polling(none_stop = True)
		except Exception:
			print(f"bot has been falling")
			time.sleep(5)
