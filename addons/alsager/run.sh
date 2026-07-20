#!/usr/bin/with-contenv bashio
# ==============================================================================
# Alsager Add-on entrypoint
# Starts the FastAPI service via uvicorn inside the HA add-on container (s6).
# ==============================================================================

VERSION="0.3.0"
bashio::log.info "Starting Alsager add-on v${VERSION}"

cd /app || exit 1

# Home Assistant connection:
#  - In a normal add-on install, the Supervisor injects SUPERVISOR_TOKEN and
#    SUPERVISOR_URL automatically. The app uses these to reach HA at
#    ${SUPERVISOR_URL}/core/api (no manual config needed).
#  - Optionally the user can set ha_base_url / ha_token in the add-on options
#    (advanced/manual setups). These are passed through to the app.
if bashio::config.has_value 'ha_base_url'; then
  export HA_BASE_URL="$(bashio::config 'ha_base_url')"
fi
if bashio::config.has_value 'ha_token'; then
  export HA_LONG_LIVED_TOKEN="$(bashio::config 'ha_token')"
fi
if bashio::config.has_value 'poll_interval'; then
  export ALSAGER_POLL_INTERVAL="$(bashio::config 'poll_interval')"
fi

# Persistence paths (HA mounts /data and /config).
export ALSAGER_DATA_DIR="/data"
export ALSAGER_CONFIG_DIR="/config/alsager"

exec python -m uvicorn src.main:app \
    --host 0.0.0.0 \
    --port 5000 \
    --log-level info
