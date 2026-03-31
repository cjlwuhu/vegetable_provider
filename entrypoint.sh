#!/bin/sh
set -e

echo "Waiting for MySQL..."

until python -c "
import os
import pymysql
pymysql.connect(
    host=os.getenv('MYSQL_HOST'),
    port=int(os.getenv('MYSQL_PORT', 3306)),
    user=os.getenv('MYSQL_USER'),
    password=os.getenv('MYSQL_PASSWORD'),
    database=os.getenv('MYSQL_DATABASE'),
)
print('MySQL is ready')
" >/dev/null 2>&1
do
  sleep 2
done

echo "Running migrations..."
flask --app run:app db upgrade

echo "Starting app..."
exec gunicorn -w 1 -b 0.0.0.0:5000 run:app