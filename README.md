# EOn-backend

This is a monolithic architecture django project for BITS EOn.

# Prerequisites

- Postgres Setup
- Redis

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

To setup the local postgres database use below commands in order
```bash
$ sudo -s s postgres;                                              -> connect with postgres
$ psql;
$ CREATE DATABASE <dbname>;                                        -> create a new DB
$ CREATE USER <username> WITH PASSWORD <password>;                 -> create a new postgres user for local
$ GRANT ALL PRIVILEGES ON DATABASE <dbname> TO USER <username>;    -> Grant all privileges to that user for new DB
```
Create SuperUser in local to access Django admin as:
```bash
$ python3 manage.py createsuperuser;
```

NOTE: To connect the django app with local Database use these credentials to set the environment variables


## Environment variables

```
#DJANGO
SECRET_KEY=<something_very_secret>
DB_NAME=<db_name_created_above>
DB_USERNAME=<db_user_created_above>
DB_PASSWORD=<db_password_created_above>
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

## Run Test (with coverage)
```bash
$ python manage.py test
```

## Check Pylint Score
Run this command outside of project folder
```bash
$ pylint eon-backend --rcfile=eon-backend/.pylintrc
```

### Main Libraries Used

- Django-Rest-Framework : Django REST framework is a powerful and flexible toolkit for building Web APIs. It gives us multiple features that combine deeply with Django's existing structures, supporting us build RESTful HTTP resources that agree to the models.

  https://www.django-rest-framework.org/

- Boto : It helps in building Python-based applications in the cloud, converting application programming interface (API) responses from AWS into Python classes.

  https://boto3.amazonaws.com/v1/documentation/api/latest/index.html

- Grappelli : 
  To style and configure the Django admin interface we used grappelli. Grappelli adds a consistent and grid-based look & feel
  
  https://django-grappelli.readthedocs.io/


### Folder Structure

Main Folder : eon-backend contains complete monolithic django project
It further includes: 
```
A basic django app contains following files:
models.py : All the models related to the module
urls.py  : Contains API urls list 
admin.py :  Configuration related to django admin for the module
tests.py : Contains test cases for the module
signals.py : Contains custom signals required pre/post any actions like save
apps.py : This file registers any sub app with the main app here(eon-backend)
views.py : This file contains all the APIs and required all the logic related to them
serializers.py : Have custom classes used to serialize the data into django object
```

Comprising of these files this django app contains following modules(sub apps)
```

authentication: This module contains complete sub app for authentication including 

login
signup
Password-reset
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

payment: Contains payment API based on monolithic architecture
``` 
