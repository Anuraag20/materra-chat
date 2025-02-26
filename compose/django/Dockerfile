FROM python:3.10-slim
 
RUN mkdir /app
WORKDIR /app
 
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1 
 
RUN pip install --upgrade pip 
 
COPY materra-django/requirements.txt  /app/
 
RUN pip install --no-cache-dir -r requirements.txt
 
COPY materra-django/ /app/
 
EXPOSE 8000
 
CMD ["python", "manage.py", "runserver", "0.0.0.0:80"]

