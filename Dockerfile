FROM ubi9:latest
USER root
RUN yum install -y libGL git wget python3 python3-pip

WORKDIR /opt/app-root/src
COPY web web
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
RUN ln -s /opt/app-root/src/simplevis-data/detected-files/exp web/static

ENV ENVIRONMENT_NAME="RHEL+Podman"
ENV SIMPLEVIS_DATA=/opt/app-root/src/simplevis-data
ENV MODEL_SERVER=cvedge.davenet.local:8000

EXPOSE 5001
ENTRYPOINT ["/opt/app-root/src/web/main.py"]
