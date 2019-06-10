FROM python:3.7

RUN pip install python-telegram-bot
RUN pip install psycopg2-binary
RUN apt-get install git

RUN mkdir /app
ADD . /app
WORKDIR /app
RUN chmod +x /app/Bot/files.sh

CMD python3 /app/Bot/bot.py
