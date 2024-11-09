FROM mysql:8.0

COPY docker/mysql/my.cnf /etc/mysql/conf.d/
COPY docker/mysql/init.sql /docker-entrypoint-initdb.d/

# Set the default authentication plugin to caching_sha2_password
# RUN echo "default_authentication_plugin=caching_sha2_password" >> /etc/mysql/conf.d/docker.cnf