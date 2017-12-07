import urllib.request as url
import youtube_dl
import re
import subprocess
import os
from config import youtube_api
from config import path_to_wrk_dir
from apiclient.discovery import build
from apiclient.errors import HttpError

def download_by_link(link, videoid):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'format': 'bestaudio/best',
        'outtmpl': '%(name)s'+str(videoid)+'.%(ext)s',
        'postprocessor': [{
            'key': 'FFmpegExtracrtAudio',
            'preferredcodec': 'flv',
            'preferredquality':'512',
         }],
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        data = ydl.extract_info(link)
    fake_name = 'NA' + str(videoid)
    title = data.pop('title').replace(' ','_').replace('!','').replace("(","").replace(")","").replace("|","").replace("&","and").replace(":","").replace("/","")
    title = re.sub(r'[^\w]','', title)
    title = translate(title)
    return fake_name, title

def translate(inp):
    symbols = (u"абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ",
            u"abvgdeejzijklmnoprstufhzcss_y_euaABVGDEEJZIJKLMNOPRSTUFHZCSS_Y_EUA")
    tr = {ord(a):ord(b) for a, b in zip(*symbols)}
    output = inp.translate(tr)
    return output
#def youtube_search(keyword):

def convert_to_mp3(filename, title):
    DEVNULL = open(os.devnull, 'wb')
    fileA = path_to_wrk_dir + filename + '.webm'
    fileB = path_to_wrk_dir + title + '.mp3'
    meta = '-metadata'
    newtitle = 'title=' + title
    newauthor = 'artist=' + title
    # for FreeBSD absolute path to ffmpeg - /usr/local/bin/ffmpeg , for linux - /usr/bin/ffmpeg
    subprocess.run(['/usr/bin/ffmpeg','-i', fileA, '-acodec', 'libmp3lame', \
        meta,newtitle,meta,newauthor,'-aq', '4', fileB])
    os.remove(fileA)
    return fileB

def remove_file(path):
    os.remove(path)