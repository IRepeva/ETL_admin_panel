FROM python:3.10.4-bullseye

ENV PYTHONUNBUFFERED 1

WORKDIR /app

EXPOSE 8000/tcp

RUN pip install --upgrade pip &&  \
    groupadd -r app_group &&  \
    useradd -d /app -r -g app_group app_user

COPY /requirements.txt requirements.txt
RUN pip install -r requirements.txt --no-cache-dir

COPY --chown=app_user:app_group ./app /app
COPY ./etl /etl
COPY ./utils /utils

USER app_user

CMD ["uwsgi", "--ini", "uwsgi.ini"]
