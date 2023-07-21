FROM redis:alpine AS fortune-cookies-chef

RUN apk update; apk add --no-cache fortune

CMD redis-cli -h $REDIS_HOST -p $REDIS_PORT RPUSH "fortune_cookies" "$(fortune $FORTUNE_CATEGORY)"

FROM redis:alpine AS fortune-cookies-takeaway-customer

CMD redis-cli -h $REDIS_HOST -p $REDIS_PORT LPOP "fortune_cookies"

FROM python:3-alpine AS fortune-cookies-delivery-customer

EXPOSE 80

RUN mkdir -p /var/www/app

WORKDIR /var/www/app

COPY fortune-cookie-delivery.py /var/www/app
COPY requirements.txt /var/www/app

RUN pip install flask redis

CMD python fortune-cookie-delivery.py
