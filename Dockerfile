FROM python:3

RUN pip install python-telegram-bot -U --pre

COPY main.py main.py
COPY game.py game.py
COPY keys/telegram_token keys/telegram_token

RUN python3 main.py
