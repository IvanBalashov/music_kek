# Music Bot For Telegram.

This bot can download audio from youtube link. 

## How use it.

* if u wana only download music.

Find this bot in telegram [@MusicKekbot] and use command /start.
<br>Now u can download audio. Send url from youtube to bot, and he download it.
<br>Now bot can load some part from video. Used command /dw [YouTube_url] and continue use the buttons.

* if u wana use this bot for yourself.

Clone this repo on your server. Install docker and docker-compose.
<br>U need download mongodb, and redis-json images to your server. Follow this commads for setup docker enviroment.
```
    docker pull mongo
    docker pull redislabs/rejson
    docker pull debian
    docker network create user-bridge
```
After docker env created, insert bot-token in config-example.py.
Now build main image and run all.
<br>And follow commands
```
    cd PWD/music_kek
    cp config-example.py data/config.py
    cd PWD/music_kek/deploy
    ./control.sh build 
    docker-compose up -d 
```
That all folks...