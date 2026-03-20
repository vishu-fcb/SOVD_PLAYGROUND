from fastapi import FastAPI

def collect_endpoints(app: FastAPI, base_url: str) -> list[dict]:
    """Collect all available endpoints from the FastAPI app."""
    endpoints = []

    for route in app.routes:
        if hasattr(route, "path"):
            endpoints.append({
                "path": route.path,
                "methods": list(route.methods or []),
                "url": f"{base_url.rstrip('/')}{route.path}"
            })

    return endpoints
