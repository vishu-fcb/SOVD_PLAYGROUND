"""Network interface monitoring endpoints"""

import psutil
from fastapi import APIRouter, HTTPException
from .datatypes import NetworkStatsResponse

router = APIRouter()

@router.get("/net",
    response_model=NetworkStatsResponse,
    summary="Get network interfaces",
    description="Returns comprehensive network interface information including status (up/down), speed, and IP addresses for all network interfaces for network diagnostics",
    tags=["Network"]
)
def get_network_info():
    """Get network interface information"""
    stats = psutil.net_if_stats()
    addrs = psutil.net_if_addrs()

    return {
        "interfaces": {
            iface: {
                "is_up": stats[iface].isup,
                "speed": stats[iface].speed,
                "addresses": [addr.address for addr in addrs[iface]]
            }
            for iface in stats
        }
    }
