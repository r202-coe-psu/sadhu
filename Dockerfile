FROM debian:sid
RUN echo 'deb http://mirrors.psu.ac.th/debian/ sid main contrib non-free' > /etc/apt/sources.list
RUN echo 'deb http://mirror.kku.ac.th/debian/ sid main contrib non-free' >> /etc/apt/sources.list
RUN apt update --fix-missing && apt dist-upgrade -y
RUN apt install -y python3 python3-dev python3-pip python3-venv build-essential npm locales golang

RUN sed -i '/th_TH.UTF-8/s/^# //g' /etc/locale.gen && locale-gen
ENV LANG th_TH.UTF-8
ENV LANGUAGE th_TH:en
# ENV LC_ALL th_TH.UTF-8


RUN python3 -m venv /venv
ENV PYTHON=/venv/bin/python3
RUN $PYTHON -m pip install wheel poetry gunicorn

WORKDIR /app
COPY poetry.lock pyproject.toml /app/
COPY sadhu/cmd /app/sadhu/cmd
RUN $PYTHON -m poetry config virtualenvs.create false && $PYTHON -m poetry install --no-interaction --only main

COPY sadhu/web/static/package.json sadhu/web/static/package-lock.json sadhu/web/static/
RUN npm install --prefix sadhu/web/static

COPY . /app

RUN cd /app/sadhu/web/static/brython; for i in $(ls -d */); do $PYTHON -m brython --make_package ${i%%/}; done

ENV SAHDU_SETTINGS=/app/sadhu-production.cfg
