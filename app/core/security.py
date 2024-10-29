"""Security configuration."""

# Allowing all origins with credentials for simplicity of the test project
CORS_CONFIG = {
    "allow_origins": ["*"],
    "allow_credentials": True,
    "allow_methods": ["GET"],
    "allow_headers": ["*"],
}
