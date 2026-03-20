"""SOVD Health Monitoring Router - System diagnostics endpoints"""

from fastapi import APIRouter
from . import health, proc, net, fs

# Main SOVD router for health monitoring services
sovd_router = APIRouter()

sovd_router.include_router(health.router)
sovd_router.include_router(proc.router)
sovd_router.include_router(net.router)
sovd_router.include_router(fs.router)
