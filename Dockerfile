FROM django
EXPOSE 8000
CMD ["cd", "onlinejudge", "python", "manage.py", "runserver"]  