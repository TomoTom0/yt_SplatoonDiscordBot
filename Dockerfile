FROM node:alpine

WORKDIR /app
RUN apt-get update
RUN apt-get -y upgrade -y
RUN apt-get -y install -y python3.8 python3-pip
RUN npm install -g @railway/cli
COPY requirements.txt /app/
RUN pip install -r /app/requirements.txt
RUN git clone https://github.com/frozenpandaman/s3s.git
RUN pip install -r /app/s3s/requirements.txt
COPY . /app

CMD python3 src/main.py