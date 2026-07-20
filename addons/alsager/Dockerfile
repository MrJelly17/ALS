# Alsager Add-on — built by GitHub Actions (see .github/workflows/build.yml)
# and pushed to GHCR as ghcr.io/<owner>/alsager-<arch>:<version>.
#
# Home Assistant add-ons MUST be built on the HA base image, which provides
# s6-overlay and bashio (required by run.sh: #!/usr/bin/with-contenv bashio).
# The {arch} placeholder is substituted by the Supervisor at build time when
# building locally; in CI we pin an explicit arch base per matrix job.

ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base:dev
FROM ${BUILD_FROM}

# Disable Python buffering and set UTF-8
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    LANG=C.UTF-8 \
    PYTHONIOENCODING=UTF-8

# HA base is Alpine-based and ships without Python. Install python3 + pip.
RUN apk add --no-cache python3 py3-pip py3-virtualenv

WORKDIR /app

# Install Python dependencies
COPY requirements.txt /app/requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy add-on source
COPY . /app

# Expose the uvicorn port (also used by HA ingress)
EXPOSE 5000

# HA Supervisor runs this as the container command (s6 + bashio)
CMD ["/app/run.sh"]
