FROM        python:3
LABEL       maintainer="Remo Dietlicher, remo.dietlicher@meteoswiss.ch"

WORKDIR     /app
COPY        . /app

RUN         pip install -r requirements.txt
RUN         chmod 777 probtest.py
RUN         mkdir icon

ENTRYPOINT  ["./probtest.py"]