# base image for flask application
FROM python:3.11-slim

# set working directory
WORKDIR /app
# copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy other files
COPY . .

# expose the port
EXPOSE 8000

# tie the gunicorn to flask app
CMD ["gunicorn", "--workers", "3", "--threads", "2", "--bind", "0.0.0.0:8000", "app:app"]


