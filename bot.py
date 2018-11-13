import telebot
import time
import re
import src.eng as eng
from os.path import getsize
from data.config import bot_token
from data.config import database_name
from data.config import rejson_host
from data.config import rejson_port
from telebot import types
from src.store import StoreController
from src.dbmongo import DBProvider

# bot object - core for this bot.
print(f"init bot")
bot = telebot.TeleBot(bot_token)
# now here sqlite
print(f"init mongo")
provider = DBProvider("mongo", 27017, "test-base")
# used redis_json for save states
# need this, coz bot down after timeout.
# TODO: write worker for loading states in to bot after bot fall.
print(f"init redis")
store = StoreController(rejson_host, rejson_port)
# two regex for validate youtube urls, and timecode.
valid_url = r'https://www.youtube.com/watch\?v\=[0-9A-Za-z\_\-]{11}|https://youtu.be/[0-9A-Za-z\_\-]{11}'
start_fin = r'(\d{1,2}\.\d{1,2}|\d{1,2})\s(\d{1,2}\.\d{1,2}|\d{1,2})'

# first handler for command /start
# here im traning with new features, like states, mongodb, e.t.c.
@bot.message_handler(commands=['start'])
def start(message) -> None:
	"""
		first handler for command /start. 
		here im traning with new features, like states, mongodb, e.t.c.
	"""
	#print(f"msg - {message}")
	message.text = f"Привет. Я простой бот который может скачать\
				твой любимый трек с youtube. Для того чтоб научиться мной\
				пользоваться введи /help."
	#print(f"message - {message.from_user}") # TODO: delete this print. rewrite on normal loging.
	# store first message in store.
	store.save_data_in_store(message.from_user.username,
				 {'chat_id': message.chat.id,
				  'u_id': message.from_user.id,
				  'data': message.text})

	if provider.find_user_in_db(message.from_user.id) is None:
		provider.insert_user_in_db({'user_name': message.from_user.username, 'u_id' :message.from_user.id, 'files': []})
	# send msg in chat.
	bot.send_message(message.chat.id, message.text)

@bot.message_handler(commands=['help'])
def helper(message) -> None:
	"""
		second handler for command /help. he's like /start
	"""
	message.text = f"На самом деле все очень просто пока что. Надо всего лишь\
		....отправить мне ссылку на видео из которого ты хочешь достать\
		аудиодорожку и ждать) да, пока что сервис работает не очень\
		быстро, но в дальнейшем разработчик все поправит"
	store.delete_data_in_store(message.from_user.username)
	store.save_data_in_store(message.from_user.username,
				 {'chat_id': message.chat.id,
				  'u_id': message.from_user.id,
				  'data': message.text})

	if provider.find_user_in_db(message.from_user.id) is None:
		provider.insert_user_in_db({'user_name': message.from_user.username, 'u_id' :message.from_user.id, 'files': []})
	bot.send_message(message.chat.id, message.text)

# thrid handler for command /dw [url]
# set three buttons in answer on command
# don't work with out url
@bot.message_handler(commands=['dw'])
def download(message) -> None:
	"""
		thrid handler for command /dw [url]
    	set three buttons in answer on command.don't work with out url
	"""
	# generate keyboard 
	keyboard = types.InlineKeyboardMarkup()
	# first button setup download full audio from url.
	full = types.InlineKeyboardButton(text=f"Full video?", callback_data=f"full,{message.text}")
	# second button for setup time codes
	part = types.InlineKeyboardButton(text=f"Part", callback_data=f"part,{message.message_id}")
	# thrid button cancel downloading.
	cancel =  types.InlineKeyboardButton(text=f"Cancel", callback_data=f"cancel")
	# add all buttons to keyboard.
	keyboard.add(full)
	keyboard.add(part)
	keyboard.add(cancel)
	# now this is important part. need save message in store, coz buttons has callback function
	# in callback function we can't get next messages. (i'm trying more times get next message)
	store.delete_data_in_store(message.from_user.username)
	store.save_data_in_store(message.from_user.username,
				 {'chat_id': message.chat.id,
				  'u_id': message.from_user.id,
				  'data': message.text})

	if provider.find_user_in_db(message.from_user.id) is None:
		provider.insert_user_in_db({'u_id' :message.from_user.id, 'files': []})
	bot.send_message(message.chat.id, f"Which type of download u want?", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call) -> None:
	"""
		fourth handler handle callback events from buttons.
	"""
	# if have message from callback
	if call.message:
		# and data is cancel
		if call.data.find("cancel") != -1:
			# delete data from store and do nothing.
			bot.send_message(call.message.chat.id, f"cancel")
			store.delete_data_in_store(call.message.from_user.username)
			return
		# split data from callback.
		# this need for catch url from full download
		result = call.data.split(",")
		# check url on valid
		url = re.findall(valid_url, result[1])
		# if set part download we need send message for user with request setup timecodes.
		if call.data.find("part") != -1:
			bot.send_message(call.message.chat.id, f"Enter start and finish.(Two numbers, like \"0\" \"1.50\")")
			return
		# if set full, we get url and download audio with out time codes
		elif call.data.find("full") != -1 and len(url) != 0:
			# send "ok" message
			bot.send_message(call.message.chat.id, "ok")
			# start download
			download_music(call.message, url, None, None)
			# delete data from state
			store.delete_data_in_store(call.message.from_user.username)
			time.sleep(3)

