FROM django
EXPOSE 8000
RUN pip install -r requirements.txt
RUN mkdir -p /user/src/app-onlinejudge
WORKDIR /user/src/app-onlinejudge
RUN cd conlinejudge
CMD ["python", "manage.py", "runserver"]  