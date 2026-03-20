package envoy.authz

import rego.v1

# Default deny
default allow := false

# Allow OPTIONS requests (CORS preflight)
allow if {
    input.attributes.request.http.method == "OPTIONS"
}

# Public endpoints that don't require authentication
public_endpoints := {
    "/",
    "/discover",
    "/openapi.json",
    "/docs",
    "/redoc",
    "/health",
    "/status",
    "/refresh-docs",
    "/servers",
    "/endpoint-mapping"
}

# Allow public endpoints without authentication - exact match only
allow if {
    input.attributes.request.http.path in public_endpoints
}

# Allow paths that start with /docs or /redoc (including query strings and static assets)
allow if {
    startswith(input.attributes.request.http.path, "/docs")
}

allow if {
    startswith(input.attributes.request.http.path, "/redoc")
}

allow if {
    startswith(input.attributes.request.http.path, "/openapi.json")
}

# Allow /app/{name} root paths (app listings)
allow if {
    regex.match(`^/app/[^/]+/?$`, input.attributes.request.http.path)
}

# Extract JWT claims from header
jwt_payload := payload if {
    header := input.attributes.request.http.headers["x-jwt-payload"]
    payload := json.unmarshal(base64url.decode(header))
}

# Fallback: extract JWT claims from Envoy dynamic metadata (gRPC ext_authz path)
jwt_payload := payload if {
    metadata := input.attributes.metadata_context
    filter_metadata := metadata.filter_metadata
    jwt_metadata := filter_metadata["envoy.filters.http.jwt_authn"]
    payload := jwt_metadata.sovd_token_payload
}

# Validate VIN in JWT token
valid_vin if {
    # Extract VIN from authorization_details structure
    some detail in jwt_payload.authorization_details
    some resource in detail.resources
    # Allow wildcard VIN for developers/admins
    resource.vin == "*"
}

valid_vin if {
    # Extract VIN from authorization_details structure
    some detail in jwt_payload.authorization_details
    some resource in detail.resources
    # Allow specific VIN
    resource.vin == "WVWZZZ1JZXW000000"
}

# Check if user has required SOVD action
has_action(required_action) if {
    some detail in jwt_payload.authorization_details
    some action in detail.actions
    action == required_action
}

# Check if user has required role
has_role(required_role) if {
    some role in jwt_payload.roles
    role == required_role
}

# Pattern-based authorization rules
# Maps path patterns and HTTP methods to required SOVD actions

# Helper function to extract resource type from path
# e.g., "/app/ac-control/logs" -> "logs"
resource_from_path(path) := resource if {
    parts := split(path, "/")
    count(parts) >= 4
    resource := parts[3]  # /app/{app-name}/{resource}/...
}

# Authorization rules mapping: [resource_type, http_method] -> sovd_action
authorization_rules := {
    # Special case: health-monitoring app (all endpoints)
    "health-monitoring": {"GET": "sovd:health-monitoring:read"},
    
    # Standard SOVD resources across all apps
    "logs": {
        "GET": "sovd:logs:read",
        "POST": "sovd:logs:write"
    },
    "configuration": {
        "GET": "sovd:configuration:read",
        "PUT": "sovd:configuration:write"
    },
    "data": {
        "GET": "sovd:data:read",
        "PUT": "sovd:data:write"
    },
    "faults": {
        "GET": "sovd:faults:read",
        "DELETE": "sovd:faults:write"
    },
    "operations": {
        "GET": "sovd:operations:read",
        "POST": "sovd:operations:exec"
    }
}

# Determine required action based on path pattern and HTTP method
required_action_for_path(path, method) := action if {
    # Health monitoring app - special handling
    contains(path, "/app/health-monitoring/")
    method == "GET"
    action := authorization_rules["health-monitoring"]["GET"]
} else := action if {
    # App root endpoints - GET /app/{name}/
    regex.match(`^/app/[^/]+/?$`, path)
    method == "GET"
    action := "sovd:meta:read"
} else := action if {
    # Dashboard endpoints - treat as data read
    contains(path, "-dashboard")
    method == "GET"
    action := "sovd:data:read"
} else := action if {
    # Gateway metadata endpoints - require meta:read
    path == "/servers"
    method == "GET"
    action := "sovd:meta:read"
} else := action if {
    path == "/endpoint-mapping"
    method == "GET"
    action := "sovd:meta:read"
} else := action if {
    # Server registration endpoint
    path == "/register-server"
    method == "POST"
    action := "sovd:meta:read"
} else := action if {
    # Standard SOVD resources - lookup in authorization_rules
    resource := resource_from_path(path)
    method_actions := authorization_rules[resource]
    action := method_actions[method]
}

# Allow authenticated requests with proper actions
allow if {
    jwt_payload
    valid_vin
    path := input.attributes.request.http.path
    method := input.attributes.request.http.method
    required_action := required_action_for_path(path, method)
    # Ensure required_action is defined (not null/undefined)
    required_action != null
    has_action(required_action)
}

# Allow admin role to access everything
allow if {
    jwt_payload
    has_role("admin")
}
