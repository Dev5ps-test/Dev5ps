# 1. Base Image를 Ubuntu 25.04로 변경 (ARM 아키텍처 명시)
FROM --platform=linux/arm64 ubuntu:25.04

# 2. JMeter 버전 및 환경 변수 설정
ENV JMETER_VERSION=5.4.1
ENV JMETER_HOME=/opt/apache-jmeter-${JMETER_VERSION}
ENV PATH=${JMETER_HOME}/bin:$PATH

# 3. 필수 패키지 및 Java 설치 (Ubuntu에는 Java가 없으므로 추가)
# Ubuntu 25.04에 맞춰 기본 JRE(default-jre-headless)를 설치합니다.
# 대화형 프롬프트를 방지하기 위해 DEBIAN_FRONTEND=noninteractive를 임시로 적용합니다.
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y wget unzip default-jre-headless && \
    rm -rf /var/lib/apt/lists/*

# 4. Apache JMeter 다운로드 및 압축 해제
RUN wget https://archive.apache.org/dist/jmeter/binaries/apache-jmeter-${JMETER_VERSION}.tgz && \
    tar -xzf apache-jmeter-${JMETER_VERSION}.tgz -C /opt/ && \
    rm apache-jmeter-${JMETER_VERSION}.tgz

# 5. 작업 디렉토리 설정
WORKDIR ${JMETER_HOME}

# 6. 기본 실행 명령어: JMeter Non-GUI 모드
CMD ["jmeter", "-n"]