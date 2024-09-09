FROM mysql:8.0

COPY docker/mysql/my.cnf /etc/mysql/conf.d/
COPY docker/mysql/init.sql /docker-entrypoint-initdb.d/
