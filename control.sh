#!/bin/bash
case $1 in
    "build" )
        docker build -t music_kek:v0.1 ./
    ;;
    "run" )
        docker run --restart unless-stopped -d -v /home/music/music_kek/data/:/root/music_kek/data/ --name music_kek_v0.1 music_kek:v0.1
    ;;
    "stop" )
        docker stop music_kek_v0.1
    ;;
    "rm" )
        docker rm music_kek_v0.1
    ;;
    "rmi" )
        docker rmi music_kek:v0.1
    ;;
    "rebuild" )
        docker stop music_kek_v0.1
        docker rm music_kek_v0.1
        docker rmi music_kek:v0.1
        docker build -t music_kek:v0.1 ./
        docker run --restart unless-stopped -d -v /home/music/music_kek/data/:/root/music_kek/data/ --name music_kek_v0.1 music_kek:v0.1
    ;;
    "inter")
        docker run -it --entrypoint /bin/bash -v /home/music/music_kek/data/:/root/music_kek/data/ --name music_kek_v0.1 music_kek:v0.1
    ;;
esac

