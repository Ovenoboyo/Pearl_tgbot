FROM python:3.7

RUN pip install python-telegram-bot
RUN pip install psycopg2-binary

RUN mkdir /app
ADD . /app
WORKDIR /app

CMD python3 /app/bot.py
