FROM django
EXPOSE 8000
WORKDIR /app
COPY . /app
RUN ls
CMD ["python", "manage.py", "runserver"]  