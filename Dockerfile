FROM django
EXPOSE 8000
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt
CMD ["python", "conlinejudge\manage.py", "runserver"]