FROM django
EXPOSE 8000
CMD ["python", "onlinejudge/manage.py", "runserver"]  