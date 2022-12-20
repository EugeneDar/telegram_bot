FROM python:3

RUN pip install python-telegram-bot -U --pre

COPY . .

RUN python3 main.py
