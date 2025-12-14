"""
Example usage of the WebSocket server.

This script demonstrates how to initialize and use the WebSocket server
for broadcasting security status updates.
"""

from websocket_server import WebSocketServer
import time
import threading


def simulate_security_events(server):
    """
    Simulate security events and broadcast status updates.
    
    Args:
        server: WebSocketServer instance
    """
    # Wait for server to start
    time.sleep(2)
    
    print("\n=== Simulating Security Events ===\n")
    
    # Simulate YELLOW_WARNING in LivingRoom
    print("1. Motion detected in LivingRoom (YELLOW_WARNING)")
    server.broadcast_status("YELLOW_WARNING", "LivingRoom")
    time.sleep(3)
    
    # Simulate RED_CRITICAL in HOUSE
    print("2. Break-in attempt detected! (RED_CRITICAL)")
    server.broadcast_status("RED_CRITICAL", "HOUSE")
    time.sleep(3)
    
    # Simulate GREEN_SAFE in HOUSE
    print("3. Door unlocked - safe arrival (GREEN_SAFE)")
    server.broadcast_status("GREEN_SAFE", "HOUSE")
    time.sleep(3)
    
    print("\n=== Simulation Complete ===\n")


def main():
    """Main function to run the WebSocket server example."""
    print("Starting WebSocket Server Example...")
    print("Server will listen on http://localhost:5000")
    print("WebSocket endpoint: ws://localhost:5000/socket.io/")
    print("\nPress Ctrl+C to stop the server\n")
    
    # Create WebSocket server
    server = WebSocketServer(host='0.0.0.0', port=5000)
    
    # Start simulation in a separate thread
    simulation_thread = threading.Thread(
        target=simulate_security_events,
        args=(server,),
        daemon=True
    )
    simulation_thread.start()
    
    # Run the server (blocking call)
    try:
        server.run(debug=False)
    except KeyboardInterrupt:
        print("\n\nShutting down server...")


if __name__ == '__main__':
    main()
