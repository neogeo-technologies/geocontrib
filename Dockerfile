FROM python:3.7-slim-buster
MAINTAINER Benjamin Chartier at neogeo.fr

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal
ENV LC_ALL="C.UTF-8"
ENV LC_CTYPE="C.UTF-8"

# args
ARG APP_PATH
ARG SRC
ARG GIT_BRANCH

# Set envs
ENV APP_PATH=$APP_PATH
ENV SRC=$SRC

RUN apt-get update && \
    apt-get install -y libproj-dev gdal-bin && \
    apt-get clean -y

RUN echo deb http://deb.debian.org/debian testing main contrib non-free >> /etc/apt/sources.list && \
    apt-get update && \
    apt-get remove -y binutils && \
    apt-get autoremove -y

# Install netcat
RUN apt-get update \
 && apt-get install -y --no-install-recommends netcat \
 && apt-get purge -y --auto-remove \
 && rm -rf /var/lib/apt/lists/*

# Copie des sources
RUN mkdir -p $APP_PATH/$SRC
COPY . $APP_PATH/$SRC

# Upgrade pip
RUN pip install --upgrade pip

# Install python requirements
RUN pip install -r $APP_PATH/$SRC/requirements.txt
RUN pip install gunicorn

WORKDIR $APP_PATH

EXPOSE 8000
