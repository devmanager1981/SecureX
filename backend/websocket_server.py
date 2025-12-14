"""
Flask WebSocket Server for IoT security system.

This module provides a WebSocket server endpoint for real-time
communication with frontend clients, broadcasting security status updates.
"""

import logging
from flask import Flask
from flask_socketio import SocketIO, emit, disconnect
from flask_cors import CORS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WebSocketServer:
    """
    Flask WebSocket server for broadcasting security status updates.
    
    Manages client connections and provides methods for broadcasting
    JSON messages to all connected clients.
    """
    
    def __init__(self, host: str = '0.0.0.0', port: int = 5000):
        """
        Initialize Flask WebSocket server.
        
        Args:
            host: Host address to bind to (default: 0.0.0.0)
            port: Port number to listen on (default: 5000)
        """
        self.host = host
        self.port = port
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'tuya-security-digital-twin-secret'
        
        # Enable CORS for frontend communication
        CORS(self.app)
        
        # Initialize SocketIO with CORS support
        self.socketio = SocketIO(
            self.app,
            cors_allowed_origins="*",
            async_mode='threading'
        )
        
        # Track connected clients
        self.connected_clients = set()
        
        # Set up routes and event handlers
        self._setup_routes()
        self._setup_socketio_handlers()
        
        logger.info(f"WebSocketServer initialized on {host}:{port}")
    
    def _setup_routes(self):
        """Set up HTTP routes."""
        
        @self.app.route('/', methods=['GET'])
        def health_check():
            """Health check endpoint."""
            return {
                'status': 'ok',
                'service': 'tuya-security-digital-twin',
                'connected_clients': len(self.connected_clients)
            }, 200
    
    def _setup_socketio_handlers(self):
        """Set up WebSocket event handlers."""
        
        @self.socketio.on('connect')
        def handle_connect():
            """Handle client connection."""
            from flask import request
            client_id = request.sid
            
            self.connected_clients.add(client_id)
            logger.info(f"Client connected: {client_id}. Total clients: {len(self.connected_clients)}")
            
            # Send connection acknowledgment
            emit('connected', {'client_id': client_id})
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Handle client disconnection."""
            from flask import request
            client_id = request.sid
            
            if client_id in self.connected_clients:
                self.connected_clients.remove(client_id)
                logger.info(f"Client disconnected: {client_id}. Total clients: {len(self.connected_clients)}")
        
        @self.socketio.on('ping')
        def handle_ping():
            """Handle ping from client."""
            from datetime import datetime
            emit('pong', {'timestamp': str(datetime.now())})
    
    def broadcast_status(self, status: str, zone: str) -> None:
        """
        Broadcast security status update to all connected clients.
        
        Sends JSON message containing status and zone fields to all
        connected WebSocket clients.
        
        Args:
            status: Status code (RED_CRITICAL, YELLOW_WARNING, GREEN_SAFE)
            zone: Zone identifier (HOUSE, LivingRoom, Foyer, MasterBedroom)
        """
        message = {
            'status': status,
            'zone': zone
        }
        
        self.socketio.emit('status_update', message)
        logger.info(f"Broadcast status update to {len(self.connected_clients)} clients: {status} in {zone}")
    
    def get_connected_client_count(self) -> int:
        """
        Get the number of currently connected clients.
        
        Returns:
            int: Number of connected clients
        """
        return len(self.connected_clients)
    
    def run(self, debug: bool = False):
        """
        Start the WebSocket server.
        
        Args:
            debug: Enable debug mode (default: False)
        """
        logger.info(f"Starting WebSocket server on {self.host}:{self.port}")
        self.socketio.run(
            self.app,
            host=self.host,
            port=self.port,
            debug=debug,
            allow_unsafe_werkzeug=True
        )
    
    def get_socketio(self):
        """
        Get the SocketIO instance for use by other components.
        
        Returns:
            SocketIO: The Flask-SocketIO instance
        """
        return self.socketio


# Import datetime for ping handler
from datetime import datetime
