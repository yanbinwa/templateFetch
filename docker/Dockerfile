#FROM maven:3.3.9-jdk-8
FROM docker-reg.emotibot.com.cn:55688/python:yanbinwang

# Set TimeZone
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# set bundle version
ENV BUNDLE_VER=0.0.1-SNAPSHOT

# setup workspace
RUN mkdir -p /usr/src/template-fetch
WORKDIR /usr/src/template-fetch

COPY bin ./bin
COPY conf ./conf
COPY docker ./docker
COPY file ./file
COPY lib ./lib
COPY HelloWorld ./HelloWorld
COPY manage.py ./manage.py

# defaults
ENTRYPOINT ["bin/run.sh"]
