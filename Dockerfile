FROM python:3.10-slim
EXPOSE 8000
WORKDIR /app
COPY . /app
RUN pip install django
CMD ["python", "conlinejudge/manage.py", "runserver"]  