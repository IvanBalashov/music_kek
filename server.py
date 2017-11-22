import urllib.request as url
import youtube_dl
import re
import subprocess
import os
# В общем, надо хоть мысли записать. Музыку искать буду в VK, SoundCloud, Youtube, мб Yandex.Music.
# Пока что как все я это вижу. Будет бот + веб морда(возможно) куда нужно будет писать название песни, 
# пихон ее будет удачно находить, заливать в телегу, и делиться с юзерами.
# Идея такая, юзер логиниться, говорит мол, найди песню плиз, ну и соответсвенно тут начинается магия.
# Не на всех источниках есть музыка для скачивания(соундклауд как пример). Нужно найти трек, если это ютуб то
# Сделать дорожку из видео, и скачать его. Далее вернуть пользователю трек.
from apiclient.discovery import build
from apiclient.errors import HttpError

def read_api_key(path):
    full_path = os.getcwd()+'/'+ path
    f = open(full_path, 'r+')
    data = f.read()
    return data

DEVELOPER_KEY = read_api_key('api_key')
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

# Джугл апи норм завелся, в принципе работает поиск видосиков. пока что меня все устраивает.
# TODO:: insert name file in tmpl for youtube_dl, swap all spacebars on _ and remove all special symbols.
def chose_video_for_download(videos):
    videos_count = len(videos)
    print('chose video for download\nwrite a number 0 of', videos_count - 1)
    number = input()
    n = re.findall('[a-zA-Z0-9-_()]{13}$', videos[int(number)])
    newtitile = videos[int(number)].replace(' ','_').replace('!','')
    t1 = n[0].replace('(','').replace(')','')
    uri = 'https://www.youtube.com/watch?v=' + t1
    title = download_youtube(uri, newtitile)
    print(title)
#    convert_flv(t1)

def youtube_search(kw):
    print(kw)
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey = DEVELOPER_KEY)
    search_response = youtube.search().list(
        q = kw,
        part = "id,snippet",
        maxResults = 25
    ).execute()

    videos = []
    channels = []
    playlists = []
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
    print(name, uri)
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': name+'.%(ext)s',
        'postprocessor': [{
            'key': 'FFmpegExtracrtAudio',
            'preferredcodec': 'flv',
            'preferredquality':'256',
         }],
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        data = ydl.extract_info(uri)
    return data.pop('title')

def convert_flv(name):
    args = '-i ' + os.getcwd() + '/' + name + '.webm -acodec libmp3lame -aq 4 '+ os.getcwd() + '/'+ name+'.mp3'
    print(args)
    subprocess.run(['/usr/local/bin/ffmpeg', args])

youtube_search('system of a down chop say')
