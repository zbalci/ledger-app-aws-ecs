FROM amazonlinux:2023

RUN dnf install -y \
    mysql \
    awscli \
 && dnf clean all

ENTRYPOINT ["/bin/sh","-c"]