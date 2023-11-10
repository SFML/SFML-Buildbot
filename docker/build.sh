#!/bin/bash

DOCKER_BUILDKIT=1

docker build -t buildbot-worker-debian - < debian/Dockerfile
docker build -t buildbot-worker-android - < android/Dockerfile
docker build --build-arg COVERITY_TOKEN=$COVERITY_TOKEN --build-arg SONAR_TOKEN=$SONAR_TOKEN -t buildbot-worker-coverity - < coverity/Dockerfile
