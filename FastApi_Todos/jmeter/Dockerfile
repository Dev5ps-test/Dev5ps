# 모든 일반 Ubuntu 서버(Intel/AMD)에서 동작하도록 amd64로 지정
FROM --platform=linux/amd64 ubuntu:25.04

ENV JMETER_VERSION=5.4.1
ENV JMETER_HOME=/opt/apache-jmeter-${JMETER_VERSION}
ENV PATH=${JMETER_HOME}/bin:$PATH

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y wget unzip default-jre-headless && \
    rm -rf /var/lib/apt/lists/*

RUN wget https://archive.apache.org/dist/jmeter/binaries/apache-jmeter-${JMETER_VERSION}.tgz && \
    tar -xzf apache-jmeter-${JMETER_VERSION}.tgz -C /opt/ && \
    rm apache-jmeter-${JMETER_VERSION}.tgz

WORKDIR ${JMETER_HOME}

CMD ["jmeter", "-n"]