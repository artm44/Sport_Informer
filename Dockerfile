FROM python:3.12-alpine

WORKDIR /app

COPY requirements.txt /app/

RUN pip3 install --no-cache-dir -r requirements.txt

COPY . /app

CMD ["python3", "main.py"]