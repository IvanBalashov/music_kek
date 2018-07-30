# docker build -t ubuntu1604py36
FROM ubuntu:latest

RUN echo "deb http://ppa.launchpad.net/jonathonf/python-3.6/ubuntu xenial main" >/etc/apt/sources.list.d/jonathonf-ubuntu-python-3_6-xenial.list \
&& apt-key adv --keyserver ipv4.pool.sks-keyservers.net --recv-keys 8CF63AD3F06FC659 \
&& apt-get update \
&& apt-get install -y --allow-unauthenticated python3.6 python3.6-dev python3.6-venv git ffmpeg wget gcc libmysqlclient-dev \
&& wget https://bootstrap.pypa.io/get-pip.py && python3.6 get-pip.py \
&& cd /root/ \
&& git clone https://github.com/IvanBalashov/music_kek \
&& pip3.6 install virtualenv virtualenvwrapper \
&& pip3.6 install -r /root/music_kek/requirements.txt

COPY entry-point.sh /root/music_kek/
RUN mkdir /root/music_kek/data
RUN touch /root/music_kek/data/__init__.py
#EXPOSE 8082
ENTRYPOINT ["/bin/bash","/root/music_kek/entry-point.sh"]
