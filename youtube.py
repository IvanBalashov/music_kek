import urllib.request as url
import youtube_dl
import re
import subprocess
import os
from config import youtube_api
from apiclient.discovery import build
from apiclient.errors import HttpError


DEVELOPER_KEY = youtube_api
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

def chose_video_for_download(videos):
    videos_count = len(videos)
    print('chose video for download\nwrite a number 0 of', videos_count - 1)
    number = input()
    name = re.findall('[a-zA-Z0-9-_()]{13}$', videos[int(number)])
    video_id = name[0].replace('(','').replace(')','')
    newtitle = videos[int(number)].replace(' ','_').replace('!','').replace("(","").replace(")","").replace("_"+video_id,"")
    uri = 'https://www.youtube.com/watch?v=' + video_id
    title = download_youtube(uri, newtitle)
    convert_flv(newtitle)

def youtube_search(kw):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey = DEVELOPER_KEY)
    search_response = youtube.search().list(
        q = kw,
        part = "id,snippet",
        maxResults = 25
    ).execute()

    videos = []
    channels = []
    for search_result in search_response.get("items", []):
        if search_result["id"]["kind"] == "youtube#video":
            videos.append("%s (%s)" % (search_result["snippet"]["title"], search_result["id"]["videoId"]))
        elif search_result["id"]["kind"] == "youtube#channel":
            channels.append("%s (%s)" % (search_result["snippet"]["title"], search_result["id"]["channelId"]))

    print('Videos:\n')
    count = 0
    for vid in videos:
        print(count, ' ', vid.encode('utf-8'))
        count = count + 1
    print('Chanels:\n')
    for chan in channels:
        print(chan.encode('utf-8'))
    chose_video_for_download(videos)

def download_youtube(uri, name):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'format': 'bestaudio/best',
        'outtmpl': name + '.%(ext)s',
        'postprocessor': [{
            'key': 'FFmpegExtracrtAudio',
            'preferredcodec': 'flv',
            'preferredquality':'256',
         }],
    }
    print('started download')
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        data = ydl.extract_info(uri)
    print('video downloaded')
    return data.pop('title')

def convert_flv(name):
    DEVNULL = open(os.devnull, 'wb')
    fileA =  os.getcwd() + "/" + name + ".webm"
    fileB =  os.getcwd() + "/" + name + ".mp3"
    meta = '-metadata'
    newtitle = 'title=' + name
    newauthor = 'artist=' + name
    # for FreeBSD absolute path to ffmpeg - /usr/local/bin/ffmpeg , for linux - /usr/bin/ffmpeg
    print('start encode')
    subprocess.run(["/usr/local/bin/ffmpeg","-i", fileA, "-acodec", "libmp3lame", \
        meta,newtitle,meta,newauthor,"-aq", "4", fileB])
    os.remove(fileA)
    print('end encode')

youtube_search('anti-flag broken bones')