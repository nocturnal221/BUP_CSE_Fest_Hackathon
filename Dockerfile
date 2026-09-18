FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install python dependencies directly (all pre-compiled wheels)
COPY requirement.txt /app/
RUN pip install --no-cache-dir -r requirement.txt

# Copy backend application files
COPY . /app/

EXPOSE 8000

CMD ["sh", "-c", "python manage.py migrate && gunicorn --bind 0.0.0.0:8000 core.wsgi:application"]
