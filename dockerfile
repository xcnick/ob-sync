FROM python:3.11-alpine

RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.ustc.edu.cn/g' /etc/apk/repositories && \
    apk update && \
    apk add openssl-dev build-base python3-dev && \
    rm -rf /var/cache/apk/*

RUN pip config set global.index-url https://mirrors.bfsu.edu.cn/pypi/web/simple && \
    pip install --no-cache-dir -U pip

RUN pip install --no-cache-dir \
    fastapi \
    gunicorn \
    aiohttp \
    uvicorn \
    pyjwt \
    pony \
    scrypt \
    bcrypt \
    websockets

WORKDIR /workspace
