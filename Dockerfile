FROM ubuntu:latest

RUN apt update
RUN apt install python3.10 -y
RUN apt install python3-pip -y

WORKDIR /opt/dvmn_notifications

COPY . ./

RUN pip install -r requirements.txt

CMD ["python3.10", "./main.py"]