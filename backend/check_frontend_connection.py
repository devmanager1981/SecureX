"""
Quick diagnostic script to check if frontend can connect to backend.

This script starts a minimal WebSocket server and waits for connections.
Use this to verify your network setup is correct.
"""

import logging
from flask import Flask
from flask_socketio import SocketIO, emit
from flask_cors import CORS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Run diagnostic WebSocket server."""
    
    print("=" * 70)
    print("FRONTEND CONNECTION DIAGNOSTIC")
    print("=" * 70)
    print()
    print("This script will:")
    print("1. Start a WebSocket server on port 5000")
    print("2. Wait for frontend connections")
    print("3. Log all connection attempts")
    print()
    print("To test:")
    print("1. Keep this script running")
    print("2. Open frontend/test_simple.html in your browser")
    print("3. Check if you see 'Client connected' message below")
    print()
    print("=" * 70)
    print()
    
    # Create Flask app
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'test-secret'
    CORS(app)
    
    # Create SocketIO instance
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
    
    # Track connections
    connected_clients = []
    
    @app.route('/')
    def index():
        return {
            'status': 'ok',
            'message': 'WebSocket server is running',
            'connected_clients': len(connected_clients)
        }
    
    @socketio.on('connect')
    def handle_connect():
        from flask import request
        client_id = request.sid
        connected_clients.append(client_id)
        
        logger.info("=" * 70)
        logger.info(f"✅ CLIENT CONNECTED!")
        logger.info(f"   Client ID: {client_id}")
        logger.info(f"   Total clients: {len(connected_clients)}")
        logger.info("=" * 70)
        
        # Send welcome message
        emit('connected', {'message': 'Welcome to Tuya Security WebSocket'})
        
        # Send test message after 2 seconds
        import time
        time.sleep(2)
        logger.info("Sending test message to client...")
        emit('status_update', {'status': 'GREEN_SAFE', 'zone': 'HOUSE'})
    
    @socketio.on('disconnect')
    def handle_disconnect():
        from flask import request
        client_id = request.sid
        if client_id in connected_clients:
            connected_clients.remove(client_id)
        
        logger.info("=" * 70)
        logger.info(f"❌ CLIENT DISCONNECTED")
        logger.info(f"   Client ID: {client_id}")
        logger.info(f"   Remaining clients: {len(connected_clients)}")
        logger.info("=" * 70)
    
    @socketio.on('ping')
    def handle_ping():
        logger.info("Received ping from client")
        emit('pong', {'timestamp': 'pong'})
    
    # Start server
    logger.info("Starting WebSocket server on http://0.0.0.0:5000")
    logger.info("Waiting for connections...")
    logger.info("")
    
    try:
        socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)
    except KeyboardInterrupt:
        logger.info("\nShutting down...")
    except Exception as e:
        logger.error(f"Error starting server: {e}")
        logger.error("")
        logger.error("Common issues:")
        logger.error("1. Port 5000 already in use - close other applications")
        logger.error("2. Missing dependencies - run: pip install flask flask-socketio flask-cors")
        logger.error("3. Firewall blocking - temporarily disable firewall")


if __name__ == '__main__':
    main()
