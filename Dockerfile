FROM python:latest

RUN pip install git+git://github.com/Supervisor/supervisor.git@f99d017de2e921c8e6e12b64525ca306ce18bfa9
RUN pip install gunicorn

ADD supervisor.conf /etc/supervisor.conf
ADD src/ /data

RUN pip install -r /data/requirements.txt

EXPOSE 5000

CMD supervisord -c /etc/supervisor.conf -n
