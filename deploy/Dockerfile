FROM python:3.6

RUN echo "nameserver 8.8.8.8" > /etc/resolv.conf
RUN apt-get update -y && apt-get upgrade -y
RUN apt-get install -y git ffmpeg wget python3-pip \
&& cd /root/ \
&& git clone https://github.com/IvanBalashov/music_kek \
&& pip3 install virtualenv virtualenvwrapper \
&& pip3 install -r /root/music_kek/deploy/requirements.txt

COPY entry-point.sh /root/music_kek/
ENTRYPOINT ["/bin/bash","/root/music_kek/entry-point.sh"]
