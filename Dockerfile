FROM django
EXPOSE 8000
RUN pip install -r requirements.txt
RUN cd conlinejudge
CMD ["python", "manage.py", "runserver"]  