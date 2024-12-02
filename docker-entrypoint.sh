#!/bin/bash

while ! nc -z db 5432; do
  echo "Waiting for PostgreSQL..."
  sleep 1
done

PGPASSWORD=$DB_PASSWORD psql -h db -U $DB_USER -d postgres -tc "SELECT 1 FROM pg_database WHERE datname = '$DB_NAME'" | grep -q 1 || PGPASSWORD=$DB_PASSWORD psql -h db -U $DB_USER -d postgres -c "CREATE DATABASE $DB_NAME"

python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput

python manage.py shell << END
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username="${DJANGO_SUPERUSER_USERNAME}").exists():
    print("Creating superuser...")
    User.objects.create_superuser("${DJANGO_SUPERUSER_USERNAME}", "${DJANGO_SUPERUSER_EMAIL}", "${DJANGO_SUPERUSER_PASSWORD}")
    print("Superuser created successfully!")
END

exec "$@"
