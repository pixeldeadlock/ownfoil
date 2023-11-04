FROM python:3.11-alpine

RUN mkdir /app

COPY ./app /app
COPY ./conf/nginx.conf /app/conf/nginx.conf

COPY requirements.txt /tmp/
RUN apk add --update --no-cache bash nginx apache2-utils sudo && \
    pip install --requirement /tmp/requirements.txt && \
    rm /tmp/requirements.txt

RUN set -e \
      && ln -sf /dev/stdout /var/log/nginx/access.log \
      && ln -sf /dev/stderr /var/log/nginx/error.log

EXPOSE 80
ENTRYPOINT [ "/app/run.sh" ]