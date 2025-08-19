FROM ubuntu:latest
LABEL authors="Rafael"

ENTRYPOINT ["top", "-b"]