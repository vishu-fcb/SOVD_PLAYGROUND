"""Filesystem monitoring endpoints"""

import psutil
from fastapi import APIRouter, HTTPException
from .datatypes import FilesystemResponse

router = APIRouter()

@router.get("/fs",
    response_model=FilesystemResponse,
    summary="Get filesystem information",
    description="Returns detailed filesystem information including filesystem type, mount options, and disk usage statistics (total, used, free space) for all mounted filesystems for storage monitoring",
    tags=["Filesystem"]
)
def get_filesystems():
    """Get filesystem information and disk usage"""
    filesystems = []
    for part in psutil.disk_partitions(all=False):
        filesystems.append({
            "mountpoint": part.mountpoint,
            "fstype": part.fstype,
            "opts": part.opts,
            "usage": psutil.disk_usage(part.mountpoint)._asdict()
        })
    return {"filesystems": filesystems}
