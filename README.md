# EOn-backend

This is a monolithic architecture django project for BITS EOn.

## Prerequisites

- Postgres
- Redis
- Celery

Note: Make sure that Postgres and Redis is installed and running on your system. 
If your don't have these. Please installed them from below link.

- Postgres - https://www.postgresql.org/download/
- Redis - https://redis.io/topics/quickstart

## Important Features

- Python 3+
- Django 2.0+
- Database Postgres
- Uses Virtualenv
- Uses Celery and Redis for sending SMS/Email in background.
- AWS services - S3, SES, SNS, Elastic Beanstalk

## Installation
Note: If you have the zip of this project, then skip the git clone command and extract the project.

```bash
$ git clone https://github.com/bits-pgp-fse/eon-backend.git
$ virtualenv <virtual_env_name_of_your_choice>
$ source <virtual_env_name_of_your_choice>/bin/activate
$ cd eon-backend
$ pip install -r requirements.txt
```

Note:  As this project requires celery for background tasks. Make sure it is running in a different terminal.

## Running Celery
```bash
$ celery worker -A eon_backend.celery:app --loglevel=INFO
``` 

## Postgres
```CREATE DATABASE eon;```

```CREATE USER bits_eon WITH PASSWORD 'password';```

```ALTER USER bits_eon WITH SUPERUSER;```


## Environment Variables

```
#DJANGO
SECRET_KEY=<something_very_secret>
ENCODE_KEY=<encoding_key>
DB_NAME=eon
DB_USERNAME=bits_eon
DB_PASSWORD=password
DB_HOSTNAME=localhost
DB_PORT=5432
PAYMENT_URL="http://localhost:8001/core/payment/"

#JWT
ACCESS_TOKEN_LIFETIME=1(day)
REFRESH_TOKEN_LIFETIME=2(days)

#AWS
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=
EMAIL_ID=<application_email_id>
ADMIN_EMAIL=<admin_email_id>
BUCKET=
BUCKET_PATH=
BROKER_URL=redis://localhost:6379
```

## Run Server

```bash
$ python3 manage.py migrate
$ python3 manage.py runserver
```

This project has some dependency on values in the database. So for this, load the data from fixtures:
```bash
$ python3 manage.py loaddata fixtures/roles.json
$ python3 manage.py loaddata fixtures/event_types.json
$ python3 manage.py loaddata fixtures/questions.json
```

Create super user to access Django admin:
```bash
$ python3 manage.py createsuperuser;
```

## Run Test (with coverage html, if you don't want cover html than remove --cover-html option from command)
```bash
$ python3 manage.py test --cover-html
```
Note: The index.html will be generated in the same repo under cover folder.

## Check Pylint Score
Run this command outside of project folder
```bash
$ pylint eon-backend --rcfile=eon-backend/.pylintrc
```

### Main Libraries Used

- Django:
  It is a Python-based free and open-source web framework, 
  which follows the model-template-view architectural pattern.
  
  https://docs.djangoproject.com/en/3.0/

- Django-Rest-Framework: 
  Django REST framework is a powerful and flexible toolkit for building Web APIs. 
  It gives us multiple features that combine deeply with Django's existing structures, 
  supporting us build RESTful HTTP resources that agree to the models.

  https://www.django-rest-framework.org/

- Boto: 
  It helps in building Python-based applications in the cloud, 
  converting application programming interface (API) responses from AWS into Python classes and vice-versa.

  https://boto3.amazonaws.com/v1/documentation/api/latest/index.html

- Grappelli: 
  To style and configure the Django admin interface we used grappelli. 
  Grappelli adds a consistent and grid-based look & feel.
  
  https://django-grappelli.readthedocs.io/
  
- Django Nose:
  To generate the test coverage of the project.
  
  https://django-testing-docs.readthedocs.io/en/latest/coverage.html
  
- Celery:
  To run the background processes.
  
  https://docs.celeryproject.org/en/stable/getting-started/introduction.html


### Folder Structure

Main Folder : eon-backend contains complete monolithic django project
It further includes: 
```
A basic django app contains following files:
models.py : All the models related to the module
urls.py  : Contains API urls list 
admin.py :  Configuration related to django admin for the module
tests.py : Contains test cases for the module
signals.py : Contains custom signals required pre/post any actions like post_save or pre_save
apps.py : This file registers any sub app with the main app here(eon-backend)
views.py : This file contains all the APIs and required all the logic related to them
serializers.py : Have custom classes used to serialize the data into django object
```

Comprising of these files this django app contains following modules(sub apps)
```
authentication: This module contains complete sub app for authentication including 

login
signup
password-reset
change-password

core: This module contains folders:
views_layer: This folder contains separate files for APIs of
Events
Feedback
Invitation
Notification
Subscription
User
Wishlist
tests: This folder contains test cases for all the above mentioned APIs files

Some Additional files in core
	
exceptions.py: Custom exceptions class
filters.py:  Custom filters for free/paid event
presigned_url.py: API to create/fetch presigned url
reports.py: Analysis reports for django admin template generated in this file
```


Other important folders in the main app includes:

```
eon_backend: Contains main settings file for the eon_backnd app & also urls for Core / Authentication

static: Contains common css & js files for django-admin template

templates: Contains related to event_analysis dashboard in django admin
``` 
