"""SOVD AC Control Router - Vehicle air conditioning system endpoints"""

from fastapi import APIRouter
from . import logs, configuration, data, faults, operations

sovd_router = APIRouter()

sovd_router.include_router(logs.router)
sovd_router.include_router(configuration.router)
sovd_router.include_router(data.router)
sovd_router.include_router(faults.router)
sovd_router.include_router(operations.router)
