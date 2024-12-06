FROM python:3.12
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV APP_HOME=/code
WORKDIR $APP_HOME
RUN mkdir -p $APP_HOME/static
COPY requirements.txt $APP_HOME/
RUN pip install --upgrade pip
RUN pip3 install -r $APP_HOME/requirements.txt
RUN python manage.py collectstatic --noinput