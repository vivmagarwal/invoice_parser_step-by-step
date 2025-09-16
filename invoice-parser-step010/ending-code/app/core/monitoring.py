"""
Application Monitoring and Metrics Collection

Provides comprehensive system monitoring, metrics collection, and health tracking
for production observability.
"""
import asyncio
import logging
import psutil
import time
from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from threading import Lock
import json

from fastapi import BackgroundTasks
from sqlalchemy import text

from app.core.config import get_settings
from app.core.database import get_database_engine

logger = logging.getLogger(__name__)


class MetricsCollector:
    """Collects and stores application metrics."""
    
    def __init__(self):
        self._metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self._counters: Dict[str, int] = defaultdict(int)
        self._gauges: Dict[str, float] = defaultdict(float)
        self._histograms: Dict[str, List[float]] = defaultdict(list)
        self._lock = Lock()
        
        # System metrics
        self._start_time = time.time()
        self._request_count = 0
        self._error_count = 0
        
    def increment_counter(self, name: str, value: int = 1, tags: Dict[str, str] = None):
        """Increment a counter metric."""
        with self._lock:
            metric_key = f"{name}:{self._tags_to_string(tags)}" if tags else name
            self._counters[metric_key] += value
    
    def set_gauge(self, name: str, value: float, tags: Dict[str, str] = None):
        """Set a gauge metric."""
        with self._lock:
            metric_key = f"{name}:{self._tags_to_string(tags)}" if tags else name
            self._gauges[metric_key] = value
    
    def record_histogram(self, name: str, value: float, tags: Dict[str, str] = None):
        """Record a histogram value."""
        with self._lock:
            metric_key = f"{name}:{self._tags_to_string(tags)}" if tags else name
            self._histograms[metric_key].append(value)
            # Keep only last 1000 values
            if len(self._histograms[metric_key]) > 1000:
                self._histograms[metric_key] = self._histograms[metric_key][-1000:]
    
    def record_timing(self, name: str, duration_ms: float, tags: Dict[str, str] = None):
        """Record a timing metric."""
        self.record_histogram(f"{name}_duration_ms", duration_ms, tags)
    
    def _tags_to_string(self, tags: Dict[str, str]) -> str:
        """Convert tags dict to string."""
        if not tags:
            return ""
        return ",".join(f"{k}={v}" for k, v in sorted(tags.items()))
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get a summary of all metrics."""
        with self._lock:
            summary = {
                "counters": dict(self._counters),
                "gauges": dict(self._gauges),
                "histograms": {}
            }
            
            # Calculate histogram statistics
            for name, values in self._histograms.items():
                if values:
                    sorted_values = sorted(values)
                    n = len(sorted_values)
                    summary["histograms"][name] = {
                        "count": n,
                        "min": sorted_values[0],
                        "max": sorted_values[-1],
                        "mean": sum(sorted_values) / n,
                        "p50": sorted_values[int(n * 0.5)],
                        "p95": sorted_values[int(n * 0.95)],
                        "p99": sorted_values[int(n * 0.99)] if n > 1 else sorted_values[0]
                    }
            
            return summary


class SystemMonitor:
    """Monitors system resources and performance."""
    
    def __init__(self):
        self.metrics = MetricsCollector()
        self._monitoring = False
        
    async def start_monitoring(self):
        """Start background monitoring."""
        if self._monitoring:
            return
            
        self._monitoring = True
        logger.info("Starting system monitoring")
        
        # Start monitoring task
        asyncio.create_task(self._monitoring_loop())
    
    def stop_monitoring(self):
        """Stop background monitoring."""
        self._monitoring = False
        logger.info("Stopping system monitoring")
    
    async def _monitoring_loop(self):
        """Main monitoring loop."""
        while self._monitoring:
            try:
                await self._collect_system_metrics()
                await asyncio.sleep(30)  # Collect metrics every 30 seconds
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def _collect_system_metrics(self):
        """Collect system performance metrics."""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            self.metrics.set_gauge("system_cpu_percent", cpu_percent)
            
            # Memory metrics
            memory = psutil.virtual_memory()
            self.metrics.set_gauge("system_memory_percent", memory.percent)
            self.metrics.set_gauge("system_memory_used_bytes", memory.used)
            self.metrics.set_gauge("system_memory_available_bytes", memory.available)
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            self.metrics.set_gauge("system_disk_percent", disk.percent)
            self.metrics.set_gauge("system_disk_used_bytes", disk.used)
            self.metrics.set_gauge("system_disk_free_bytes", disk.free)
            
            # Process metrics
            process = psutil.Process()
            self.metrics.set_gauge("process_memory_rss_bytes", process.memory_info().rss)
            self.metrics.set_gauge("process_memory_vms_bytes", process.memory_info().vms)
            self.metrics.set_gauge("process_cpu_percent", process.cpu_percent())
            self.metrics.set_gauge("process_num_threads", process.num_threads())
            
            # Database connection metrics
            await self._collect_database_metrics()
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
    
    async def _collect_database_metrics(self):
        """Collect database performance metrics."""
        try:
            engine = get_database_engine()
            
            # Connection pool metrics
            pool = engine.pool
            self.metrics.set_gauge("db_pool_size", pool.size())
            self.metrics.set_gauge("db_pool_checked_in", pool.checkedin())
            self.metrics.set_gauge("db_pool_checked_out", pool.checkedout())
            self.metrics.set_gauge("db_pool_overflow", pool.overflow())
            
            # Database query metrics
            with engine.connect() as conn:
                # Get database size
                result = conn.execute(text("SELECT pg_database_size(current_database())"))
                db_size = result.scalar()
                self.metrics.set_gauge("db_size_bytes", db_size)
                
                # Get connection count
                result = conn.execute(text("""
                    SELECT count(*) FROM pg_stat_activity 
                    WHERE datname = current_database()
                """))
                connection_count = result.scalar()
                self.metrics.set_gauge("db_connections", connection_count)
                
                # Get table statistics
                result = conn.execute(text("""
                    SELECT schemaname, relname, n_tup_ins, n_tup_upd, n_tup_del, n_live_tup
                    FROM pg_stat_user_tables
                    WHERE schemaname = 'public'
                """))
                
                for row in result:
                    table_name = row[1]
                    self.metrics.set_gauge(f"db_table_{table_name}_inserts", row[2])
                    self.metrics.set_gauge(f"db_table_{table_name}_updates", row[3])
                    self.metrics.set_gauge(f"db_table_{table_name}_deletes", row[4])
                    self.metrics.set_gauge(f"db_table_{table_name}_live_tuples", row[5])
                    
        except Exception as e:
            logger.error(f"Error collecting database metrics: {e}")
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get current system health status."""
        try:
            # Get current metrics
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Determine health status
            health_issues = []
            
            if cpu_percent > 80:
                health_issues.append(f"High CPU usage: {cpu_percent:.1f}%")
            
            if memory.percent > 85:
                health_issues.append(f"High memory usage: {memory.percent:.1f}%")
            
            if disk.percent > 90:
                health_issues.append(f"High disk usage: {disk.percent:.1f}%")
            
            status = "unhealthy" if health_issues else "healthy"
            
            return {
                "status": status,
                "issues": health_issues,
                "metrics": {
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "disk_percent": disk.percent,
                    "uptime_seconds": time.time() - self.metrics._start_time
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting health status: {e}")
            return {
                "status": "unknown",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }


class ApplicationMetrics:
    """Application-specific metrics tracking."""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics = metrics_collector
    
    def record_request(self, method: str, path: str, status_code: int, duration_ms: float):
        """Record HTTP request metrics."""
        tags = {
            "method": method,
            "path": path,
            "status": str(status_code)
        }
        
        self.metrics.increment_counter("http_requests_total", tags=tags)
        self.metrics.record_timing("http_request_duration", duration_ms, tags=tags)
        
        # Track error rates
        if status_code >= 400:
            self.metrics.increment_counter("http_errors_total", tags=tags)
    
    def record_invoice_processing(self, status: str, duration_ms: float, file_size: int = None):
        """Record invoice processing metrics."""
        tags = {"status": status}
        
        self.metrics.increment_counter("invoice_processing_total", tags=tags)
        self.metrics.record_timing("invoice_processing_duration", duration_ms, tags=tags)
        
        if file_size:
            self.metrics.record_histogram("invoice_file_size_bytes", file_size)
    
    def record_ai_usage(self, model: str, tokens: int, duration_ms: float):
        """Record AI model usage metrics."""
        tags = {"model": model}
        
        self.metrics.increment_counter("ai_requests_total", tags=tags)
        self.metrics.record_timing("ai_request_duration", duration_ms, tags=tags)
        self.metrics.record_histogram("ai_tokens_used", tokens, tags=tags)
    
    def record_database_operation(self, operation: str, table: str, duration_ms: float):
        """Record database operation metrics."""
        tags = {
            "operation": operation,
            "table": table
        }
        
        self.metrics.increment_counter("db_operations_total", tags=tags)
        self.metrics.record_timing("db_operation_duration", duration_ms, tags=tags)
    
    def record_user_activity(self, user_id: str, action: str):
        """Record user activity metrics."""
        tags = {"action": action}
        
        self.metrics.increment_counter("user_actions_total", tags=tags)
        
        # Track unique users (simplified - in production use proper user tracking)
        self.metrics.set_gauge(f"user_{user_id}_last_activity", time.time())


# Global monitoring instances
system_monitor = SystemMonitor()
app_metrics = ApplicationMetrics(system_monitor.metrics)


async def start_monitoring():
    """Start application monitoring."""
    await system_monitor.start_monitoring()


def stop_monitoring():
    """Stop application monitoring."""
    system_monitor.stop_monitoring()


def get_metrics_endpoint() -> Dict[str, Any]:
    """Get metrics for monitoring endpoint."""
    return {
        "metrics": system_monitor.metrics.get_metrics_summary(),
        "health": system_monitor.get_health_status(),
        "timestamp": datetime.utcnow().isoformat()
    }


# Export monitoring components
__all__ = [
    "MetricsCollector",
    "SystemMonitor", 
    "ApplicationMetrics",
    "system_monitor",
    "app_metrics",
    "start_monitoring",
    "stop_monitoring",
    "get_metrics_endpoint"
]
