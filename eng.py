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
	# set youtube_dl arguments 
	ydl_opts = {
		'quiet': True, # don't write in output
		'no_warnings': True, # write warnings in output
		'format': "bestaudio/best", # download best audio quality
		'format': 'webm', # setup format webm
		'outtmpl': '%(name)s' + str(videoid) + '.%(ext)s', # setup output name 
		'postprocessor': [{ # dk how this need work, but if this not setup audio didn't download
			'key': "FFmpegExtractAudioPP",
			'preferredquality': "512",
		 }],
	}
	# start download audio
	with youtube_dl.YoutubeDL(ydl_opts) as ydl:
		data = ydl.extract_info(link) # exctrat info about audio
	fake_name = "NA" + str(videoid)
	# TODO: think about this query 
	# refactoring title 
	title = data.pop('title')
	title = re.sub(r'[^\w]', ' ', title)
	title = translate(title)
	title = title.replace(' ', '_')
	# return tmp_name and title
	return fake_name, title

def translate(inp: str) -> str:
	"""This is strange method for retranslate cirylic symbols in latin.
	   Stolen from stackoverflow)."""
	# list for encdoe cirylic symbols in latinc.
	symbols = (u"абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ",
			u"abvgdeejzijklmnoprstufhzcss_y_euaABVGDEEJZIJKLMNOPRSTUFHZCSS_Y_EUA")
	# generate dict like {"a":"a","б":"",...}
	tr = {ord(a):ord(b) for a, b in zip(*symbols)}
	# switch all symbols
	output = inp.translate(tr)
	return output

def convert_to_mp3(filename: str, title: str, start: int=None, end: int=None) -> list:
	"""core func for encode webm files to mp3"""
	# setup args for ffmpeg
	file_a = f"{path_to_wrk_dir}{filename}.webm" # input file
	file_b = f"{path_to_wrk_dir}{title}.mp3" # output file
	files_b = [] # this list need if file more than 30 mb
	args = [
		"/usr/bin/ffmpeg", # path to ffmpeg
		"-i", # flag for input file
		file_a, # input file
		"-acodec", # setup codec
		"libmp3lame", # codec name
		]

	# now need setup timings for target encode
	if start is not None and start != 0:
		args = args + ["-ss", str(start)]
	if end is not None and end != 0:
		args = args + ["-t", str(end - start)]

	# and last part for args to ffmpeg
	args = args + [
		"-metadata", # setup metadata for file
		f"title={title}", # title
		"-metadata",
		f"artist={title}", # and artist
		"-b:a", # setup bitrate
		"320k", # setup max bitrate
		file_b,
		]
	
	# start subprocess for encoding
	popen = subprocess.Popen(args)
	popen.wait()

	# check size file. if he more than 30 mb, bot need split him to chunks.
	size = getsize(file_b) / 1024 / 1024
	if size > 30 and ( start or end is None ):
		# setup args for split to chunks
		args = [
			"ffprobe",
			"-show_entries",
			"format=duration",
			"-i",
			file_b,
			]

		# get duration video.
		popen = subprocess.Popen(args, stdout=subprocess.PIPE)
		popen.wait()
		output = popen.stdout.read()
		# now we know how long this audio file
		# split to 10 min chunks
		dur = re.findall(r"\d{1,10}", str(output))
		# get chunks count for loop
		count_chunks = (int(dur[0]) // 600) + 1
		for chunk_start_time in range(0, count_chunks):
			# setup args for split
			# big parts of args the same for encode
			args = [
				"/usr/bin/ffmpeg",
				"-i",
				file_b,
				"-ss",
				f"{chunk_start_time * 600}", # when start chunk
				"-t",
				"600", # 10 mints duration
				"-acodec",
				"copy", # copy
				"-b:a",
				"320k",
				f"{path_to_wrk_dir}{title}_{chunk_start_time}.mp3", # now we have path to video with chunk number.
			]
			try:
				# start process for cut chunk
				popen = subprocess.Popen(args, stdout=subprocess.PIPE)
				popen.wait()
			# handle except.
			except Exception as e:
				print(f"Exception - {e}")
			files_b.append(f"{path_to_wrk_dir}{title}_{chunk_start_time}.mp3") # append name of file in list
	try:
		# remove tmp file
		remove(file_a)
	# handle except
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
	""" This function delete file. All work with files needed in one py script.
		Think this is true way."""
	remove(path)

def get_file_list(path: str) -> list:
	"""Get list with all files in wrk directory."""
	return [f for f in listdir(path) if isfile(join(path, f))]
