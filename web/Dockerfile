FROM python:latest

RUN apt-get install libssl-dev
RUN pip3 install python-dotenv flask redis pyjwt requests passlib pymongo authlib

WORKDIR /var/www
ENV FLASK_APP=app/app.py
ENV FLASK_RUN_HOST=0.0.0.0
CMD ["flask", "run"]
