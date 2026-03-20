import asyncio
import logging
import httpx

from fastapi import FastAPI
from .collect_endpoints import collect_endpoints

logger = logging.getLogger(__name__)

async def register_with_server(server_url: str, app_url: str, app: FastAPI, max_retries: int = 5, delay: int = 2):
    """Register the app with the SOVD server, retrying with exponential backoff."""
    payload = {
        "name": app.title.lower().replace(" ", "-"),
        "url": app_url,
        "type": "app",
        "endpoints": collect_endpoints(app, app_url),
        "metadata": {
            "title": app.title,
            "version": app.version,
            "description": app.description,
            "supported_identifiers": []
        }
    }

    for attempt in range(1, max_retries + 1):
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.post(f"{server_url}/register", json=payload)
                if resp.status_code == 422:
                    logger.error(f"Registration failed with 422: {resp.json()}")
                resp.raise_for_status()
            logger.info("Successfully registered with SOVD server.")
            return True
        except Exception as e:
            logger.warning(f"Registration attempt {attempt} failed: {e}")
            if attempt == max_retries:
                logger.error(f"Could not register after {max_retries} attempts.")
                return False
            await asyncio.sleep(delay)
            delay *= 2
