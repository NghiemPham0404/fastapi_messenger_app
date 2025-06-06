FROM python:3.11

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

COPY ./.env /code/.env

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app

COPY ./static /code/static

COPY ./templates /code/templates

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]