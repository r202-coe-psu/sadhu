FROM debian:sid
RUN echo 'deb http://mirrors.psu.ac.th/debian/ sid main contrib non-free' > /etc/apt/sources.list
RUN echo 'deb http://mirror.kku.ac.th/debian/ sid main contrib non-free' >> /etc/apt/sources.list
RUN apt update --fix-missing && apt dist-upgrade -y
RUN apt install -y python3 python3-dev python3-pip python3-venv build-essential npm locales golang

RUN sed -i '/th_TH.UTF-8/s/^# //g' /etc/locale.gen && locale-gen
ENV LANG th_TH.UTF-8
ENV LANGUAGE th_TH:en
# ENV LC_ALL th_TH.UTF-8

COPY . /app
WORKDIR /app

RUN python3 -m venv venv
ENV PYTHON=/app/venv/bin/python3
RUN $PYTHON -m pip install wheel poetry gunicorn
RUN $PYTHON -m poetry config virtualenvs.create false && $PYTHON -m poetry install --no-interaction


RUN npm install --prefix sadhu/web/static

RUN cd /app/sadhu/web/static/brython; for i in $(ls -d */); do $PYTHON -m brython --make_package ${i%%/}; done

# ENV SADHU_SETTINGS=/app/sadhu-production.cfg
# ENV FLASK_DEBUG=false
#ENV AUTHLIB_INSECURE_TRANSPORT=true


#EXPOSE 8080
#ENTRYPOINT ['sadhu-web']
