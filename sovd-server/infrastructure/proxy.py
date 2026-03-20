"""Proxy functionality for SOVD server."""

import httpx
import logging

from fastapi import Request, HTTPException, Response

from infrastructure.registry import get_server_info

logger = logging.getLogger(__name__)

async def proxy_request(target_url: str, request: Request) -> Response:
    """Forward request to target service and return response."""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Prepare the request
            method = request.method
            url = target_url
            headers = dict(request.headers)

            # Remove host header to avoid conflicts
            headers.pop('host', None)

            # Get request body if present
            body = None
            if method in ['POST', 'PUT', 'PATCH']:
                body = await request.body()
                if body:
                    logger.info(f"Request body for {method} {url}: {body.decode('utf-8', errors='ignore')[:500]}")
                else:
                    logger.warning(f"No body found for {method} request to {url}")

            # Make the proxied request
            response = await client.request(
                method=method,
                url=url,
                headers=headers,
                content=body,
                params=request.query_params
            )

            # Prepare response headers
            response_headers = dict(response.headers)
            # Remove headers that shouldn't be forwarded
            response_headers.pop('content-encoding', None)
            response_headers.pop('transfer-encoding', None)

            # Return the response
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=response_headers,
                media_type=response_headers.get('content-type', 'application/json')
            )

    except httpx.TimeoutException:
        logger.error(f"Timeout when proxying request to {target_url}")
        raise HTTPException(status_code=504, detail="Gateway timeout")
    except httpx.ConnectError:
        logger.error(f"Connection error when proxying request to {target_url}")
        raise HTTPException(status_code=502, detail="Bad gateway - service unavailable")
    except Exception as e:
        logger.error(f"Error proxying request to {target_url}: {e}")
        raise HTTPException(status_code=502, detail="Bad gateway")

async def proxy_request_for_app(request: Request, app_name: str, path: str):
    """Forward request to registered application by name."""
    app_info = get_server_info(app_name)
    if not app_info:
        raise HTTPException(status_code=404, detail=f"App '{app_name}' not found")

    app_url = app_info.get("url")
    if not app_url:
        raise HTTPException(status_code=502, detail=f"App '{app_name}' has no URL configured")

    # Construct the full target URL
    target_url = f"{app_url}{path}"

    logger.info(f"Proxying {request.method} for '{app_name}' to {target_url}")

    return await proxy_request(target_url, request)
