"""
Network & mDNS configuration
"""
from app.config.settings import settings

MDNS_SERVICE_NAME = settings.MDNS_SERVICE_NAME
MDNS_SERVICE_TYPE = settings.MDNS_SERVICE_TYPE
SERVER_PORT = settings.SERVER_PORT

# mDNS config for service discovery
mdns_config = {
    "service_name": MDNS_SERVICE_NAME,
    "service_type": MDNS_SERVICE_TYPE,
    "port": SERVER_PORT,
}
