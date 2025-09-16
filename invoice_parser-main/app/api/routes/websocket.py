"""
WebSocket API Routes

Provides real-time WebSocket communication endpoints for notifications,
updates, and live data streaming.
"""
import logging
import uuid
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from fastapi.responses import HTMLResponse

from app.core.websocket_manager import websocket_manager, websocket_cleanup_task
from app.core.security import verify_token
from app.models.api_responses import success_response

logger = logging.getLogger(__name__)
router = APIRouter(tags=["websocket"])


async def get_user_from_websocket_token(token: str) -> str:
    """Extract user ID from WebSocket authentication token."""
    try:
        payload = verify_token(token)
        if payload:
            return payload.get('sub')
        return None
    except Exception as e:
        logger.error(f"Error verifying WebSocket token: {e}")
        return None


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(..., description="JWT authentication token"),
    connection_id: str = Query(None, description="Optional connection identifier")
):
    """
    Main WebSocket endpoint for real-time communication.
    
    Features:
    - Real-time invoice processing notifications
    - System status updates
    - User activity broadcasting
    - Topic-based subscriptions
    - Connection health monitoring
    
    Authentication:
    - Requires valid JWT token as query parameter
    - Token is verified on connection establishment
    
    Message Types:
    - ping/pong: Connection health check
    - subscribe/unsubscribe: Topic management
    - get_stats: Connection statistics
    
    Notification Types:
    - invoice_processing: Processing updates
    - invoice_completed: Completion notifications
    - invoice_failed: Error notifications
    - system_update: System-wide updates
    - analytics_update: Analytics data updates
    """
    # Verify authentication
    user_id = await get_user_from_websocket_token(token)
    if not user_id:
        await websocket.close(code=4001, reason="Authentication failed")
        return
    
    # Generate connection ID if not provided
    if not connection_id:
        connection_id = str(uuid.uuid4())
    
    try:
        # Connect to WebSocket manager
        connection = await websocket_manager.connect(websocket, user_id, connection_id)
        logger.info(f"WebSocket connection established for user {user_id}")
        
        # Subscribe to user-specific notifications by default
        await websocket_manager.subscribe_to_topic(connection_id, f"user:{user_id}")
        
        # Handle incoming messages
        while True:
            try:
                message = await websocket.receive_text()
                await websocket_manager.handle_message(connection_id, message)
            except WebSocketDisconnect:
                logger.info(f"WebSocket disconnected for user {user_id}")
                break
            except Exception as e:
                logger.error(f"Error handling WebSocket message: {e}")
                # Send error notification to client
                await websocket_manager.send_to_connection(connection_id, {
                    "type": "error",
                    "message": "Error processing message",
                    "error": str(e)
                })
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected during setup for user {user_id}")
    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
        try:
            await websocket.close(code=1011, reason="Internal server error")
        except:
            pass
    finally:
        # Clean up connection
        await websocket_manager.disconnect(connection_id)


