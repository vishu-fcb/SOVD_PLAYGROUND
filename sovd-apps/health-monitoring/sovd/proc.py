"""Process monitoring endpoints"""

import psutil, time
from fastapi import APIRouter, HTTPException
from .datatypes import ProcessListResponse, ProcessDetailResponse

router = APIRouter()

@router.get("/proc",
    response_model=ProcessListResponse,
    summary="List running processes",
    description="Returns all running processes with PID, name, status, CPU usage percentage, and memory usage for system-wide process monitoring and diagnostics",
    tags=["Processes"]
)
def list_processes():
    """List all running processes with resource usage"""
    procs = []
    for p in psutil.process_iter(attrs=["pid", "name", "status", "cpu_percent", "memory_info"]):
        try:
            info = p.info
            procs.append({
                "pid": info["pid"],
                "name": info["name"],
                "status": info["status"],
                "cpu_percent": info["cpu_percent"],
                "memory_rss": info["memory_info"].rss
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return {"processes": procs}

@router.get("/proc/{pid}",
    response_model=ProcessDetailResponse,
    summary="Get process details",
    description="Returns detailed process information by PID including command line arguments, CPU times, memory usage, status, and creation timestamp for in-depth process analysis",
    tags=["Processes"]
)
def get_process(pid: int):
    """Get detailed process information by PID"""
    try:
        p = psutil.Process(pid)
        return {
            "pid": p.pid,
            "name": p.name(),
            "cmdline": p.cmdline(),
            "status": p.status(),
            "cpu_times": p.cpu_times()._asdict(),
            "memory_info": p.memory_info()._asdict(),
            "create_time": time.strftime("%Y-%m-%d %H:%M:%S",
                                       time.localtime(p.create_time()))
        }
    except psutil.NoSuchProcess:
        raise HTTPException(404, detail=f"No process with PID {pid}")
