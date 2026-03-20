"""AC control logging endpoints"""

from fastapi import APIRouter
from .model import diagnostic_app
from .datatypes import LogEntry, LogList, LogItem

router = APIRouter()

@router.get("/logs",
    response_model=LogList,
    summary="Get application logs",
    description="Returns all log entries from the AC control application including timestamps and event descriptions for climate system diagnostics and troubleshooting",
    tags=["Logs"]
)
def get_logs():
    """Get all application logs"""
    log_dicts = diagnostic_app.get_logs()
    log_items = [LogItem(**log_dict) for log_dict in log_dicts]
    return {"logs": log_items}

@router.post("/logs",
    response_model=LogEntry,
    summary="Add log entry",
    description="Add a new log entry with event description to the AC control application log for tracking climate system operational events",
    tags=["Logs"]
)
def add_log(entry: LogEntry):
    """Add a new log entry"""
    diagnostic_app.add_log(entry.event)
    return entry
