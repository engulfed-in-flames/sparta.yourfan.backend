FROM python:3.11-slim

EXPOSE 8000

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY . .

RUN apt-get update && apt-get install -y \
    libgirepository1.0-dev \
    # ubuntu-advantage-tools \
    # command-not-found \
    libdbus-1-dev \ 
    libsystemd-dev \
    libcairo2-dev libjpeg-dev libgif-dev \
    pkg-config \
    build-essential \
    libpq-dev \
    libvirt-dev \
    && rm -rf /var/lib/apt/lists/*

# RUN export PKG_CONFIG_PATH=/usr/lib/pkgconfig:/usr/share/pkgconfig
# RUN export PKG_CONFIG_PATH=/path/to/libvirt.pc/directory:$PKG_CONFIG_PATH

RUN python3 -m venv /opt/venv

RUN /opt/venv/bin/pip install pip --upgrade && \
    /opt/venv/bin/pip install -r requirements.txt && \
    chmod +x entrypoint.sh

CMD ["/app/entrypoint.sh"]
