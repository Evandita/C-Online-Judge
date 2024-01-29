FROM django
EXPOSE 8000
RUN ls
CMD ["python", "manage.py", "runserver"]  