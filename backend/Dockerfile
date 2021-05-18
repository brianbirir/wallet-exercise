FROM python:3.9.5-buster

# set environment variables
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# set working directory
WORKDIR /app

# copy project
COPY . /app

# install dependencies
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt