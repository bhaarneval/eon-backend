# EOn-backend

This is a monolithic architecture django project for BITS EOn.

## Important Features

- Python 3+
- Django 2.0+
- Database Postgres
- Uses Pipenv, Virtualenv
- Uses Celery and Redis for sending SMS/Email in background.
- AWS services - S3, SES, SNS, Elastic Beanstalk

## Installation

```bash
$ git clone https://github.com/bits-pgp-fse/eon-backend.git
$ virtualenv <virtual_env_name_of_your_choice>
$ source <virtual_env_name_of_your_choice>/bin/activate
$ cd eon-backend
$ pip install -r requirements.txt
```

## Environment variables

```
#DJANGO
SECRET_KEY=<something_very_secret>
DB_NAME=<db_name>
DB_USERNAME=<db_user>
DB_PASSWORD=<your_password>
DB_HOSTNAME=localhost
DB_PORT=5432

#JWT
ACCESS_TOKEN_LIFETIME=1(day)
REFRESH_TOKEN_LIFETIME=2(days)

#AWS
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=
EMAIL_ID=<your_email_id>
BUCKET=
BUCKET_PATH=
BROKER_URL=redis://localhost:6379
```

## Run Celery
Open separate terminal with your virtualenv activated. Then paste the below command.

```bash
$ celery -A eon_backend worker -l info
```

## Run Server

```bash
$ python manage.py migrate
$ python manage.py runserver
```
