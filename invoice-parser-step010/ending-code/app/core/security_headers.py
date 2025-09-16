"""
Security Headers Middleware

Provides comprehensive security headers to protect against common web vulnerabilities
including XSS, CSRF, clickjacking, and other attacks.
"""
import logging
from typing import Dict, Optional, List
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers to all responses."""
    
    def __init__(
        self,
        app,
        # Content Security Policy
        csp_policy: Optional[str] = None,
        # HSTS settings
        hsts_max_age: int = 31536000,  # 1 year
        hsts_include_subdomains: bool = True,
        hsts_preload: bool = True,
        # Frame options
        frame_options: str = "DENY",
        # Content type options
        content_type_options: bool = True,
        # XSS Protection
        xss_protection: str = "1; mode=block",
        # Referrer Policy
        referrer_policy: str = "strict-origin-when-cross-origin",
        # Permissions Policy
        permissions_policy: Optional[str] = None,
        # Additional custom headers
        custom_headers: Optional[Dict[str, str]] = None,
        # Environment-specific settings
        environment: str = "development"
    ):
        super().__init__(app)
        self.environment = environment
        self.custom_headers = custom_headers or {}
        
        # Build security headers
        self.security_headers = self._build_security_headers(
            csp_policy=csp_policy,
            hsts_max_age=hsts_max_age,
            hsts_include_subdomains=hsts_include_subdomains,
            hsts_preload=hsts_preload,
            frame_options=frame_options,
            content_type_options=content_type_options,
            xss_protection=xss_protection,
            referrer_policy=referrer_policy,
            permissions_policy=permissions_policy
        )
    
    def _build_security_headers(
        self,
        csp_policy: Optional[str],
        hsts_max_age: int,
        hsts_include_subdomains: bool,
        hsts_preload: bool,
        frame_options: str,
        content_type_options: bool,
        xss_protection: str,
        referrer_policy: str,
        permissions_policy: Optional[str]
    ) -> Dict[str, str]:
        """Build the security headers dictionary."""
        headers = {}
        
        # Content Security Policy
        if csp_policy:
            headers["Content-Security-Policy"] = csp_policy
        else:
            headers["Content-Security-Policy"] = self._get_default_csp_policy()
        
        # HTTP Strict Transport Security (HSTS)
        if self.environment == "production":
            hsts_value = f"max-age={hsts_max_age}"
            if hsts_include_subdomains:
                hsts_value += "; includeSubDomains"
            if hsts_preload:
                hsts_value += "; preload"
            headers["Strict-Transport-Security"] = hsts_value
        
        # X-Frame-Options (prevent clickjacking)
        headers["X-Frame-Options"] = frame_options
        
        # X-Content-Type-Options (prevent MIME type sniffing)
        if content_type_options:
            headers["X-Content-Type-Options"] = "nosniff"
        
        # X-XSS-Protection (legacy XSS protection)
        headers["X-XSS-Protection"] = xss_protection
        
        # Referrer-Policy
        headers["Referrer-Policy"] = referrer_policy
        
        # Permissions-Policy (formerly Feature-Policy)
        if permissions_policy:
            headers["Permissions-Policy"] = permissions_policy
        else:
            headers["Permissions-Policy"] = self._get_default_permissions_policy()
        
        # Cross-Origin Embedder Policy
        headers["Cross-Origin-Embedder-Policy"] = "require-corp"
        
        # Cross-Origin Opener Policy
        headers["Cross-Origin-Opener-Policy"] = "same-origin"
        
        # Cross-Origin Resource Policy
        headers["Cross-Origin-Resource-Policy"] = "same-site"
        
        # Cache Control for sensitive endpoints
        headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        headers["Pragma"] = "no-cache"
        headers["Expires"] = "0"
        
        # Server information hiding
        headers["Server"] = "InvoiceParser"
        
        return headers
    
    def _get_default_csp_policy(self) -> str:
        """Get default Content Security Policy."""
        if self.environment == "development":
            # More relaxed policy for development
            return (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval' http://localhost:* https://localhost:*; "
                "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
                "font-src 'self' https://fonts.gstatic.com; "
                "img-src 'self' data: blob: https:; "
                "connect-src 'self' http://localhost:* https://localhost:* ws://localhost:* wss://localhost:*; "
                "media-src 'self' data: blob:; "
                "object-src 'none'; "
                "base-uri 'self'; "
                "form-action 'self'; "
                "frame-ancestors 'none'; "
                "upgrade-insecure-requests"
            )
        else:
            # Strict policy for production
            return (
                "default-src 'self'; "
                "script-src 'self'; "
                "style-src 'self' https://fonts.googleapis.com; "
                "font-src 'self' https://fonts.gstatic.com; "
                "img-src 'self' data: blob: https:; "
                "connect-src 'self' https:; "
                "media-src 'self' data: blob:; "
                "object-src 'none'; "
                "base-uri 'self'; "
                "form-action 'self'; "
                "frame-ancestors 'none'; "
                "upgrade-insecure-requests"
            )
    
    def _get_default_permissions_policy(self) -> str:
        """Get default Permissions Policy."""
        return (
            "accelerometer=(), "
            "ambient-light-sensor=(), "
            "autoplay=(), "
            "battery=(), "
            "camera=(), "
            "cross-origin-isolated=(), "
            "display-capture=(), "
            "document-domain=(), "
            "encrypted-media=(), "
            "execution-while-not-rendered=(), "
            "execution-while-out-of-viewport=(), "
            "fullscreen=(), "
            "geolocation=(), "
            "gyroscope=(), "
            "keyboard-map=(), "
            "magnetometer=(), "
            "microphone=(), "
            "midi=(), "
            "navigation-override=(), "
            "payment=(), "
            "picture-in-picture=(), "
            "publickey-credentials-get=(), "
            "screen-wake-lock=(), "
            "sync-xhr=(), "
            "usb=(), "
            "web-share=(), "
            "xr-spatial-tracking=()"
        )
    
    def _should_apply_headers(self, request: Request) -> bool:
        """Determine if security headers should be applied to this request."""
        # Don't apply to static files
        if request.url.path.startswith("/static/"):
            return False
        
        # Don't apply to health checks (optional)
        if request.url.path in ["/health", "/api/health", "/api/v1/health"]:
            return False
        
        return True
    
    def _customize_headers_for_path(self, request: Request, headers: Dict[str, str]) -> Dict[str, str]:
        """Customize headers based on request path."""
        path = request.url.path
        customized_headers = headers.copy()
        
        # API endpoints - allow JSON responses
        if path.startswith("/api/"):
            # More relaxed CSP for API endpoints
            if self.environment == "development":
                customized_headers["Content-Security-Policy"] = (
                    "default-src 'self'; "
                    "script-src 'none'; "
                    "style-src 'none'; "
                    "img-src 'none'; "
                    "connect-src 'self'; "
                    "object-src 'none'; "
                    "base-uri 'none'; "
                    "form-action 'none'"
                )
            
            # Different cache policy for API
            if path.startswith("/api/health") or path.startswith("/api/metrics"):
                customized_headers["Cache-Control"] = "no-cache, max-age=0"
            else:
                customized_headers["Cache-Control"] = "no-store"
        
        # File upload endpoints
        if "upload" in path or "files" in path:
            # Allow file operations
            customized_headers["Content-Security-Policy"] += "; media-src 'self' blob: data:"
        
        # Authentication endpoints
        if "auth" in path:
            # Extra security for auth endpoints
            customized_headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
            customized_headers["Pragma"] = "no-cache"
        
        return customized_headers
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Add security headers to response."""
        # Process the request
        response = await call_next(request)
        
        # Check if we should apply headers
        if not self._should_apply_headers(request):
            return response
        
        # Get headers customized for this path
        headers_to_apply = self._customize_headers_for_path(request, self.security_headers)
        
        # Add custom headers
        headers_to_apply.update(self.custom_headers)
        
        # Apply headers to response
        for header_name, header_value in headers_to_apply.items():
            response.headers[header_name] = header_value
        
        # Log security headers application (debug level)
        logger.debug(f"Applied security headers to {request.method} {request.url.path}")
        
        return response


