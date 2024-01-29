FROM django
EXPOSE 8000
CMD ["python", "manage.py", "runserver"]  