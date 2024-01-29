FROM django
EXPOSE 8000
WORKDIR /app
COPY . /app
RUN ls
RUN cd conlinejudge
CMD ["python", "manage.py", "runserver"]  