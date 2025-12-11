FROM debian:sid
RUN echo 'deb http://mirrors.psu.ac.th/debian/ sid main contrib non-free' > /etc/apt/sources.list
RUN echo 'deb http://mirror.kku.ac.th/debian/ sid main contrib non-free' >> /etc/apt/sources.list
RUN apt update --fix-missing && apt dist-upgrade -y
RUN apt install -y python3.14 python3.14-dev python3.14-venv python3-pip build-essential npm locales golang

RUN sed -i '/th_TH.UTF-8/s/^# //g' /etc/locale.gen && locale-gen
ENV LANG th_TH.UTF-8
ENV LANGUAGE th_TH:en
ENV SADHU_SETTINGS=/app/sadhu-production.cfg
# ENV LC_ALL th_TH.UTF-8


RUN python3.14 -m venv /venv
RUN /venv/bin/python -m pip install wheel poetry gunicorn

WORKDIR /app
COPY poetry.lock pyproject.toml /app/
COPY sadhu/cmd /app/sadhu/cmd
RUN . /venv/bin/activate \
    && poetry config virtualenvs.create false \
    && python -m poetry install --no-interaction --only main 

COPY sadhu/web/static/package.json sadhu/web/static/package-lock.json sadhu/web/static/
RUN npm install --prefix sadhu/web/static

COPY . /app
RUN /venv/bin/brython-cli install --no-demo --install-dir sadhu/web/static/brython_modules

RUN cd sadhu/web/static/brython_modules; for i in $(ls -d */); do /venv/bin/python -m brython make_package ${i%%/}; done