class CSPViolationReporter:
    """Handler for Content Security Policy violation reports."""
    
    @staticmethod
    async def handle_csp_report(request: Request):
        """Handle CSP violation reports."""
        try:
            report_data = await request.json()
            logger.warning(
                "CSP Violation Report",
                extra={
                    "csp_report": report_data,
                    "user_agent": request.headers.get("user-agent"),
                    "client_ip": request.client.host if request.client else None
                }
            )
        except Exception as e:
            logger.error(f"Failed to process CSP report: {e}")


def create_security_middleware(environment: str = "development", custom_config: Optional[Dict] = None) -> SecurityHeadersMiddleware:
    """Factory function to create security middleware with environment-specific settings."""
    config = custom_config or {}
    
    if environment == "production":
        return SecurityHeadersMiddleware(
            app=None,
            csp_policy=config.get("csp_policy"),
            hsts_max_age=config.get("hsts_max_age", 31536000),
            hsts_include_subdomains=config.get("hsts_include_subdomains", True),
            hsts_preload=config.get("hsts_preload", True),
            frame_options=config.get("frame_options", "DENY"),
            content_type_options=config.get("content_type_options", True),
            xss_protection=config.get("xss_protection", "1; mode=block"),
            referrer_policy=config.get("referrer_policy", "strict-origin-when-cross-origin"),
            permissions_policy=config.get("permissions_policy"),
            custom_headers=config.get("custom_headers"),
            environment=environment
        )
    else:
        # Development settings - more relaxed
        return SecurityHeadersMiddleware(
            app=None,
            csp_policy=config.get("csp_policy"),
            hsts_max_age=0,  # Disable HSTS in development
            hsts_include_subdomains=False,
            hsts_preload=False,
            frame_options=config.get("frame_options", "SAMEORIGIN"),  # More relaxed
            content_type_options=config.get("content_type_options", True),
            xss_protection=config.get("xss_protection", "1; mode=block"),
            referrer_policy=config.get("referrer_policy", "strict-origin-when-cross-origin"),
            permissions_policy=config.get("permissions_policy"),
            custom_headers=config.get("custom_headers"),
            environment=environment
        )


def get_security_headers_info() -> Dict[str, str]:
    """Get information about implemented security headers."""
    return {
        "Content-Security-Policy": "Prevents XSS and data injection attacks",
        "Strict-Transport-Security": "Enforces HTTPS connections",
        "X-Frame-Options": "Prevents clickjacking attacks",
        "X-Content-Type-Options": "Prevents MIME type sniffing",
        "X-XSS-Protection": "Legacy XSS protection",
        "Referrer-Policy": "Controls referrer information",
        "Permissions-Policy": "Controls browser feature access",
        "Cross-Origin-Embedder-Policy": "Isolates origin context",
        "Cross-Origin-Opener-Policy": "Prevents cross-origin attacks",
        "Cross-Origin-Resource-Policy": "Controls resource loading",
        "Cache-Control": "Prevents sensitive data caching"
    }


# Export security components
__all__ = [
    "SecurityHeadersMiddleware",
    "CSPViolationReporter",
    "create_security_middleware",
    "get_security_headers_info"
]
