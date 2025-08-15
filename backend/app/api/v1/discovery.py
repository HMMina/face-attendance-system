"""
API endpoint for mDNS service discovery
"""
from fastapi import APIRouter
from app.services.discovery_service import get_mdns_info

router = APIRouter()

@router.get("/mdns")
def mdns_info():
    return get_mdns_info()
