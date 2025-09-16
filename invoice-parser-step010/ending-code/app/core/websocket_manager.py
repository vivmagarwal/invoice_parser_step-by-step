"""
WebSocket Manager for Real-time Notifications

Provides real-time communication capabilities for invoice processing updates,
system notifications, and user activity broadcasting.
"""
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Set
from enum import Enum
import asyncio
from collections import defaultdict

from fastapi import WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState

logger = logging.getLogger(__name__)


class NotificationType(str, Enum):
    """WebSocket notification types."""
    INVOICE_PROCESSING = "invoice_processing"
    INVOICE_COMPLETED = "invoice_completed"
    INVOICE_FAILED = "invoice_failed"
    SYSTEM_UPDATE = "system_update"
    USER_ACTIVITY = "user_activity"
    ANALYTICS_UPDATE = "analytics_update"
    BULK_OPERATION = "bulk_operation"
    ERROR_NOTIFICATION = "error_notification"


class NotificationPriority(str, Enum):
    """Notification priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class WebSocketConnection:
    """Represents a WebSocket connection with metadata."""
    
    def __init__(self, websocket: WebSocket, user_id: str, connection_id: str):
        self.websocket = websocket
        self.user_id = user_id
        self.connection_id = connection_id
        self.connected_at = datetime.utcnow()
        self.last_ping = datetime.utcnow()
        self.subscriptions: Set[str] = set()
        self.metadata: Dict[str, Any] = {}
    
    async def send_message(self, message: Dict[str, Any]) -> bool:
        """Send message to WebSocket connection."""
        try:
            if self.websocket.client_state == WebSocketState.CONNECTED:
                await self.websocket.send_text(json.dumps(message))
                return True
            return False
        except Exception as e:
            logger.error(f"Error sending WebSocket message: {e}")
            return False
    
    async def ping(self) -> bool:
        """Send ping to check connection health."""
        try:
            if self.websocket.client_state == WebSocketState.CONNECTED:
                await self.websocket.ping()
                self.last_ping = datetime.utcnow()
                return True
            return False
        except Exception as e:
            logger.error(f"Error pinging WebSocket: {e}")
            return False


class WebSocketManager:
    """Manages WebSocket connections and real-time notifications."""
    
    def __init__(self):
        # User connections: user_id -> List[WebSocketConnection]
        self.user_connections: Dict[str, List[WebSocketConnection]] = defaultdict(list)
        # All connections by connection_id
        self.connections: Dict[str, WebSocketConnection] = {}
        # Topic subscriptions: topic -> Set[connection_id]
        self.topic_subscriptions: Dict[str, Set[str]] = defaultdict(set)
        # Connection statistics
        self.stats = {
            "total_connections": 0,
            "active_connections": 0,
            "messages_sent": 0,
            "messages_failed": 0,
            "connections_by_user": defaultdict(int)
        }
    
    async def connect(self, websocket: WebSocket, user_id: str, connection_id: str) -> WebSocketConnection:
        """Accept and register a new WebSocket connection."""
        try:
            await websocket.accept()
            
            connection = WebSocketConnection(websocket, user_id, connection_id)
            
            # Register connection
            self.connections[connection_id] = connection
            self.user_connections[user_id].append(connection)
            
            # Update statistics
            self.stats["total_connections"] += 1
            self.stats["active_connections"] += 1
            self.stats["connections_by_user"][user_id] += 1
            
            logger.info(f"WebSocket connected: user={user_id}, connection={connection_id}")
            
            # Send welcome message
            await self.send_to_connection(connection_id, {
                "type": "connection_established",
                "message": "WebSocket connection established",
                "connection_id": connection_id,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            return connection
            
        except Exception as e:
            logger.error(f"Error connecting WebSocket: {e}")
            raise
    
    async def disconnect(self, connection_id: str):
        """Disconnect and clean up a WebSocket connection."""
        try:
            if connection_id not in self.connections:
                return
            
            connection = self.connections[connection_id]
            user_id = connection.user_id
            
            # Remove from user connections
            if user_id in self.user_connections:
                self.user_connections[user_id] = [
                    conn for conn in self.user_connections[user_id] 
                    if conn.connection_id != connection_id
                ]
                if not self.user_connections[user_id]:
                    del self.user_connections[user_id]
            
            # Remove from topic subscriptions
            for topic, subscribers in self.topic_subscriptions.items():
                subscribers.discard(connection_id)
            
            # Remove from connections
            del self.connections[connection_id]
            
            # Update statistics
            self.stats["active_connections"] -= 1
            self.stats["connections_by_user"][user_id] -= 1
            if self.stats["connections_by_user"][user_id] <= 0:
                del self.stats["connections_by_user"][user_id]
            
            logger.info(f"WebSocket disconnected: user={user_id}, connection={connection_id}")
            
        except Exception as e:
            logger.error(f"Error disconnecting WebSocket: {e}")
    
    async def send_to_connection(self, connection_id: str, message: Dict[str, Any]) -> bool:
        """Send message to a specific connection."""
        try:
            if connection_id not in self.connections:
                return False
            
            connection = self.connections[connection_id]
            success = await connection.send_message(message)
            
            if success:
                self.stats["messages_sent"] += 1
            else:
                self.stats["messages_failed"] += 1
            
            return success
            
        except Exception as e:
            logger.error(f"Error sending to connection {connection_id}: {e}")
            self.stats["messages_failed"] += 1
            return False
    
    async def send_to_user(self, user_id: str, message: Dict[str, Any]) -> int:
        """Send message to all connections for a user."""
        if user_id not in self.user_connections:
            return 0
        
        sent_count = 0
        failed_connections = []
        
        for connection in self.user_connections[user_id]:
            success = await connection.send_message(message)
            if success:
                sent_count += 1
                self.stats["messages_sent"] += 1
            else:
                self.stats["messages_failed"] += 1
                failed_connections.append(connection.connection_id)
        
        # Clean up failed connections
        for connection_id in failed_connections:
            await self.disconnect(connection_id)
        
        return sent_count
    
    async def broadcast_to_topic(self, topic: str, message: Dict[str, Any]) -> int:
        """Broadcast message to all subscribers of a topic."""
        if topic not in self.topic_subscriptions:
            return 0
        
        sent_count = 0
        failed_connections = []
        
        for connection_id in self.topic_subscriptions[topic]:
            if connection_id in self.connections:
                success = await self.send_to_connection(connection_id, message)
                if success:
                    sent_count += 1
                else:
                    failed_connections.append(connection_id)
        
        # Clean up failed connections
        for connection_id in failed_connections:
            await self.disconnect(connection_id)
        
        return sent_count
    
    async def subscribe_to_topic(self, connection_id: str, topic: str) -> bool:
        """Subscribe a connection to a topic."""
        try:
            if connection_id not in self.connections:
                return False
            
            connection = self.connections[connection_id]
            connection.subscriptions.add(topic)
            self.topic_subscriptions[topic].add(connection_id)
            
            logger.info(f"Connection {connection_id} subscribed to topic: {topic}")
            return True
            
        except Exception as e:
            logger.error(f"Error subscribing to topic: {e}")
            return False
    
    async def unsubscribe_from_topic(self, connection_id: str, topic: str) -> bool:
        """Unsubscribe a connection from a topic."""
        try:
            if connection_id in self.connections:
                connection = self.connections[connection_id]
                connection.subscriptions.discard(topic)
            
            if topic in self.topic_subscriptions:
                self.topic_subscriptions[topic].discard(connection_id)
            
            logger.info(f"Connection {connection_id} unsubscribed from topic: {topic}")
            return True
            
        except Exception as e:
            logger.error(f"Error unsubscribing from topic: {e}")
            return False
    
    async def send_notification(
        self,
        notification_type: NotificationType,
        message: str,
        user_id: Optional[str] = None,
        topic: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        priority: NotificationPriority = NotificationPriority.NORMAL
    ) -> int:
        """Send a structured notification."""
        notification = {
            "type": notification_type.value,
            "message": message,
            "priority": priority.value,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data or {}
        }
        
        sent_count = 0
        
        if user_id:
            sent_count += await self.send_to_user(user_id, notification)
        elif topic:
            sent_count += await self.broadcast_to_topic(topic, notification)
        else:
            # Broadcast to all connections
            for connection_id in list(self.connections.keys()):
                await self.send_to_connection(connection_id, notification)
                sent_count += 1
        
        logger.info(f"Sent notification '{notification_type.value}' to {sent_count} connections")
        return sent_count
    
    async def handle_message(self, connection_id: str, message: str):
        """Handle incoming WebSocket message."""
        try:
            data = json.loads(message)
            message_type = data.get("type")
            
            if message_type == "ping":
                await self.send_to_connection(connection_id, {
                    "type": "pong",
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            elif message_type == "subscribe":
                topic = data.get("topic")
                if topic:
                    success = await self.subscribe_to_topic(connection_id, topic)
                    await self.send_to_connection(connection_id, {
                        "type": "subscription_response",
                        "topic": topic,
                        "success": success,
                        "timestamp": datetime.utcnow().isoformat()
                    })
            
            elif message_type == "unsubscribe":
                topic = data.get("topic")
                if topic:
                    success = await self.unsubscribe_from_topic(connection_id, topic)
                    await self.send_to_connection(connection_id, {
                        "type": "unsubscription_response",
                        "topic": topic,
                        "success": success,
                        "timestamp": datetime.utcnow().isoformat()
                    })
            
            elif message_type == "get_stats":
                if connection_id in self.connections:
                    connection = self.connections[connection_id]
                    await self.send_to_connection(connection_id, {
                        "type": "stats_response",
                        "stats": {
                            "connection_info": {
                                "connection_id": connection_id,
                                "connected_at": connection.connected_at.isoformat(),
                                "subscriptions": list(connection.subscriptions)
                            },
                            "system_stats": self.stats
                        },
                        "timestamp": datetime.utcnow().isoformat()
                    })
            
        except json.JSONDecodeError:
            await self.send_to_connection(connection_id, {
                "type": "error",
                "message": "Invalid JSON message",
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            logger.error(f"Error handling WebSocket message: {e}")
            await self.send_to_connection(connection_id, {
                "type": "error",
                "message": "Error processing message",
                "timestamp": datetime.utcnow().isoformat()
            })
    
    async def cleanup_stale_connections(self):
        """Clean up stale connections periodically."""
        stale_connections = []
        current_time = datetime.utcnow()
        
        for connection_id, connection in self.connections.items():
            # Check if connection is still alive
            if connection.websocket.client_state != WebSocketState.CONNECTED:
                stale_connections.append(connection_id)
                continue
            
            # Check for stale connections (no ping for 5 minutes)
            if (current_time - connection.last_ping).total_seconds() > 300:
                try:
                    success = await connection.ping()
                    if not success:
                        stale_connections.append(connection_id)
                except:
                    stale_connections.append(connection_id)
        
        # Clean up stale connections
        for connection_id in stale_connections:
            await self.disconnect(connection_id)
        
        if stale_connections:
            logger.info(f"Cleaned up {len(stale_connections)} stale WebSocket connections")
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get current connection statistics."""
        return {
            "active_connections": self.stats["active_connections"],
            "total_connections": self.stats["total_connections"],
            "messages_sent": self.stats["messages_sent"],
            "messages_failed": self.stats["messages_failed"],
            "users_connected": len(self.user_connections),
            "topics_with_subscribers": len([t for t, s in self.topic_subscriptions.items() if s]),
            "connections_by_user": dict(self.stats["connections_by_user"])
        }


