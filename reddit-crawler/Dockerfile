FROM python:3.13.2-slim

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

# Keep the container running
CMD ["tail", "-f", "/dev/null"]