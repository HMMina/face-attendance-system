"""
mDNS service discovery logic (mock)
"""
from app.config.network_config import mdns_config

def get_mdns_info():
    # Mock mDNS info for MVP
    return {
        "service_name": mdns_config["service_name"],
        "service_type": mdns_config["service_type"],
        "port": mdns_config["port"],
        "status": "online"
    }
