FROM python:3.12

WORKDIR /app

COPY ./*.py .
COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "-u", "./sender.py"]
