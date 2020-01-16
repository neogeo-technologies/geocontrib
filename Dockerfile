FROM python:3.8-slim-buster
LABEL maintainer="Benjamin Chartier at neogeo.fr"

ENV PYTHONUNBUFFERED=1
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal
ENV LC_ALL="C.UTF-8"
ENV LC_CTYPE="C.UTF-8"

# args
ARG APP_PATH
# not used ?
ARG GIT_BRANCH

# Set envs
ENV APP_PATH=$APP_PATH

RUN apt-get update && \
    apt-get install -y libproj-dev gdal-bin && \
    apt-get install -y --no-install-recommends netcat && \
    apt-get clean -y

RUN echo deb http://deb.debian.org/debian testing main contrib non-free >> /etc/apt/sources.list && \
    apt-get update && \
    apt-get remove -y binutils && \
    apt-get autoremove -y && \
    apt-get purge -y --auto-remove && \
    rm -rf /var/lib/apt/lists/*


RUN useradd -r -m apprunner
USER apprunner
ENV HOME=/home/apprunner
ENV PATH=$HOME/.local/bin:$PATH
# if WORKDIR only is set, then $APP_PATH will be owned by root :-/
RUN mkdir $APP_PATH
WORKDIR $APP_PATH

# Upgrade pip
RUN pip install --user --upgrade pip
# Install python requirements
COPY requirements.txt .
RUN pip install --user -r requirements.txt gunicorn
COPY --chown=apprunner . src/


EXPOSE 8000
ENTRYPOINT ["src/docker/docker-entrypoint.sh"]
CMD ["gunicorn", "-w 3", "-b 0.0.0.0:8000", "config.wsgi:application"]