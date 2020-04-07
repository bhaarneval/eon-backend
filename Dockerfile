FROM python:3
COPY . /app
WORKDIR /app
EXPOSE 8000
RUN pip3 install -r requirements.txt
RUN python3 manage.py migrate
CMD ["python3" "manage.py", "runserver", "0.0.0.0:8000"]
