import urllib.request as url
import youtube_dl
import re
import subprocess
import os
from config import youtube_api
from config import path_to_wrk_dir
from apiclient.discovery import build
from apiclient.errors import HttpError

def download_by_link(link):
    i = 0
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'format': 'bestaudio/best',
        'outtmpl': '%(name)s'+str(i)+'.%(ext)s',
        'postprocessor': [{
            'key': 'FFmpegExtracrtAudio',
            'preferredcodec': 'flv',
            'preferredquality':'512',
         }],
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        data = ydl.extract_info(link)
    fake_name = 'NA' + str(i)
    title = data.pop('title').replace(' ','_').replace('!','').replace("(","").replace(")","").replace("|","").replace("&","and").replace(":","")
    return fake_name, title

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

fake_name, title = download_by_link('https://www.youtube.com/watch?v=CW5oGRx9CLM')
convert_to_mp3(fake_name, title)