@router.get("/ws/stats")
async def get_websocket_stats():
    """
    Get WebSocket connection statistics.
    
    Returns:
    - Active connection count
    - Total connections served
    - Messages sent/failed
    - Users currently connected
    - Topic subscription counts
    """
    try:
        stats = websocket_manager.get_connection_stats()
        return success_response(
            data=stats,
            message="WebSocket statistics retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error getting WebSocket stats: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@router.get("/ws/test")
async def websocket_test_page():
    """
    Serve a test page for WebSocket functionality.
    
    This endpoint provides a simple HTML page for testing WebSocket connections
    during development and debugging.
    """
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>WebSocket Test</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .container { max-width: 800px; margin: 0 auto; }
            .status { padding: 10px; margin: 10px 0; border-radius: 5px; }
            .connected { background-color: #d4edda; color: #155724; }
            .disconnected { background-color: #f8d7da; color: #721c24; }
            .messages { height: 300px; overflow-y: scroll; border: 1px solid #ccc; padding: 10px; }
            .input-group { margin: 10px 0; }
            input, button, select { padding: 8px; margin: 5px; }
            button { background-color: #007bff; color: white; border: none; border-radius: 3px; cursor: pointer; }
            button:hover { background-color: #0056b3; }
            .message { margin: 5px 0; padding: 5px; background-color: #f8f9fa; border-left: 3px solid #007bff; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>WebSocket Test Interface</h1>
            
            <div id="status" class="status disconnected">Disconnected</div>
            
            <div class="input-group">
                <input type="text" id="tokenInput" placeholder="Enter JWT token" style="width: 300px;">
                <button onclick="connect()">Connect</button>
                <button onclick="disconnect()">Disconnect</button>
            </div>
            
            <div class="input-group">
                <select id="messageType">
                    <option value="ping">Ping</option>
                    <option value="subscribe">Subscribe</option>
                    <option value="unsubscribe">Unsubscribe</option>
                    <option value="get_stats">Get Stats</option>
                </select>
                <input type="text" id="topicInput" placeholder="Topic (for subscribe/unsubscribe)" style="width: 200px;">
                <button onclick="sendMessage()">Send Message</button>
            </div>
            
            <div class="input-group">
                <button onclick="clearMessages()">Clear Messages</button>
                <button onclick="getStats()">Get Connection Stats</button>
            </div>
            
            <h3>Messages:</h3>
            <div id="messages" class="messages"></div>
        </div>
        
        <script>
            let ws = null;
            const statusDiv = document.getElementById('status');
            const messagesDiv = document.getElementById('messages');
            
            function updateStatus(status, className) {
                statusDiv.textContent = status;
                statusDiv.className = 'status ' + className;
            }
            
            function addMessage(message, type = 'received') {
                const messageDiv = document.createElement('div');
                messageDiv.className = 'message';
                messageDiv.innerHTML = `<strong>[${new Date().toLocaleTimeString()}] ${type.toUpperCase()}:</strong> ${message}`;
                messagesDiv.appendChild(messageDiv);
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
            }
            
            function connect() {
                const token = document.getElementById('tokenInput').value;
                if (!token) {
                    alert('Please enter a JWT token');
                    return;
                }
                
                if (ws) {
                    ws.close();
                }
                
                const wsUrl = `ws://localhost:8000/api/v1/ws?token=${encodeURIComponent(token)}`;
                ws = new WebSocket(wsUrl);
                
                ws.onopen = function(event) {
                    updateStatus('Connected', 'connected');
                    addMessage('WebSocket connection established', 'system');
                };
                
                ws.onmessage = function(event) {
                    const data = JSON.parse(event.data);
                    addMessage(JSON.stringify(data, null, 2), 'received');
                };
                
                ws.onclose = function(event) {
                    updateStatus('Disconnected', 'disconnected');
                    addMessage(`Connection closed: ${event.code} - ${event.reason}`, 'system');
                };
                
                ws.onerror = function(error) {
                    updateStatus('Error', 'disconnected');
                    addMessage(`WebSocket error: ${error}`, 'error');
                };
            }
            
            function disconnect() {
                if (ws) {
                    ws.close();
                    ws = null;
                }
            }
            
            function sendMessage() {
                if (!ws || ws.readyState !== WebSocket.OPEN) {
                    alert('WebSocket is not connected');
                    return;
                }
                
                const messageType = document.getElementById('messageType').value;
                const topic = document.getElementById('topicInput').value;
                
                let message = { type: messageType };
                
                if ((messageType === 'subscribe' || messageType === 'unsubscribe') && topic) {
                    message.topic = topic;
                }
                
                const messageStr = JSON.stringify(message);
                ws.send(messageStr);
                addMessage(messageStr, 'sent');
            }
            
            function clearMessages() {
                messagesDiv.innerHTML = '';
            }
            
            function getStats() {
                fetch('/api/v1/ws/stats')
                    .then(response => response.json())
                    .then(data => {
                        addMessage(JSON.stringify(data, null, 2), 'stats');
                    })
                    .catch(error => {
                        addMessage(`Error getting stats: ${error}`, 'error');
                    });
            }
            
            // Auto-connect if token is in URL parameters
            const urlParams = new URLSearchParams(window.location.search);
            const token = urlParams.get('token');
            if (token) {
                document.getElementById('tokenInput').value = token;
                connect();
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


# Start background cleanup task when module is imported
import asyncio
try:
    # Only start if event loop is running
    loop = asyncio.get_running_loop()
    loop.create_task(websocket_cleanup_task())
except RuntimeError:
    # No running event loop, task will be started when app starts
    pass
