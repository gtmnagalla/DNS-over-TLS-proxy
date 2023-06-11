FROM python:alpine3.17

WORKDIR /usr/local/bin
COPY DNS-proxy.py .

EXPOSE 53/tcp
EXPOSE 53/udp

CMD ["python","DNS-proxy.py"]