FROM ubi8/python-39:latest

USER root
RUN yum install -y libGL
RUN pip install flask requests bs4 flask_restful waitress

WORKDIR /opt/app-root/src
COPY web web
COPY requirements.txt requirements.txt
RUN mkdir uploaded-files
RUN mkdir detected-files
RUN pip install -r requirements.txt
RUN ln -s /opt/app-root/src/detected-files/exp web/static

ENV ENVIRONMENT_NAME="RHEL+Podman"

EXPOSE 5002
ENTRYPOINT ["/opt/app-root/src/web/main.py"]
