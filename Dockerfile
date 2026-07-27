FROM python 3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip -r requirements.txt

COPY . .

CMD ["python", "run.py"]