FROM ubuntu:18.04
MAINTAINER garimavkarma2014@gmail.com

RUN apt-get update -y
RUN apt-get install python3-pip -y
RUN apt-get install gunicorn3 -y

COPY requirement.txt requirement.txt
COPY app /opt/

RUN pip3 install -r requirement.txt
WORKDIR /opt/

CMD ["gunicorn3","-b","0.0.0.0:8000", "app/classify_data:app"]
