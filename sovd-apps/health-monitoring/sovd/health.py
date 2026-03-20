"""System health monitoring endpoints"""

import psutil, time, platform
from fastapi import APIRouter, HTTPException
from .datatypes import HealthResponse

BOOT_TIME = psutil.boot_time()
router = APIRouter()


@router.get("/health",
    response_model=HealthResponse,
    summary="Get system health metrics",
    description="Returns comprehensive system health metrics including CPU usage, memory statistics, platform information, and system uptime for monitoring overall system performance",
    tags=["Health"]
)
def get_health():
    """Get system health metrics"""
    uptime = time.time() - BOOT_TIME
    return {
        "system": platform.system(),
        "release": platform.release(),
        "machine": platform.machine(),
        "cpu": {
            "count": psutil.cpu_count(),
            "load_percent": psutil.cpu_percent(interval=0.5)
        },
        "memory": psutil.virtual_memory()._asdict(),
        "uptime_seconds": int(uptime)
    }
