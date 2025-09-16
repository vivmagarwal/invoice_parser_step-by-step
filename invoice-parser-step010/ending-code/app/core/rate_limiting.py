"""
Rate Limiting Middleware

Provides comprehensive rate limiting with different strategies and storage backends
to protect against abuse and ensure fair usage.
"""
import asyncio
import logging
import time
from abc import ABC, abstractmethod
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple, Any
from enum import Enum

from fastapi import Request, Response, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware

from app.models.api_responses import ErrorCodes

logger = logging.getLogger(__name__)


class RateLimitStrategy(str, Enum):
    """Rate limiting strategies."""
    FIXED_WINDOW = "fixed_window"
    SLIDING_WINDOW = "sliding_window"
    TOKEN_BUCKET = "token_bucket"
    LEAKY_BUCKET = "leaky_bucket"


class RateLimitScope(str, Enum):
    """Rate limiting scopes."""
    GLOBAL = "global"
    PER_IP = "per_ip"
    PER_USER = "per_user"
    PER_ENDPOINT = "per_endpoint"


class RateLimitBackend(ABC):
    """Abstract base class for rate limit storage backends."""
    
    @abstractmethod
    async def get_counter(self, key: str) -> Tuple[int, Optional[datetime]]:
        """Get current counter value and expiry time."""
        pass
    
    @abstractmethod
    async def increment_counter(self, key: str, window_seconds: int) -> int:
        """Increment counter and return new value."""
        pass
    
    @abstractmethod
    async def reset_counter(self, key: str):
        """Reset counter for key."""
        pass


class InMemoryRateLimitBackend(RateLimitBackend):
    """In-memory rate limit storage (not suitable for multi-instance deployments)."""
    
    def __init__(self):
        self._counters: Dict[str, Dict[str, Any]] = defaultdict(lambda: {"count": 0, "window_start": None})
        self._lock = asyncio.Lock()
    
    async def get_counter(self, key: str) -> Tuple[int, Optional[datetime]]:
        """Get current counter value and expiry time."""
        async with self._lock:
            data = self._counters[key]
            return data["count"], data["window_start"]
    
    async def increment_counter(self, key: str, window_seconds: int) -> int:
        """Increment counter and return new value."""
        async with self._lock:
            now = datetime.utcnow()
            data = self._counters[key]
            
            # Reset counter if window has expired
            if (data["window_start"] is None or 
                now - data["window_start"] > timedelta(seconds=window_seconds)):
                data["count"] = 0
                data["window_start"] = now
            
            data["count"] += 1
            return data["count"]
    
    async def reset_counter(self, key: str):
        """Reset counter for key."""
        async with self._lock:
            if key in self._counters:
                del self._counters[key]


class SlidingWindowRateLimitBackend(RateLimitBackend):
    """Sliding window rate limit implementation."""
    
    def __init__(self):
        self._requests: Dict[str, list] = defaultdict(list)
        self._lock = asyncio.Lock()
    
    async def get_counter(self, key: str) -> Tuple[int, Optional[datetime]]:
        """Get current counter value."""
        async with self._lock:
            requests = self._requests[key]
            return len(requests), None
    
    async def increment_counter(self, key: str, window_seconds: int) -> int:
        """Add request to sliding window and return current count."""
        async with self._lock:
            now = time.time()
            window_start = now - window_seconds
            
            # Clean old requests
            self._requests[key] = [req_time for req_time in self._requests[key] 
                                 if req_time > window_start]
            
            # Add current request
            self._requests[key].append(now)
            
            return len(self._requests[key])
    
    async def reset_counter(self, key: str):
        """Reset counter for key."""
        async with self._lock:
            if key in self._requests:
                del self._requests[key]


