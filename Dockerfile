FROM python:3.7-alpine
LABEL maintainer="Yui Yukihria (yuiyukihria@pm.me)"
EXPOSE 8080
COPY setup /setup
RUN sh /setup/setup.sh
COPY src /src
ENTRYPOINT ["python3.7"]
CMD ["/src/rest/main.py", "&"]
ARG snowflake_url
ENV SNOWFLAKE_URL=$snowflake_url
ARG database_url
ENV DATABASE_URL=$database_url
