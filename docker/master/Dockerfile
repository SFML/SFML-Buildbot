FROM debian:stable-slim

RUN apt-get update && apt-get install --no-install-recommends -y \
    python3-pip \
    python3-docker \
    python3-setuptools \
    libcairo2 \
    zip \
    unzip \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm /usr/lib/python3.*/EXTERNALLY-MANAGED \
    && pip3 install "buildbot[bundle]" "sqlalchemy==1.3.24" buildbot-badges txrequests

EXPOSE 9989/tcp

WORKDIR /home/buildbot

ENTRYPOINT ["buildbot", "start", "--nodaemon", "/home/buildbot"]
