web: python manage.py migrate --noinput && python manage.py setup_roles && gunicorn boutique_management.wsgi:application --bind 0.0.0.0:$PORT
