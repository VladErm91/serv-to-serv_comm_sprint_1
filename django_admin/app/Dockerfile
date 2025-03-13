FROM python:3.10

WORKDIR /opt/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV UWSGI_PROCESSES 1
ENV UWSGI_THREADS 16
ENV UWSGI_HARAKIRI 240
ENV DJANGO_SETTINGS_MODULE 'config.settings'

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip \
    && pip install -r requirements.txt --no-cache

COPY . .

RUN mkdir -p /opt/app/staticfiles /opt/app/uploads \
    && chmod 755 run_uwsgi.sh \
    && chmod -R 777 /opt/app/staticfiles /opt/app/uploads \
    && chown -R www-data:www-data /opt/app

EXPOSE 8081

ENTRYPOINT ["sh", "-c", "chmod +x /opt/app/run_uwsgi.sh && /opt/app/run_uwsgi.sh"]