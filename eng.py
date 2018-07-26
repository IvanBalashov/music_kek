import urllib.request as url
import youtube_dl
import re
import subprocess
import os
from data.config import path_to_wrk_dir

def download_by_link(link, videoid):
	ydl_opts = {
		'quiet': True,
		'no_warnings': True,
		'format': 'bestaudio/best',
		'outtmpl': '%(name)s' + str(videoid) + '.%(ext)s',
		'postprocessor': [{
			'key': 'FFmpegExtractAudioPP',
			'preferredquality': '512',
		 }],
	}
	with youtube_dl.YoutubeDL(ydl_opts) as ydl:
		data = ydl.extract_info(link)
	fake_name = 'NA' + str(videoid)
	title = data.pop('title')
	title = re.sub(r'[^\w]', ' ', title)
	title = translate(title)
	title = title.replace(' ', '_')
	return fake_name, title

def translate(inp):
	symbols =(u"абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ",
			u"abvgdeejzijklmnoprstufhzcss_y_euaABVGDEEJZIJKLMNOPRSTUFHZCSS_Y_EUA")
	tr = {ord(a):ord(b) for a, b in zip(*symbols)}
	output = inp.translate(tr)
	return output

def convert_to_mp3(filename, title):
	DEVNULL = open(os.devnull, 'wb')
	fileB = f"{path_to_wrk_dir}{title}.mp3"
	meta = f"-metadata"
	newtitle = f"title={title}"
	newauthor = f"artist={title}"
	# for FreeBSD absolute path to ffmpeg - /usr/local/bin/ffmpeg , for linux - /usr/bin/ffmpeg
	try:
		fileA = f"{path_to_wrk_dir}{filename}.webm"
		subprocess.run(['/usr/bin/ffmpeg','-i', fileA, '-acodec', 'libmp3lame', \
			meta, newtitle, meta, newauthor, '-aq', '0', fileB])
	except Exception:
		fileA = f"{path_to_wrk_dir}{filename}.mp4"
		subprocess.run(['/usr/bin/ffmpeg','-i', fileA, '-acodec', 'libmp3lame', \
			meta, newtitle, meta, newauthor, '-aq', '0', fileB])
	try:
		os.remove(fileA)
	except FileNotFoundError:
		files = get_file_list(path_to_wrk_dir)
		for i in files:
			if -1 == f"{path_to_wrk_dir}{i}".find(f"{filename}") and f"{i}".find(f".mp3") == -1:
				os.remove(f"{path_to_wrk_dir}{i}")

	return fileB

def remove_file(path):
	os.remove(path)

def get_file_list(path: str) -> list:
    return [f for f in os.listdir(path) if os.path(join(path, f))]