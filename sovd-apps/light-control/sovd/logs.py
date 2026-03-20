"""Light control logging endpoints"""

from fastapi import APIRouter
from .model import lightctrl
from .datatypes import LogEntry, LogList

router = APIRouter()

@router.get("/logs",
    response_model=LogList,
    summary="Get application logs",
    description="Returns all log entries from the light control application including timestamps and event descriptions for diagnostic and troubleshooting purposes",
    tags=["Logs"]
)
def get_logs():
    """Get all application logs"""
    return {"logs": lightctrl.get_logs()}

@router.post("/logs",
    response_model=LogEntry,
    summary="Add log entry",
    description="Add a new log entry with event description to the light control application log for tracking operational events and diagnostics",
    tags=["Logs"]
)
def add_log(entry: LogEntry):
    """Add a new log entry"""
    lightctrl.add_log(entry.dict().get("event"))
    return entry
