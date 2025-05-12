FROM python:3.13-alpine

ENV PIP_ROOT_USER_ACTION=ignore

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY . /code/app

CMD ["python", "app/main.py"]
