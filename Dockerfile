FROM python:3

RUN pip install python-telegram-bot -U --pre

COPY . .

ENTRYPOINT ["python3", "./main.py", "PASTE_TOKEN_HERE"]
