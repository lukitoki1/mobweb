FROM python:latest

RUN apt-get install libssl-dev
RUN pip3 install python-dotenv flask redis pyjwt requests pymongo Flask-WTF flask-bcrypt

WORKDIR /var/www
CMD ["flask", "run"]
