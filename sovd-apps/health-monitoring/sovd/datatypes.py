from typing import Optional, List, Dict, Any
from pydantic import BaseModel

# HEALTH RESPONSE SCHEMAS
class CpuInfo(BaseModel):
    """CPU information"""
    count: int
    load_percent: float

class MemoryInfo(BaseModel):
    """Memory information"""
    total: int
    available: int
    percent: float
    used: int
    free: int
    active: Optional[int] = None
    inactive: Optional[int] = None
    buffers: Optional[int] = None
    cached: Optional[int] = None
    shared: Optional[int] = None
    slab: Optional[int] = None

class HealthResponse(BaseModel):
    """System health metrics response"""
    system: str
    release: str
    machine: str
    cpu: CpuInfo
    memory: MemoryInfo
    uptime_seconds: int
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "system": "Linux",
                    "release": "5.15.0-1234-generic",
                    "machine": "x86_64",
                    "cpu": {
                        "count": 8,
                        "load_percent": 45.2
                    },
                    "memory": {
                        "total": 16777216000,
                        "available": 8388608000,
                        "percent": 50.0,
                        "used": 8388608000,
                        "free": 8388608000
                    },
                    "uptime_seconds": 86400
                }
            ]
        }
    }

class ProcessInfo(BaseModel):
    """Process information"""
    pid: int
    name: str
    status: str
    cpu_percent: Optional[float] = None
    memory_rss: Optional[int] = None

class ProcessListResponse(BaseModel):
    """Process list response"""
    processes: List[ProcessInfo]
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "processes": [
                        {
                            "pid": 1,
                            "name": "systemd",
                            "status": "running",
                            "cpu_percent": 0.1,
                            "memory_rss": 8192000
                        },
                        {
                            "pid": 1234,
                            "name": "python",
                            "status": "running",
                            "cpu_percent": 2.5,
                            "memory_rss": 51200000
                        }
                    ]
                }
            ]
        }
    }

class ProcessDetailResponse(BaseModel):
    """Detailed process information"""
    pid: int
    name: str
    cmdline: List[str]
    status: str
    cpu_times: Dict[str, Any]
    memory_info: Dict[str, Any]
    create_time: str
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "pid": 1234,
                    "name": "python",
                    "cmdline": ["python", "-m", "uvicorn", "main:app"],
                    "status": "running",
                    "cpu_times": {
                        "user": 12.5,
                        "system": 3.2
                    },
                    "memory_info": {
                        "rss": 51200000,
                        "vms": 102400000
                    },
                    "create_time": "2025-10-21T10:30:00Z"
                }
            ]
        }
    }

class NetworkInterfaceInfo(BaseModel):
    """Network interface information"""
    is_up: bool
    speed: int
    addresses: List[str]

class NetworkStatsResponse(BaseModel):
    """Network statistics response"""
    interfaces: Dict[str, NetworkInterfaceInfo]
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "interfaces": {
                        "lo": {
                            "is_up": True,
                            "speed": 0,
                            "addresses": ["127.0.0.1", "::1", "00:00:00:00:00:00"]
                        },
                        "eth0": {
                            "is_up": True,
                            "speed": 1000,
                            "addresses": ["192.168.1.100", "aa:bb:cc:dd:ee:ff"]
                        }
                    }
                }
            ]
        }
    }

class DiskUsage(BaseModel):
    """Disk usage information"""
    total: int
    used: int
    free: int
    percent: float

class FilesystemInfo(BaseModel):
    """Filesystem information"""
    mountpoint: str
    fstype: str
    opts: str
    usage: DiskUsage

class FilesystemResponse(BaseModel):
    """Filesystem statistics response"""
    filesystems: List[FilesystemInfo]
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "filesystems": [
                        {
                            "mountpoint": "/",
                            "fstype": "ext4",
                            "opts": "rw,relatime",
                            "usage": {
                                "total": 107374182400,
                                "used": 53687091200,
                                "free": 53687091200,
                                "percent": 50.0
                            }
                        }
                    ]
                }
            ]
        }
    }

class Problem(BaseModel):
    """RFC 7807 Problem Details for HTTP APIs"""
    type: str = "about:blank"
    title: str
    status: int
    detail: Optional[str] = None
    instance: Optional[str] = None
