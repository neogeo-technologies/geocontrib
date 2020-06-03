FROM nginx

COPY entrypoint.sh /
COPY conf.d/geocontrib.template /etc/nginx/conf.d/geocontrib.template

ENTRYPOINT ["/entrypoint.sh"]
CMD ["nginx", "-g", "daemon off;"]
