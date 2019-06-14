FROM debian:sid
RUN echo 'deb http://mirrors.psu.ac.th/debian/ sid main contrib non-free' > /etc/apt/sources.list
RUN echo 'deb http://mirror.kku.ac.th/debian/ sid main contrib non-free' >> /etc/apt/sources.list
RUN apt update && apt upgrade -y
RUN apt install -y python3 python3-dev python3-pip python3-venv
RUN apt install -y npm

COPY . /app
WORKDIR /app

RUN pip3 install flask
RUN python3.7 setup.py develop
RUN pip3 install uwsgi
RUN npm install --prefix sadhu/static

ENV SADHU_SETTINGS=/app/sadhu-production.cfg
#ENV FLASK_ENV=prodoction
#ENV AUTHLIB_INSECURE_TRANSPORT=true


#EXPOSE 8080
#ENTRYPOINT ['sadhu-web']