class RateLimitRule:
    """Defines a rate limiting rule."""
    
    def __init__(
        self,
        requests: int,
        window_seconds: int,
        scope: RateLimitScope = RateLimitScope.PER_IP,
        strategy: RateLimitStrategy = RateLimitStrategy.FIXED_WINDOW,
        paths: Optional[list] = None,
        methods: Optional[list] = None,
        exempt_ips: Optional[list] = None,
        exempt_users: Optional[list] = None
    ):
        self.requests = requests
        self.window_seconds = window_seconds
        self.scope = scope
        self.strategy = strategy
        self.paths = paths or []
        self.methods = methods or ["GET", "POST", "PUT", "DELETE", "PATCH"]
        self.exempt_ips = set(exempt_ips or [])
        self.exempt_users = set(exempt_users or [])
    
    def applies_to(self, request: Request) -> bool:
        """Check if rule applies to the request."""
        # Check HTTP method
        if request.method not in self.methods:
            return False
        
        # Check path patterns
        if self.paths:
            path = request.url.path
            if not any(pattern in path for pattern in self.paths):
                return False
        
        return True
    
    def is_exempt(self, request: Request, user_id: Optional[str] = None) -> bool:
        """Check if request is exempt from rate limiting."""
        # Check IP exemption
        client_ip = self._get_client_ip(request)
        if client_ip in self.exempt_ips:
            return True
        
        # Check user exemption
        if user_id and user_id in self.exempt_users:
            return True
        
        return False
    
    def get_rate_limit_key(self, request: Request, user_id: Optional[str] = None) -> str:
        """Generate rate limit key based on scope."""
        if self.scope == RateLimitScope.GLOBAL:
            return "global"
        elif self.scope == RateLimitScope.PER_IP:
            return f"ip:{self._get_client_ip(request)}"
        elif self.scope == RateLimitScope.PER_USER:
            return f"user:{user_id or 'anonymous'}"
        elif self.scope == RateLimitScope.PER_ENDPOINT:
            return f"endpoint:{request.method}:{request.url.path}"
        else:
            return f"ip:{self._get_client_ip(request)}"
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request."""
        # Check for forwarded headers (proxy/load balancer)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback to direct connection
        return request.client.host if request.client else "unknown"


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware."""
    
    def __init__(
        self,
        app,
        backend: Optional[RateLimitBackend] = None,
        rules: Optional[list] = None
    ):
        super().__init__(app)
        self.backend = backend or InMemoryRateLimitBackend()
        self.rules = rules or self._default_rules()
        
    def _default_rules(self) -> list:
        """Default rate limiting rules."""
        return [
            # Global rate limit - 1000 requests per hour
            RateLimitRule(
                requests=1000,
                window_seconds=3600,
                scope=RateLimitScope.GLOBAL,
                strategy=RateLimitStrategy.SLIDING_WINDOW
            ),
            
            # Per IP - 100 requests per minute
            RateLimitRule(
                requests=100,
                window_seconds=60,
                scope=RateLimitScope.PER_IP,
                strategy=RateLimitStrategy.SLIDING_WINDOW
            ),
            
            # Authentication endpoints - stricter limits
            RateLimitRule(
                requests=5,
                window_seconds=60,
                scope=RateLimitScope.PER_IP,
                paths=["/api/auth/login", "/api/auth/register"],
                strategy=RateLimitStrategy.FIXED_WINDOW
            ),
            
            # File upload - moderate limits
            RateLimitRule(
                requests=20,
                window_seconds=300,  # 5 minutes
                scope=RateLimitScope.PER_USER,
                paths=["/api/files/upload", "/api/parse-invoice", "/api/process-and-save"],
                methods=["POST"],
                strategy=RateLimitStrategy.SLIDING_WINDOW
            )
        ]
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Apply rate limiting to requests."""
        # Extract user ID if available
        user_id = await self._extract_user_id(request)
        
        # Check each rule
        for rule in self.rules:
            if not rule.applies_to(request):
                continue
            
            if rule.is_exempt(request, user_id):
                continue
            
            # Check rate limit
            rate_limit_key = rule.get_rate_limit_key(request, user_id)
            
            try:
                current_count = await self._check_rate_limit(rule, rate_limit_key)
                
                if current_count > rule.requests:
                    return await self._create_rate_limit_response(rule, current_count)
                
            except Exception as e:
                logger.error(f"Rate limiting error: {e}")
                # Continue on error to avoid blocking requests
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Remaining"] = "1"  # Simplified
        
        return response
    
    async def _check_rate_limit(self, rule: RateLimitRule, key: str) -> int:
        """Check rate limit for key."""
        if rule.strategy == RateLimitStrategy.SLIDING_WINDOW:
            backend = SlidingWindowRateLimitBackend() if not hasattr(self, '_sliding_backend') else self._sliding_backend
            if not hasattr(self, '_sliding_backend'):
                self._sliding_backend = backend
            return await backend.increment_counter(key, rule.window_seconds)
        else:
            return await self.backend.increment_counter(key, rule.window_seconds)
    
    async def _extract_user_id(self, request: Request) -> Optional[str]:
        """Extract user ID from request if authenticated."""
        try:
            auth_header = request.headers.get('authorization', '')
            if auth_header.startswith('Bearer '):
                from app.core.security import verify_token
                token = auth_header.split(' ')[1]
                payload = verify_token(token)
                return payload.get('sub') if payload else None
        except Exception:
            pass
        return None
    
    async def _create_rate_limit_response(self, rule: RateLimitRule, current_count: int) -> Response:
        """Create rate limit exceeded response."""
        from fastapi.responses import JSONResponse
        from app.models.api_responses import ErrorResponse
        
        retry_after = rule.window_seconds
        
        error_response = ErrorResponse.create(
            message=f"Rate limit exceeded. Try again in {retry_after} seconds.",
            error_code=ErrorCodes.RATE_LIMIT_EXCEEDED,
            error_details={
                "limit": rule.requests,
                "window_seconds": rule.window_seconds,
                "current_count": current_count,
                "retry_after": retry_after
            }
        )
        
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content=error_response.dict(),
            headers={
                "Retry-After": str(retry_after),
                "X-RateLimit-Limit": str(rule.requests),
                "X-RateLimit-Window": str(rule.window_seconds),
                "X-RateLimit-Remaining": "0"
            }
        )


# Factory functions for common configurations
def create_basic_rate_limiter(requests_per_minute: int = 60) -> RateLimitMiddleware:
    """Create a basic rate limiter with simple IP-based limiting."""
    rules = [
        RateLimitRule(
            requests=requests_per_minute,
            window_seconds=60,
            scope=RateLimitScope.PER_IP,
            strategy=RateLimitStrategy.SLIDING_WINDOW
        )
    ]
    return RateLimitMiddleware(None, rules=rules)


def create_production_rate_limiter() -> RateLimitMiddleware:
    """Create a production-ready rate limiter with comprehensive rules."""
    rules = [
        # Global limits
        RateLimitRule(
            requests=10000,
            window_seconds=3600,
            scope=RateLimitScope.GLOBAL,
            strategy=RateLimitStrategy.SLIDING_WINDOW
        ),
        
        # Per IP limits
        RateLimitRule(
            requests=200,
            window_seconds=60,
            scope=RateLimitScope.PER_IP,
            strategy=RateLimitStrategy.SLIDING_WINDOW
        ),
        
        # Authentication - very strict
        RateLimitRule(
            requests=3,
            window_seconds=60,
            scope=RateLimitScope.PER_IP,
            paths=["/api/auth/login", "/api/auth/register"],
            strategy=RateLimitStrategy.FIXED_WINDOW
        ),
        
        # File operations - moderate
        RateLimitRule(
            requests=50,
            window_seconds=300,
            scope=RateLimitScope.PER_USER,
            paths=["/api/files/", "/api/parse-invoice", "/api/process-and-save"],
            methods=["POST"],
            strategy=RateLimitStrategy.SLIDING_WINDOW
        ),
        
        # API endpoints - per user
        RateLimitRule(
            requests=1000,
            window_seconds=3600,
            scope=RateLimitScope.PER_USER,
            strategy=RateLimitStrategy.SLIDING_WINDOW
        )
    ]
    
    return RateLimitMiddleware(None, rules=rules)


# Export rate limiting components
__all__ = [
    "RateLimitStrategy",
    "RateLimitScope",
    "RateLimitRule",
    "RateLimitMiddleware",
    "RateLimitBackend",
    "InMemoryRateLimitBackend",
    "SlidingWindowRateLimitBackend",
    "create_basic_rate_limiter",
    "create_production_rate_limiter"
]
