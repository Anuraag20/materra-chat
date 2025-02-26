# Materra Chat

## Steps to deploy

1. Create compose/django/.env with the following structure:
```
DB_NAME=DB_NAME
DB_USER=DB_USER
DB_PASSWORD=DB_PASSWORD
DB_HOST=DB_HOST
DB_PORT=DB_PORT

DJANGO_SECRET_KEY=DJANGO_SECRET_KEY
DJANGO_DEBUG=DJANGO_DEBUG

REDIS_URL=redis://redis:6379
```

2. Create compose/fastapi/.env with the following structure:
```
LLM_API_KEY=LLM_API_KEY
LLM_BASE_URL=LLM_BASE_URL
```
3. Make sure to update the .env files with the correct values
4. Run the following commands:
```
docker compose build
docker compose up
```
