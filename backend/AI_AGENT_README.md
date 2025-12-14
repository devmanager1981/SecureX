# AI Agent - Main Integration Module

## Overview

The AI Agent (`ai_agent.py`) is the main integration module that wires together all components of the Tuya Security Digital Twin system:

- **TuyaConnectionManager**: Handles connection to Tuya Cloud and device communication
- **ThreatAnalyzer**: Processes sensor events and detects threat patterns
- **ResponseOrchestrator**: Executes response protocols based on threat classifications
- **WebSocketServer**: Broadcasts security status updates to frontend clients

## Architecture

```
Tuya Cloud → TuyaConnectionManager → ThreatAnalyzer → ResponseOrchestrator → WebSocketServer → Frontend
```

## Configuration

Before running the AI Agent, you must set the following environment variables:

```bash
export CLIENT_ID="your_tuya_client_id"
export SECRET_KEY="your_tuya_secret_key"
export LIVING_ROOM_MOTION_ID="device_id_1"
export WINDOW_VIBRATION_ID="device_id_2"
export FRONT_DOOR_LOCK_ID="device_id_3"
export SMART_BULB_ID="device_id_4"
export SIREN_ID="device_id_5"
```

## Running the AI Agent

### Basic Usage

```bash
cd backend
python ai_agent.py
```

### Expected Output

```
============================================================
Tuya Security Digital Twin - AI Agent
============================================================
2024-XX-XX XX:XX:XX - __main__ - INFO - Initializing AI Agent...
2024-XX-XX XX:XX:XX - __main__ - INFO - Configuration loaded successfully
2024-XX-XX XX:XX:XX - __main__ - INFO - AI Agent initialized
2024-XX-XX XX:XX:XX - __main__ - INFO - Starting AI Agent...
2024-XX-XX XX:XX:XX - __main__ - INFO - Initializing system components...
2024-XX-XX XX:XX:XX - websocket_server - INFO - WebSocketServer initialized on 0.0.0.0:5000
2024-XX-XX XX:XX:XX - tuya_connection_manager - INFO - TuyaConnectionManager initialized
2024-XX-XX XX:XX:XX - threat_analyzer - INFO - ThreatAnalyzer initialized
2024-XX-XX XX:XX:XX - response_orchestrator - INFO - ResponseOrchestrator initialized
2024-XX-XX XX:XX:XX - __main__ - INFO - All components initialized successfully
2024-XX-XX XX:XX:XX - __main__ - INFO - Connecting to Tuya Cloud...
2024-XX-XX XX:XX:XX - tuya_connection_manager - INFO - Attempting to connect to Tuya Cloud (attempt 1)...
2024-XX-XX XX:XX:XX - tuya_connection_manager - INFO - Successfully connected to Tuya Cloud
2024-XX-XX XX:XX:XX - __main__ - INFO - Connected to Tuya Cloud successfully
2024-XX-XX XX:XX:XX - __main__ - INFO - Message callback registered
2024-XX-XX XX:XX:XX - tuya_connection_manager - INFO - Subscribing to 5 devices...
2024-XX-XX XX:XX:XX - tuya_connection_manager - INFO - Successfully subscribed to devices: [...]
2024-XX-XX XX:XX:XX - __main__ - INFO - Subscribed to 5 devices
2024-XX-XX XX:XX:XX - __main__ - INFO - WebSocket server started in background thread
2024-XX-XX XX:XX:XX - __main__ - INFO - AI Agent is now running. Press Ctrl+C to stop.
============================================================
```

## Event Processing Flow

1. **Device Event Received**: Tuya Cloud pushes a device status change via WebSocket
2. **Event Added to Buffer**: ThreatAnalyzer adds the event to its bounded buffer (max 3 events)
3. **Sequence Analysis**: ThreatAnalyzer analyzes the event sequence for threat patterns
4. **Threat Classification**: Events are classified as RED_CRITICAL, YELLOW_WARNING, or GREEN_SAFE
5. **Response Execution**: ResponseOrchestrator executes the appropriate protocol
6. **Status Broadcast**: WebSocketServer broadcasts the status update to all connected frontend clients

## Threat Patterns

### RED_CRITICAL (Break-in Attempt)
- **Pattern**: Motion detected followed by window vibration within 10 seconds
- **Response**: 
  - Smart bulb → Red strobe mode
  - Siren → Activated
  - Front door → Locked
  - Push notification sent
  - WebSocket broadcast: `{"status": "RED_CRITICAL", "zone": "HOUSE"}`

### YELLOW_WARNING (Potential Concern)
- **Pattern**: Motion detected with no vibration follow-up within 10 seconds
- **Response**:
  - Smart bulb → Soft pulsing yellow at low brightness
  - WebSocket broadcast: `{"status": "YELLOW_WARNING", "zone": "LivingRoom"}`

### GREEN_SAFE (Safe Arrival)
- **Pattern**: Front door unlocked
- **Response**:
  - Smart bulb → Warm white at 20% brightness
  - Clear all warning states
  - WebSocket broadcast: `{"status": "GREEN_SAFE", "zone": "HOUSE"}`

## Graceful Shutdown

The AI Agent handles shutdown signals gracefully:

- Press `Ctrl+C` to initiate shutdown
- The agent will:
  1. Stop processing new events
  2. Disconnect from Tuya Cloud
  3. Stop the WebSocket server
  4. Clean up resources

## Testing

Run the integration tests to verify the AI Agent works correctly:

```bash
cd backend
python -m pytest test_ai_agent_integration.py -v
```

## Troubleshooting

### Connection Issues

If the agent fails to connect to Tuya Cloud:
- Verify your CLIENT_ID and SECRET_KEY are correct
- Check your internet connection
- Ensure you're using the correct Tuya Cloud endpoint for your region
- The agent will automatically retry with exponential backoff

### Device Subscription Issues

If devices are not responding:
- Verify all device IDs are correct
- Ensure devices are online in the Tuya app
- Check that devices are associated with your Tuya account

### WebSocket Server Issues

If the WebSocket server fails to start:
- Verify port 5000 is not already in use
- Check firewall settings
- Ensure Flask and Flask-SocketIO are installed

## Requirements Validation

This implementation satisfies the following requirements:

- **Requirement 2.3**: Receives real-time event messages from Tuya Cloud via WebSocket
- **Requirement 4.1**: Appends sensor events to in-memory sequence with timestamp
- **Requirement 5.1**: Detects motion + vibration pattern and calculates threat score with time-contextual weighting

## Next Steps

After starting the AI Agent:

1. Open the frontend application in a web browser
2. The frontend will connect to `ws://localhost:5000/ws`
3. Trigger device events (motion, vibration, door unlock)
4. Observe the 3D visualization update in real-time
5. Monitor the console logs for detailed event processing information
