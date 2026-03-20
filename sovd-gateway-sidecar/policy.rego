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
    "/discover",
    "/openapi.json",
    "/docs",
    "/redoc",
    "/health",
    "/status",
    "/refresh-docs"
}

# Allow public endpoints without authentication
allow if {
    input.attributes.request.http.path in public_endpoints
}

# Allow any path that starts with public endpoint
allow if {
    some endpoint in public_endpoints
    startswith(input.attributes.request.http.path, endpoint)
}

# Extract JWT claims from header
jwt_payload := payload if {
    header := input.attributes.request.http.headers["x-jwt-payload"]
    payload := json.unmarshal(base64url.decode(header))
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
    has_action(required_action)
}

# Allow admin role to access everything
allow if {
    jwt_payload
    valid_vin
    has_role("admin")
}

# Detailed decision for logging
decision := {
    "allow": allow,
    "jwt_present": jwt_payload != null,
    "vin_valid": valid_vin,
    "path": input.attributes.request.http.path,
    "method": input.attributes.request.http.method,
    "required_action": required_action_for_path(input.attributes.request.http.path, input.attributes.request.http.method)
}
