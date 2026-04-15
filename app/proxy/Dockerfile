FROM nginx:1.27-alpine

RUN apk add --no-cache gettext

COPY nginx.conf.template /etc/nginx/templates/default.conf.template

EXPOSE 80

ENV NGINX_SERVER_NAME=naturalsql.online \
    FRONTEND_UPSTREAM=naturalsql-client-ahpyii:80 \
    BACKEND_UPSTREAM=naturalsql-backend-9lrxni:8000

CMD ["/bin/sh", "-c", "envsubst '$NGINX_SERVER_NAME $FRONTEND_UPSTREAM $BACKEND_UPSTREAM' < /etc/nginx/templates/default.conf.template > /etc/nginx/conf.d/default.conf && exec nginx -g 'daemon off;'"]
