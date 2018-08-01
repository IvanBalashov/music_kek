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
valid_url = r'https://www.youtube.com/watch\?v\=[0-9A-Za-z\_\-]{11}|https://youtu.be/[0-9A-Za-z\_\-]{11}'
start_fin = r'(\d{1,2}\.\d{1,2}|\d{1,2})\s(\d{1,2}\.\d{1,2}|\d{1,2})'
state = []

@bot.message_handler(commands=['start'])
def start(message):
	message.text = f"Привет. Я простой бот который может скачать\
				твой любимый трек с youtube. Для того чтоб научиться мной\
				пользоваться введи /help."
	state.append({'chat_id':message.chat.id,
				  'u_id':message.from_user.id,
				  'data':message.text})
	bot.send_message(message.chat.id, message.text)

@bot.message_handler(commands=['help'])
def start(message):
	message.text = f"На самом деле все очень просто пока что. Надо всего лишь\
		....отправить мне ссылку на видео из которого ты хочешь достать\
		аудиодорожку и ждать) да, пока что сервис работает не очень\
		быстро, но в дальнейшем разработчик все поправит"
	remove_from_state(message.from_user.id)
	state.append({'chat_id':message.chat.id,
				  'u_id':message.from_user.id,
				  'data':message.text})
	bot.send_message(message.chat.id, message.text)

@bot.message_handler(commands=['url'])
def get_url(message):
	new_message = message
	new_message.message_id = message.message_id + 1
	download_music(new_message)

@bot.message_handler(commands=['dw'])
def test_method(message):
	keyboard = types.InlineKeyboardMarkup()
	full = types.InlineKeyboardButton(text="Full video?", callback_data=f"full,{message.text}")
	part = types.InlineKeyboardButton(text="Part", callback_data=f"part,{message.message_id}")
	cancel =  types.InlineKeyboardButton(text="Cancel", callback_data=f"cancel")
	keyboard.add(full)
	keyboard.add(part)
	keyboard.add(cancel)
	update_state({'chat_id': message.chat.id, 'u_id': message.from_user.id, 'data': message.text})
	bot.send_message(message.chat.id, "Which type of download u want?", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
	if call.message:
		if call.data.find("cancel") != -1:
			bot.send_message(call.message.chat.id, f"cancel")
			remove_from_state(call.message.chat.id)
			print(f"cancel_state - {state}")
			return
		result = call.data.split(",")
		url = re.findall(valid_url, result[1])
		if call.data.find("part") != -1:
			bot.send_message(call.message.chat.id, f"Enter start and finish.(Two numbers, like \"0\" \"1.50\")")
			return
		elif call.data.find("full") != -1:
			if len(url) != 0:
				bot.send_message(call.message.chat.id, "ok")
				download_music(call.message, url, None, None)
				remove_from_state(call.message.from_user.id)
				time.sleep(3)
		elif call.data.find("time") != -1:
			try:
				dataid = int(result[1])
			except Exception as e:
				bot.send_message(call.message.chat.id, f"what's wrong with this REBYATISHKI - {e}")

@bot.message_handler(content_types=["text"])
def get_music(message):
	times = []
	url = re.findall(valid_url, message.text)
	download_time = re.findall(start_fin, message.text)
	if len(url) != 0:
		bot.send_message(message.chat.id, "ok")
		download_music(message, url)
		time.sleep(3)
	elif len(download_time) != 0:
		finded_obj = find_obj_in_state(message.from_user.id)
		if finded_obj is None:
			bot.send_message(message.chat.id, "haven't url for download")
			return
		url = re.findall(valid_url, finded_obj['data'])
		if len(download_time[0]) == 2:
			for d_time in download_time[0]:
				seconds = validate_time(d_time)
				times.append(seconds)
			if times[0] > times[1]:
				bot.send_message(message.chat.id, "start bigger than end.")
				return
		elif len(download_time[0]) == 1:
			bot.send_message(message.chat.id, f"Start download - 0 to f{download_time[0]}")
			seconds = validate_time(download_time[0][0])
			download_music(message, url, None, seconds)
		else:
			bot.send_message(message.chat.id, "write 2 numbers plz.")
		download_music(message, url, times[0], times[1])
		remove_from_state(message.from_user.id)
	else:
		bot.send_message(message.chat.id, "don't understand u")

def download_music(message, url, start=None, finish=None):
	url_for_download = url[0]
	if db.check_exist_file(url_for_download):
		fileid = db.select_by_url(url_for_download)
		bot.send_audio(message.chat.id, fileid[0], None, timeout = 5)
	else:
		t1 = bot.send_message(message.chat.id, f"0%")
		bot.edit_message_text(f"25%", chat_id=message.chat.id, message_id=t1.message_id)
		fake_name, title = eng.download_by_link(url_for_download, message.chat.id)
		bot.edit_message_text(f"50%", chat_id=message.chat.id, message_id=t1.message_id) 
		path = eng.convert_to_mp3(fake_name, title, start, finish)
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

def find_obj_in_state(uid):
	f_obj = [x for x in state if x['u_id'] == uid]
	if len(f_obj) == 0:
		return None
	else:
		return f_obj[0]

def update_state(obj):
	remove_from_state(obj['u_id'])
	state.append(obj)

def remove_from_state(uid):
	rem_obj = [x for x in state if x['chat_id'] == uid]
	try:
		state.remove(rem_obj[0])
	except Exception as e:
		print(f"can't remove obj from state - {e}")

def validate_time(time):
	if time.find('.') == -1:
		return int(time)
	else:
		splited_time = i.split('.')
		seconds = int(splited_time[0]) * 60 + int(splited_time[1])
	return seconds

if __name__ == '__main__':
	try:
		bot.polling(none_stop = True)
	except Exception as e:
		print(f"bot has been falling {e}")
		time.sleep(5)
