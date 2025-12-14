# WebSocket Server Implementation

## Overview

This implementation provides a Flask-SocketIO based WebSocket server for the Tuya Security Digital Twin system. The server enables real-time bidirectional communication between the backend security system and frontend visualization clients.

## Files Created

1. **websocket_server.py** - Main WebSocket server implementation
2. **test_websocket_server.py** - Property-based tests for the server
3. **example_websocket_usage.py** - Example usage script
4. **test_client.html** - HTML test client for manual testing

## Features

### WebSocket Server (`websocket_server.py`)

The `WebSocketServer` class provides:

- **Connection Management**: Automatically tracks connected clients
- **Health Check Endpoint**: GET / returns server status and client count
- **WebSocket Endpoint**: Socket.IO endpoint for real-time communication
- **Broadcast Functionality**: Send status updates to all connected clients
- **Event Handlers**: 
  - `connect` - Handles new client connections
  - `disconnect` - Handles client disconnections and cleanup
  - `ping` - Keeps connections alive

### Key Methods

```python
# Initialize server
server = WebSocketServer(host='0.0.0.0', port=5000)

# Broadcast status update to all clients
server.broadcast_status(status='RED_CRITICAL', zone='HOUSE')

# Get connected client count
count = server.get_connected_client_count()

# Get SocketIO instance for integration with other components
socketio = server.get_socketio()

# Run the server
server.run(debug=False)
```

## Property-Based Tests

All three required properties have been implemented and pass:

### Property 18: WebSocket Client Connection Acceptance
**Validates: Requirements 8.2**

Tests that any valid WebSocket connection is accepted and the client is added to the broadcast list.

```bash
pytest backend/test_websocket_server.py::test_property_18_websocket_client_connection_acceptance -v
```

### Property 19: Broadcast Message Format
**Validates: Requirements 8.3**

Tests that all broadcast messages contain both "status" and "zone" fields in the correct format.

```bash
pytest backend/test_websocket_server.py::test_property_19_broadcast_message_format -v
```

### Property 20: Client Cleanup on Disconnection
**Validates: Requirements 8.4**

Tests that disconnected clients are properly removed from the broadcast list.

```bash
pytest backend/test_websocket_server.py::test_property_20_client_cleanup_on_disconnection -v
```

## Running Tests

Run all WebSocket server tests:
```bash
pytest backend/test_websocket_server.py -v
```

Run all backend tests:
```bash
pytest backend/ -v
```

## Usage Examples

### Example 1: Standalone Server

Run the example script to see the server in action:

```bash
python backend/example_websocket_usage.py
```

This will:
1. Start the WebSocket server on port 5000
2. Simulate security events (YELLOW_WARNING, RED_CRITICAL, GREEN_SAFE)
3. Broadcast status updates to all connected clients

### Example 2: Integration with Response Orchestrator

```python
from websocket_server import WebSocketServer
from response_orchestrator import ResponseOrchestrator
from tuya_connection_manager import TuyaConnectionManager

# Initialize WebSocket server
ws_server = WebSocketServer(host='0.0.0.0', port=5000)

# Initialize Tuya connection manager
tuya_manager = TuyaConnectionManager(client_id, secret_key, device_ids)

# Initialize response orchestrator with WebSocket server
orchestrator = ResponseOrchestrator(
    tuya_manager=tuya_manager,
    socketio=ws_server.get_socketio(),
    smart_bulb_id=device_ids['SMART_BULB_ID'],
    siren_id=device_ids['SIREN_ID'],
    front_door_lock_id=device_ids['FRONT_DOOR_LOCK_ID']
)

# Run server in a separate thread or process
import threading
server_thread = threading.Thread(target=ws_server.run, daemon=True)
server_thread.start()

# Now orchestrator can broadcast status updates
orchestrator.execute_red_protocol('HOUSE')
```

### Example 3: Testing with HTML Client

1. Start the server:
   ```bash
   python backend/example_websocket_usage.py
   ```

2. Open `backend/test_client.html` in a web browser

3. The client will automatically connect and display:
   - Connection status
   - All received status updates with timestamps
   - Color-coded messages based on threat level

## Message Format

All status update messages follow this JSON format:

```json
{
    "status": "RED_CRITICAL" | "YELLOW_WARNING" | "GREEN_SAFE",
    "zone": "HOUSE" | "LivingRoom" | "Foyer" | "MasterBedroom"
}
```

## Endpoints

### HTTP Endpoints

- **GET /** - Health check endpoint
  - Returns: `{"status": "ok", "service": "tuya-security-digital-twin", "connected_clients": <count>}`

### WebSocket Events

**Client → Server:**
- `connect` - Establish connection
- `disconnect` - Close connection
- `ping` - Keep-alive ping

**Server → Client:**
- `connected` - Connection acknowledgment with client ID
- `status_update` - Security status update broadcast
- `pong` - Response to ping

## Dependencies

- Flask >= 2.3.0
- Flask-SocketIO >= 5.3.0
- Flask-CORS >= 4.0.0
- python-socketio >= 5.9.0

## Integration Notes

The WebSocket server is designed to integrate seamlessly with:

1. **Response Orchestrator**: Uses the SocketIO instance to broadcast status updates
2. **Frontend Visualization**: Clients connect to receive real-time security status
3. **AI Threat Analyzer**: Indirectly through the Response Orchestrator

## Testing Strategy

The implementation uses property-based testing with Hypothesis to verify:

1. **Connection acceptance** across multiple clients (1-10 clients)
2. **Message format consistency** across all status/zone combinations
3. **Cleanup behavior** when clients disconnect

Each test runs 100 iterations with randomly generated inputs to ensure robustness.

## Performance Considerations

- Uses Flask-SocketIO's threading mode for concurrent client handling
- Maintains a set of connected clients for O(1) lookup
- Broadcasts are non-blocking and don't wait for client acknowledgment
- Supports CORS for cross-origin frontend connections

## Security Considerations

- CORS is enabled for all origins (suitable for development)
- For production, configure CORS to allow only trusted origins
- Consider adding authentication/authorization for WebSocket connections
- Use HTTPS/WSS in production environments

## Troubleshooting

### Issue: Clients can't connect

**Solution**: Ensure the server is running and accessible:
```bash
curl http://localhost:5000/
```

### Issue: Messages not received

**Solution**: Check that clients are properly connected and listening for `status_update` events.

### Issue: Tests timeout

**Solution**: The tests have a 500ms deadline. If tests consistently timeout, increase the deadline in the test settings.

## Future Enhancements

Potential improvements for production use:

1. Add authentication/authorization for WebSocket connections
2. Implement message queuing for offline clients
3. Add message persistence and replay functionality
4. Implement rate limiting for broadcasts
5. Add metrics and monitoring endpoints
6. Support for multiple rooms/namespaces
7. Add SSL/TLS support for secure connections
