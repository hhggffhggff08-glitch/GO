FROM python:3.10-slim

WORKDIR /app

# تحديث setuptools أولاً
RUN pip install --upgrade pip setuptools wheel

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "render_server.py"]