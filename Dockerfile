FROM python:3.8

WORKDIR /app

COPY . /app

RUN apt-get update && \
    apt-get install -y libfreetype6-dev && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt

ENV LD_LIBRARY_PATH=/usr/local/lib

EXPOSE 80

CMD ["python", "main.py"]
