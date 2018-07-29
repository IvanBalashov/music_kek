import urllib.request as url
import youtube_dl
import re
import subprocess
from subprocess import run
from os import listdir, remove, devnull
from os.path import isfile, join
from data.config import path_to_wrk_dir

def download_by_link(link: str, videoid: str) -> [str, str]:
	"""This method is setup youtube_dl for downlad video"""
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

def translate(inp: str) -> str:
	"""This is strange method for retranslate cirylic symbols in latin.
	   Stolen from stackoverflow)."""
	symbols =(u"абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ",
			u"abvgdeejzijklmnoprstufhzcss_y_euaABVGDEEJZIJKLMNOPRSTUFHZCSS_Y_EUA")
	tr = {ord(a):ord(b) for a, b in zip(*symbols)}
	output = inp.translate(tr)
	return output

def convert_to_mp3(filename: str, title: str, start: int=None, end: int=None) -> str:
	arg_to_start = None
	arg_to_end = None
	fileB = f"{path_to_wrk_dir}{title}.mp3"
	meta = f"-metadata"
	newtitle = f"title={title}"
	newauthor = f"artist={title}"
	# for FreeBSD absolute path to ffmpeg - /usr/local/bin/ffmpeg , for linux - /usr/bin/ffmpeg
	fileA = f"{path_to_wrk_dir}{filename}.webm"
	args = ['/usr/bin/ffmpeg','-i', fileA, '-acodec', 'libmp3lame']		
	if start is not None or start != 0:
		args = args + ['-ss', str(start)]
	if end is not None or start != 0:
		args = args + ['-t', str(end - start)]
	args = args + [meta, newtitle, meta, newauthor, '-aq', '0', fileB]
	try:
		run(args)
	except Exception:
		run(['/usr/bin/ffmpeg','-i', fileA, '-acodec', 'libmp3lame', \
			meta, newtitle, meta, newauthor, arg_to_start, arg_to_end, '-aq', '0', fileB])
	try:
		remove(fileA)
	except FileNotFoundError:
		files = get_file_list(path_to_wrk_dir)
		for i in files:
			if -1 != f"{path_to_wrk_dir}{i}".find(f"{filename}") and f"{i}".find(f".mp3") == -1:
				try:
					remove(f"{path_to_wrk_dir}{i}")
				except FileNotFoundError:
					print(f"can't remove file {path_to_wrk_dir}{i}")
	return fileB

def remove_file(path: str) -> None:
	remove(path)

def get_file_list(path: str) -> list:
    return [f for f in listdir(path) if isfile(join(path, f))]
