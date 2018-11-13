FROM debian:latest

RUN echo "nameserver 8.8.8.8" > /etc/resolv.conf
RUN apt-get update -y && apt-get upgrade -y
RUN apt-get install -y make build-essential libssl-dev zlib1g-dev \
&& apt-get install -y libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm \
&& apt-get install -y libncurses5-dev  libncursesw5-dev xz-utils tk-dev \
&& echo "deb http://ftp.de.debian.org/debian testing main" > /etc/apt/sources.list \
&& echo 'APT::Default-Release "stable";' | tee -a /etc/apt/apt.conf.d/00local \
&& apt-get update && apt-get -t testing install -y python3.6 \
&& apt-get -t testing install -y git ffmpeg wget python3-pip \
&& cd /root/ \
&& git clone https://github.com/IvanBalashov/music_kek \
&& pip3 install virtualenv virtualenvwrapper \
&& pip3 install -r /root/music_kek/deploy/requirements.txt

COPY entry-point.sh /root/music_kek/
ENTRYPOINT ["/bin/bash","/root/music_kek/entry-point.sh"]