@bot.message_handler(content_types=["text"])
def get_music(message) -> None:
	""" 
		fifth handler for text
			here we have two options
				- only url -> download full audio with out another question to user.
				- setup timecodes -> if user use command /dw, we stored him url in state
				and we need download part of audio.
		most complicated part of bot.
	"""
	# init list with timecodes.
	times = []
	# validate message on url.
	url = re.findall(valid_url, message.text)
	# and validate message on timecodes
	download_time = re.findall(start_fin, message.text) # TODO: think about another code.
	# if we get only url, start download full audio.
	if len(url) != 0:
		bot.send_message(message.chat.id, f"ok")
		download_music(message, url)
		time.sleep(3)
		return
	# if we get 2 numbers, than url did setup in state.
	elif len(download_time) != 0:
		# get url from store [/dw [url_from_youtube]]
		finded_obj = store.get_field_data_in_store(message.from_user.username, 'data')
		print(f"finded-obj - {finded_obj}") # TODO: delete this print, he is need for debug.
		# if store for this user empty, return him message about this.
		if finded_obj is None:
			bot.send_message(message.chat.id, f"haven't url for download")
			return
		# parse url from request from store.
		url = re.findall(valid_url, finded_obj['data'])
		# coz timecode is placed, need parse to two numbres.
		if len(download_time[0]) == 2:
			# in loop parse two numbers in seconds, like 1.30 min = 90 sec
			for d_time in download_time[0]:
				seconds = validate_time(d_time)
				times.append(seconds)
			# check for corrtly timecodes.
			if times[0] > times[1]:
				# if not, answer user about error.
				bot.send_message(message.chat.id, f"start bigger than end.")
				return
		# TODO: fix regex for one number. main think is, if placed one number, start download with 0.00
		elif len(download_time[0]) == 1:
			bot.send_message(message.chat.id, f"Start download - 0 to f{download_time[0]}")
			seconds = validate_time(download_time[0][0])
			download_music(message, url, None, seconds)
		# if seted not numbers, answer to user about it.
		else:
			bot.send_message(message.chat.id, f"write 2 numbers plz.")
		# start download audio with timecodes.
		download_music(message, url, times[0], times[1])
		# delete data from store
		store.delete_data_in_store(message.from_user.username)
	else:
		# if user setups not correct, answer him about this.
		bot.send_message(message.chat.id, f"don't understand u")

def download_music(message, url, start=None, finish=None) -> None:
	"""
		main method for downlad audio.
	"""
	url_for_download = url[0]
	file = None
	list_of_files = []
	if (start and finish) is None:
		file = provider.find_file_in_db(url_for_download)
		return
	if file is not None:
		msg = bot.send_message(message.chat.id, f"i'm know this song, w8 plz a bit...")
		if len(file['files']) > 0:
			for f in file['files']:
				bot.send_audio(message.chat.id, f, None, timeout = 5)
			return
	# need save msg obj for progress_bar
	user_msg = bot.send_message(message.chat.id, f"0%")
	# start download and request user about start downloading
	bot.edit_message_text(f"25%", chat_id=message.chat.id, message_id=user_msg.message_id)
	# try to fix bug with 
	rand_name = message.chat.id + message.message_id
	# download audio and safe title, and tmp_name of file
	tmp_file, title = eng.download_by_link(url_for_download, rand_name)
	# request user about start encoding
	bot.edit_message_text(f"50%", chat_id=message.chat.id, message_id=user_msg.message_id)
	# start comvert file same file names
	path = eng.convert_to_mp3(tmp_file, title, start, finish)
	for chunk in reversed(path):
		# all steps like for one file
		file = open(chunk, 'rb')
		bot.edit_message_text(f"75%", chat_id=message.chat.id, message_id=user_msg.message_id)
		try:
			msg = bot.send_audio(message.chat.id, file, None, timeout = 60)
			bot.edit_message_text(f"100%", chat_id=message.chat.id, message_id=user_msg.message_id)
			list_of_files.append(msg.audio.file_id)
		except Exception as e:
			bot.edit_message_text(f"TimeOut {e}", chat_id=message.chat.id, message_id=user_msg.message_id)
		# remove all files from server
		eng.remove_file(chunk)
	# save file in mongodb, need save url and list of files for big files
	if (start and finish) is None:
		print(f"save file in db")
		file_id = provider.insert_file_in_db({'file_name': title, 'downloaded_url': url_for_download, 'files': list_of_files})
		# save info about files in user fields TODO: add llast 10 downloaded files.
		user = provider.find_user_in_db(message.from_user.id)
		# if user don't exist in mongo, need add him.
		print(f"user - {user}")
		if user is None:
			provider.insert_user_in_db({'user_name': message.from_user.username, 'u_id' :message.from_user.id, 'files': [file_id]})
		else:
			files_list = user['files']
			files_list.append(list_of_files)
			print(f"files list is {files_list}")
			provider.update_user_in_db(message.from_user.id, {'files': files_list})

def validate_time(time) -> int:
	"""
		helper for validate time. split string by dot, 
		summ mun and sec. return sec
	"""
	if time.find('.') == -1:
		return int(time)
	else:
		splited_time = time.split('.')
		seconds = int(splited_time[0]) * 60 + int(splited_time[1])
	return seconds

if __name__ == '__main__':
	try:
		bot.polling(none_stop = True)
	except Exception as e:
		print(f"bot has been falling {e}")
		time.sleep(5)