# Global WebSocket manager instance
websocket_manager = WebSocketManager()


# Utility functions for common notification patterns
async def notify_invoice_processing(user_id: str, invoice_id: str, progress: float = 0):
    """Notify user about invoice processing progress."""
    await websocket_manager.send_notification(
        NotificationType.INVOICE_PROCESSING,
        f"Processing invoice {invoice_id}",
        user_id=user_id,
        data={
            "invoice_id": invoice_id,
            "progress": progress,
            "stage": "processing"
        }
    )


async def notify_invoice_completed(user_id: str, invoice_id: str, result: Dict[str, Any]):
    """Notify user about completed invoice processing."""
    await websocket_manager.send_notification(
        NotificationType.INVOICE_COMPLETED,
        f"Invoice {invoice_id} processed successfully",
        user_id=user_id,
        priority=NotificationPriority.HIGH,
        data={
            "invoice_id": invoice_id,
            "result": result,
            "stage": "completed"
        }
    )


async def notify_invoice_failed(user_id: str, invoice_id: str, error: str):
    """Notify user about failed invoice processing."""
    await websocket_manager.send_notification(
        NotificationType.INVOICE_FAILED,
        f"Failed to process invoice {invoice_id}: {error}",
        user_id=user_id,
        priority=NotificationPriority.HIGH,
        data={
            "invoice_id": invoice_id,
            "error": error,
            "stage": "failed"
        }
    )


async def notify_system_update(message: str, data: Optional[Dict[str, Any]] = None):
    """Send system-wide notification."""
    await websocket_manager.send_notification(
        NotificationType.SYSTEM_UPDATE,
        message,
        topic="system",
        priority=NotificationPriority.NORMAL,
        data=data
    )


# Background task for connection cleanup
async def websocket_cleanup_task():
    """Background task to clean up stale connections."""
    while True:
        try:
            await websocket_manager.cleanup_stale_connections()
            await asyncio.sleep(60)  # Run every minute
        except Exception as e:
            logger.error(f"Error in WebSocket cleanup task: {e}")
            await asyncio.sleep(60)


# Export WebSocket components
__all__ = [
    "WebSocketManager",
    "WebSocketConnection", 
    "NotificationType",
    "NotificationPriority",
    "websocket_manager",
    "notify_invoice_processing",
    "notify_invoice_completed",
    "notify_invoice_failed",
    "notify_system_update",
    "websocket_cleanup_task"
]
