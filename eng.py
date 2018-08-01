import urllib.request as url
import youtube_dl
import re
import subprocess
from subprocess import run
from os import listdir, remove, devnull
from os.path import isfile, join, getsize
from data.config import path_to_wrk_dir

def download_by_link(link: str, videoid: str) -> [str, str]:
	"""This method is setup youtube_dl for downlad video"""
	print(f"link - {link}")
	ydl_opts = {
#		'quiet': True,
		'no_warnings': True,
		'format': "bestaudio/best",
		'outtmpl': '%(name)s' + str(videoid) + '.%(ext)s',
		'postprocessor': [{
			'key': "FFmpegExtractAudioPP",
			'preferredquality': "512",
		 }],
	}
	with youtube_dl.YoutubeDL(ydl_opts) as ydl:
		data = ydl.extract_info(link)
	fake_name = "NA" + str(videoid)
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
	file_b = f"{path_to_wrk_dir}{title}.mp3"
	files_b = []
	meta = f"-metadata"
	newtitle = f"title={title}"
	newauthor = f"artist={title}"
	file_a = f"{path_to_wrk_dir}{filename}.webm"
	args = ["/usr/bin/ffmpeg","-i", file_a, "-acodec", "libmp3lame"]		
	if start is not None and start != 0:
		args = args + ["-ss", str(start)]
	if end is not None and end != 0:
		args = args + ["-t", str(end - start)]
	args = args + [meta, newtitle, meta, newauthor,]
	size = getsize(file_a) / 1024 / 1024
	print(f"size - {size}")
	if size > 3:
		args = args + ["-aq", "3", file_b]
	else:
		args = args + ['-aq', '0', file_b]
	run(args)
	size = getsize(file_b) / 1024 / 1024
	print(f"size - {size}")
	if size < 30:
		args = ["ffprobe","-show_entries", "format=duration", "-i", file_b]
		popen = subprocess.Popen(args, stdout=subprocess.PIPE)
		popen.wait()
		output = popen.stdout.read()
		dur = re.findall(r"\d{1,10}", str(output))
		count_chunks = int(dur[0]) // 600
		print(f"count_chunks - {count_chunks}")
		for chunk_start_time in range(0, count_chunks + 1):
			args = [
				"/usr/bin/ffmpeg",
				"-i",
				file_b,
				"-ss",
				f"{chunk_start_time * 600}",
				"-t",
				f"600",
				"-acodec",
				"copy",
				f"{path_to_wrk_dir}{title}_{chunk_start_time}.mp3",
			]
			try:
				run(args)
			except Exception as e:
				print(f"Exception - {e}")
			files_b.append(f"{path_to_wrk_dir}{title}_{chunk_start_time}.mp3")
	try:
		remove(file_a)
	except FileNotFoundError:
		files = get_file_list(path_to_wrk_dir)
		for i in files:
			if -1 != f"{path_to_wrk_dir}{i}".find(f"{filename}") and f"{i}".find(f".mp3") == -1:
				try:
					remove(f"{path_to_wrk_dir}{i}")
				except FileNotFoundError:
					print(f"can't remove file {path_to_wrk_dir}{i}")
	if len(files_b) == 0:
		return [file_b]
	else:
		return files_b

def remove_file(path: str) -> None:
	remove(path)

def get_file_list(path: str) -> list:
	return [f for f in listdir(path) if isfile(join(path, f))]
