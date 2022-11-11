FROM python:3.10-slim

COPY ./requirements.txt /meal-tracker/requirements.txt

WORKDIR /meal-tracker

RUN pip3 install --upgrade pip

RUN pip3 install -r requirements.txt

COPY ./src /meal-tracker/

EXPOSE 5001

CMD ["python", "main.py"]