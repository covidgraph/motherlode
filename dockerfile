FROM python:3.6


RUN mkdir -p /app/motherlode
WORKDIR /app/motherlode

COPY requirement.txt ./
RUN pip install --no-cache-dir -r requirement.txt
COPY motherlode .

CMD [ "python3", "main.py" ]