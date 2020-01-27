FROM python:latest

RUN apt-get install libssl-dev
RUN pip3 install python-dotenv flask redis pyjwt requests passlib pymongo authlib gevent greenlet gunicorn itsdangerous

WORKDIR /var/www
CMD ["gunicorn", "-k", "gevent", "-b", "0.0.0.0:5000", "--chdir", "app", "app:app"]
