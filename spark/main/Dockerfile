# tonyq2k3/task-submitter

FROM bitnami/spark:3.5.5-debian-12-r2

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app