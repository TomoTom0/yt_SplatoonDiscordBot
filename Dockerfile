FROM python:3.8
RUN sudo apt update && \
    sudo apt upgrade -y && \
    sudo apt install -y git
WORKDIR /app
RUN git clone https://github.com/frozenpandaman/s3s.git && \
    pip install -r requirements.txt && \
    pip install -r s3s/requirements.txt
COPY . /app

ENV SPLATOON_DISCORD_BOT_NOTICED_CHANNELS_MAIN ""
ENV SPLATOON_DISCORD_BOT_NOTICED_CHANNELS_TEST ""
ENV SPLATOON_DISCORD_BOT_TOKEN ""

CMD python3 src/main.py