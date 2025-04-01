FROM python:3.13.2-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

# Keep the container running
CMD ["tail", "-f", "/dev/null"]