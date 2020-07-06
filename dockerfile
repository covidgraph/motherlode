FROM python:3.6


RUN mkdir -p /app/motherlode
WORKDIR /app/motherlode

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY motherlode .

CMD [ "python3", "main.py" ]