# Design Document

## Overview

This system implements an AI-powered IoT security platform that integrates Tuya smart home devices with real-time threat analysis and 3D visualization. The architecture consists of two main components:

1. **Backend System**: A Python Flask application that connects to Tuya Cloud via WebSocket, processes device events through an AI threat analyzer with time-contextual weighting, and controls actuator devices while broadcasting security status updates.

2. **Frontend System**: A web-based 3D digital twin built with Three.js that visualizes the home layout and reflects real-time security status through dynamic color changes.

The system moves beyond simple rule-based automation by incorporating temporal context into threat assessment, enabling predictive AI behavior that distinguishes normal activity patterns from genuine security threats.

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                        Tuya Cloud                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Sensors    │  │  Actuators   │  │  WebSocket   │     │
│  │  (Motion,    │  │  (Bulb,      │  │   Message    │     │
│  │  Vibration,  │  │  Siren,      │  │   Service    │     │
│  │  Lock)       │  │  Lock)       │  │              │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ WebSocket + REST API
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Backend System (Python)                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Tuya Connection Manager                  │  │
│  │  - WebSocket client for real-time events             │  │
│  │  - REST API client for device control                │  │
│  └──────────────────────────────────────────────────────┘  │
│                            │                                 │
│                            ▼                                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              AI Threat Analyzer                       │  │
│  │  - Event sequence buffer (last 3 events)             │  │
│  │  - Time-contextual threat scoring                    │  │
│  │  - Pattern detection (motion + vibration)            │  │
│  └──────────────────────────────────────────────────────┘  │
│                            │                                 │
│                            ▼                                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           Response Orchestrator                       │  │
│  │  - Actuator command dispatcher                        │  │
│  │  - Push notification sender                           │  │
│  │  - WebSocket broadcaster                              │  │
│  └──────────────────────────────────────────────────────┘  │
│                            │                                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           Flask WebSocket Server                      │  │
│  │  - Endpoint: ws://localhost:5000/ws                   │  │
│  │  - Broadcasts JSON status messages                    │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ WebSocket
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                Frontend System (Three.js)                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           WebSocket Client                            │  │
│  │  - Connects to backend                                │  │
│  │  - Receives status updates                            │  │
│  └──────────────────────────────────────────────────────┘  │
│                            │                                 │
│                            ▼                                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           3D Scene Manager                            │  │
│  │  - Three.js renderer                                  │  │
│  │  - Orthographic camera (top-down view)               │  │
│  │  - Zone meshes (Foyer, LivingRoom, MasterBedroom)   │  │
│  └──────────────────────────────────────────────────────┘  │
│                            │                                 │
│                            ▼                                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           Visualization Controller                    │  │
│  │  - Color state manager                                │  │
│  │  - Animation controller (flashing, transitions)      │  │
│  │  - Zone-specific updates                              │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

**Backend:**
- Python 3.8+
- Flask 2.3+ with Flask-SocketIO for WebSocket support
- tuya-connector-python SDK for Tuya Cloud integration
- datetime for time-contextual analysis

**Frontend:**
- HTML5/CSS3/JavaScript (ES6+)
- Three.js r150+ for 3D rendering
- Native WebSocket API for real-time communication

## Components and Interfaces

### Backend Components

#### 1. Tuya Connection Manager

**Responsibilities:**
- Initialize connection to Tuya Cloud using credentials
- Subscribe to WebSocket message service for device events
- Send control commands to actuator devices
- Handle connection failures and reconnection logic

**Key Methods:**
```python
class TuyaConnectionManager:
    def __init__(self, client_id: str, secret_key: str, device_ids: dict)
    def connect() -> bool
    def subscribe_to_devices(device_ids: list) -> None
    def send_command(device_id: str, commands: dict) -> bool
    def on_message(callback: Callable) -> None
    def reconnect() -> bool
```

**Configuration:**
```python
CONFIG = {
    'CLIENT_ID': 'your_tuya_client_id',
    'SECRET_KEY': 'your_tuya_secret_key',
    'DEVICES': {
        'LIVING_ROOM_MOTION_ID': 'device_id_1',
        'WINDOW_VIBRATION_ID': 'device_id_2',
        'FRONT_DOOR_LOCK_ID': 'device_id_3',
        'SMART_BULB_ID': 'device_id_4',
        'SIREN_ID': 'device_id_5'
    }
}
```

#### 2. AI Threat Analyzer

**Responsibilities:**
- Maintain event sequence buffer (last 3 events with timestamps)
- Calculate time-contextual threat scores
- Detect threat patterns (motion followed by vibration)
- Classify threats into RED_CRITICAL, YELLOW_WARNING, or GREEN_SAFE

**Key Methods:**
```python
class ThreatAnalyzer:
    def __init__(self)
    def add_event(device_id: str, event_data: dict, timestamp: datetime) -> None
    def calculate_threat_score(event_sequence: list) -> float
    def get_time_weight(current_time: datetime) -> float
    def analyze_sequence() -> tuple[str, str]  # Returns (status, zone)
    def clear_warnings() -> None
```

**Threat Scoring Algorithm:**
```
base_score = pattern_score  # 0-100 based on event pattern
time_weight = get_time_weight(current_time)
  - Nighttime (22:00-06:00): 1.5x multiplier
  - Daytime (06:00-22:00): 0.7x multiplier
final_score = base_score * time_weight

Classification:
  - final_score >= 80: RED_CRITICAL
  - 40 <= final_score < 80: YELLOW_WARNING
  - final_score < 40: GREEN_SAFE
```

**Pattern Detection:**
- Motion + Vibration within 10s: base_score = 90
- Motion alone (no follow-up): base_score = 50
- Door unlock event: base_score = 0 (safe arrival)

#### 3. Response Orchestrator

**Responsibilities:**
- Execute multi-step response protocols based on threat classification
- Dispatch commands to actuator devices
- Send push notifications to users (via mock/webhook service)
- Broadcast status updates to frontend clients

**Key Methods:**
```python
class ResponseOrchestrator:
    def __init__(self, tuya_manager: TuyaConnectionManager, socketio: SocketIO)
    def execute_red_protocol(zone: str) -> None
    def execute_yellow_protocol(zone: str) -> None
    def execute_green_protocol(zone: str) -> None
    def send_push_notification(message: str, priority: str) -> None
    def broadcast_status(status: str, zone: str) -> None
```

**Response Protocols:**

RED_CRITICAL:
1. Send command to SMART_BULB_ID: `{"commands": [{"code": "colour_data", "value": {"h": 0, "s": 1000, "v": 1000}}, {"code": "flash_scene", "value": "1"}]}`
2. Send command to SIREN_ID: `{"commands": [{"code": "alarm_switch", "value": true}]}`
3. Send command to FRONT_DOOR_LOCK_ID: `{"commands": [{"code": "lock", "value": true}]}`
4. Send push notification: `{"message": "CRITICAL: Break-in attempt detected!", "priority": "high"}` (via webhook to Discord/Slack or mock console output)
5. Broadcast: `{"status": "RED_CRITICAL", "zone": "HOUSE"}`

YELLOW_WARNING:
1. Send command to SMART_BULB_ID: `{"commands": [{"code": "colour_data", "value": {"h": 60, "s": 800, "v": 300}}, {"code": "work_mode", "value": "scene_1"}]}` (soft pulsing yellow at low brightness)
2. Broadcast: `{"status": "YELLOW_WARNING", "zone": "LivingRoom"}`

GREEN_SAFE:
1. Send command to SMART_BULB_ID: `{"commands": [{"code": "colour_data", "value": {"h": 30, "s": 200, "v": 200}}, {"code": "bright_value", "value": 20}]}`
2. Clear all warning states
3. Broadcast: `{"status": "GREEN_SAFE", "zone": "HOUSE"}`

**Push Notification Implementation Note:**
For hackathon purposes, push notifications are implemented as a webhook integration to a service like Discord, Slack, or a simple HTTP endpoint. This provides immediate visual feedback without requiring mobile app infrastructure. Alternative implementations include console logging with timestamp or email via SMTP.

#### 4. Flask WebSocket Server

**Responsibilities:**
- Accept WebSocket connections from frontend clients
- Maintain list of connected clients
- Broadcast JSON messages to all clients
- Handle client disconnections

**Endpoints:**
- `GET /`: Serve basic health check
- `WS /ws`: WebSocket endpoint for real-time communication

### Frontend Components

#### 1. WebSocket Client

**Responsibilities:**
- Establish connection to backend WebSocket server
- Parse incoming JSON messages
- Trigger visualization updates
- Handle reconnection on failure

**Key Functions:**
```javascript
class WebSocketClient {
    constructor(url)
    connect()
    onMessage(callback)
    reconnect()
    disconnect()
}
```

#### 2. 3D Scene Manager

**Responsibilities:**
- Initialize Three.js scene, camera, and renderer
- Create zone meshes with labels
- Set up lighting and materials
- Handle window resize events
- Render animation loop

**Key Functions:**
```javascript
class SceneManager {
    constructor(containerId)
    initScene()
    createZoneMesh(name, position, size)
    addLabel(text, position)
    animate()
    resize()
}
```

**Zone Layout:**
```
Top-down view (orthographic):

┌─────────────────────────────────────┐
│          Foyer (5x5 units)          │
│         Position: (0, 0, 0)         │
└─────────────────────────────────────┘
┌─────────────────────────────────────┐
│      LivingRoom (10x8 units)        │
│        Position: (0, 0, -8)         │
└─────────────────────────────────────┘
┌─────────────────────────────────────┐
│    MasterBedroom (8x8 units)        │
│       Position: (0, 0, -18)         │
└─────────────────────────────────────┘
```

#### 3. Visualization Controller

**Responsibilities:**
- Update zone colors based on status messages
- Animate color transitions
- Implement flashing effects for RED_CRITICAL
- Manage zone-specific vs. house-wide updates

**Key Functions:**
```javascript
class VisualizationController {
    constructor(sceneManager)
    updateDigitalTwin(status, zone)
    setZoneColor(zoneName, color, animated)
    flashAllZones(color, frequency)
    clearAnimations()
}
```

**Color Mappings:**
- RED_CRITICAL: `#FF0000` (flashing at 2Hz)
- YELLOW_WARNING: `#FFFF00` (solid)
- GREEN_SAFE: `#87CEEB` (subtle blue-white)
- Default: `#CCCCCC` (light gray)

## Data Models

### Event Model

```python
@dataclass
class SensorEvent:
    device_id: str
    device_type: str  # 'motion', 'vibration', 'lock'
    timestamp: datetime
    data: dict  # Raw event data from Tuya
    
    def age_seconds(self) -> float:
        """Calculate age of event in seconds"""
        return (datetime.now() - self.timestamp).total_seconds()
```

### Threat Assessment Model

```python
@dataclass
class ThreatAssessment:
    status: str  # 'RED_CRITICAL', 'YELLOW_WARNING', 'GREEN_SAFE'
    zone: str  # 'HOUSE', 'LivingRoom', 'Foyer', 'MasterBedroom'
    score: float  # 0-150 (base score * time weight)
    base_score: float  # 0-100
    time_weight: float  # 0.7-1.5
    timestamp: datetime
    triggering_events: list[SensorEvent]
    
    def to_json(self) -> dict:
        return {
            'status': self.status,
            'zone': self.zone
        }
```

### Device Command Model

```python
@dataclass
class DeviceCommand:
    device_id: str
    commands: list[dict]  # Tuya command format
    retry_count: int = 0
    max_retries: int = 3
    
    def to_tuya_format(self) -> dict:
        return {
            'commands': self.commands
        }
```

### WebSocket Message Model

```javascript
// Frontend message format
interface StatusMessage {
    status: 'RED_CRITICAL' | 'YELLOW_WARNING' | 'GREEN_SAFE';
    zone: 'HOUSE' | 'LivingRoom' | 'Foyer' | 'MasterBedroom';
}
```


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Configuration loading completeness
*For any* valid configuration source containing CLIENT_ID and SECRET_KEY, initializing the Backend System should successfully load both values into memory.
**Validates: Requirements 1.1**

### Property 2: Missing configuration rejection
*For any* configuration source with one or more missing required fields (CLIENT_ID, SECRET_KEY, or device IDs), the Backend System should log an error and prevent startup.
**Validates: Requirements 1.3**

### Property 3: Device subscription completeness
*For any* set of configured device IDs, after establishing a Tuya Cloud connection, the Backend System should subscribe to all devices in the configuration.
**Validates: Requirements 2.2**

### Property 4: Exponential backoff reconnection
*For any* sequence of connection failures, the Backend System should increase retry delays exponentially (e.g., 1s, 2s, 4s, 8s) up to a maximum delay.
**Validates: Requirements 2.4**

### Property 5: Command transmission for required actions
*For any* threat assessment requiring actuator response, the Backend System should invoke send_command with the correct device_id and commands for each required actuator.
**Validates: Requirements 3.1, 3.2**

### Property 6: Command logging consistency
*For any* command transmission attempt, the Backend System should create a log entry indicating success or failure.
**Validates: Requirements 3.3, 3.4**

### Property 7: Command retry on failure
*For any* failed command transmission, the Backend System should retry up to three times before giving up.
**Validates: Requirements 3.4**

### Property 8: Event sequence append
*For any* sensor event received, the Threat Analyzer should add the event with timestamp to the in-memory sequence.
**Validates: Requirements 4.1**

### Property 9: Event sequence bounded buffer
*For any* sequence of sensor events, the Threat Analyzer should maintain a maximum of three events, removing the oldest when a fourth arrives.
**Validates: Requirements 4.2**

### Property 10: Event sequence chronological ordering
*For any* event sequence, events should remain sorted by timestamp in ascending order.
**Validates: Requirements 4.3**

### Property 11: Time contextual weighting function
*For any* time of day, the Threat Analyzer should apply a multiplier greater than 1.0 for nighttime hours (22:00-06:00) and less than 1.0 for daytime hours (06:00-22:00).
**Validates: Requirements 4A.2, 4A.3**

### Property 12: Threat score classification
*For any* calculated threat score, the Threat Analyzer should classify as RED_CRITICAL when score >= 80, YELLOW_WARNING when 40 <= score < 80, and GREEN_SAFE when score < 40.
**Validates: Requirements 4A.4, 4A.5**

### Property 13: Motion-vibration pattern scoring
*For any* event sequence where WINDOW_VIBRATION_ID occurs within 10 seconds after LIVING_ROOM_MOTION_ID, the Threat Analyzer should calculate a threat score using time contextual weighting.
**Validates: Requirements 5.1**

### Property 14: RED_CRITICAL response protocol completeness
*For any* threat classified as RED_CRITICAL, the Backend System should execute all five required actions: send red strobe command to bulb, activate siren, lock door, send push notification, and broadcast WebSocket message with status RED_CRITICAL and zone HOUSE.
**Validates: Requirements 5.3, 5.4, 5.5, 5.6, 5.7**

### Property 15: YELLOW_WARNING graduated response
*For any* LIVING_ROOM_MOTION_ID event with no WINDOW_VIBRATION_ID follow-up within 10 seconds, the Threat Analyzer should classify as YELLOW_WARNING and the Backend System should send a soft pulsing yellow command to the bulb, broadcast the message, and NOT activate siren or lock.
**Validates: Requirements 6.1, 6.2, 6.3, 6.4**

### Property 16: Door unlock GREEN_SAFE classification
*For any* FRONT_DOOR_LOCK_ID status change to unlocked, the Threat Analyzer should classify as GREEN_SAFE.
**Validates: Requirements 7.1**

### Property 17: GREEN_SAFE response protocol
*For any* status classified as GREEN_SAFE, the Backend System should send warm white command to bulb at 20% brightness, clear all warning states, and broadcast WebSocket message with status GREEN_SAFE and zone HOUSE.
**Validates: Requirements 7.2, 7.3, 7.4**

### Property 18: WebSocket client connection acceptance
*For any* valid WebSocket connection attempt to the /ws endpoint, the Backend System should accept the connection and add the client to the broadcast list.
**Validates: Requirements 8.2**

### Property 19: Broadcast message format
*For any* security status change, the Backend System should broadcast a JSON message to all connected clients containing both "status" and "zone" fields.
**Validates: Requirements 8.3**

### Property 20: Client cleanup on disconnection
*For any* client disconnection, the Backend System should remove the client from the broadcast list such that future broadcasts do not attempt to send to that client.
**Validates: Requirements 8.4**

### Property 21: WebSocket message parsing
*For any* valid JSON message received by the Frontend System, the system should successfully extract both "status" and "zone" field values.
**Validates: Requirements 10.3**

### Property 22: Frontend reconnection timing
*For any* WebSocket connection failure, the Frontend System should attempt reconnection at 5-second intervals.
**Validates: Requirements 10.4**

### Property 23: Zone-specific color update
*For any* YELLOW_WARNING message with a specific zone, the Frontend System should change only that zone's mesh color to yellow while leaving other zones unchanged.
**Validates: Requirements 11.1**

### Property 24: House-wide RED_CRITICAL animation
*For any* RED_CRITICAL message, the Frontend System should apply flashing red animation to all three zone meshes (Foyer, LivingRoom, MasterBedroom).
**Validates: Requirements 11.2**

### Property 25: House-wide GREEN_SAFE color update
*For any* GREEN_SAFE message, the Frontend System should change all three zone meshes to blue-white color.
**Validates: Requirements 11.3**

### Property 26: Color transition animation timing
*For any* zone color change, the Frontend System should animate the transition over exactly one second.
**Validates: Requirements 11.4**


## Error Handling

### Backend Error Handling

#### Connection Errors

**Tuya Cloud Connection Failures:**
- Catch connection exceptions during initialization
- Log error with timestamp and error details
- Implement exponential backoff: 1s, 2s, 4s, 8s, 16s (max)
- Retry indefinitely until connection succeeds
- Emit system status event for monitoring

**WebSocket Server Errors:**
- Catch Flask-SocketIO initialization errors
- Log error and exit with non-zero status code
- Validate port availability before binding
- Handle client connection errors gracefully without crashing server

#### Device Command Errors

**Command Transmission Failures:**
- Catch Tuya API exceptions (timeout, authentication, device offline)
- Log error with device_id, command details, and error message
- Retry up to 3 times with 2-second delay between attempts
- After max retries, log final failure and continue operation
- Do not block other commands or threat analysis

**Invalid Command Format:**
- Validate command structure before transmission
- Log validation errors with details
- Skip invalid commands and continue with valid ones

#### Data Processing Errors

**Event Parsing Errors:**
- Catch JSON parsing exceptions from Tuya events
- Log malformed event data
- Skip invalid events and continue processing
- Maintain system stability despite bad data

**Threat Analysis Errors:**
- Catch exceptions in scoring calculations
- Log error with event sequence details
- Default to YELLOW_WARNING classification on error
- Continue processing subsequent events

#### Configuration Errors

**Missing Configuration:**
- Validate all required fields on startup
- Log specific missing fields
- Exit with clear error message and non-zero status
- Provide example configuration in error message

**Invalid Configuration:**
- Validate data types and formats
- Log validation errors with expected vs. actual values
- Exit with clear error message

### Frontend Error Handling

#### Connection Errors

**WebSocket Connection Failures:**
- Catch connection errors during initial connect
- Display user-friendly message: "Connecting to security system..."
- Implement reconnection with 5-second interval
- Update UI status indicator (connected/disconnected)

**Message Parsing Errors:**
- Catch JSON parsing exceptions
- Log error to console with raw message
- Skip invalid messages and continue listening
- Do not crash visualization

#### Rendering Errors

**Three.js Initialization Errors:**
- Catch WebGL context creation failures
- Display fallback message: "3D visualization not supported"
- Log error details to console
- Provide link to browser compatibility information

**Animation Errors:**
- Catch errors in animation loop
- Log error and attempt to restart animation
- Maintain last known good state if restart fails

#### Resource Errors

**Asset Loading Failures:**
- Handle missing or failed CDN resources
- Display error message if Three.js fails to load
- Provide fallback to text-based status display

## Testing Strategy

### Overview

This project employs a dual testing approach combining unit tests for specific scenarios and property-based tests for universal correctness guarantees. Unit tests validate concrete examples and integration points, while property-based tests verify that system behaviors hold across all possible inputs.

### Property-Based Testing

**Framework:** Hypothesis (Python) for backend, fast-check (JavaScript) for frontend

**Configuration:**
- Minimum 100 iterations per property test
- Seed-based reproducibility for failed tests
- Shrinking enabled to find minimal failing examples

**Test Organization:**
- Each property test must include a comment tag: `# Feature: tuya-security-digital-twin, Property X: [property description]`
- Property tests should be co-located with the modules they test
- One property test per correctness property from design document

**Backend Property Tests:**

1. **Configuration Properties (Properties 1-2):**
   - Generate random valid/invalid configuration dictionaries
   - Test loading and validation logic
   - Verify error handling for missing fields

2. **Event Sequence Properties (Properties 8-10):**
   - Generate random sequences of sensor events
   - Test buffer management (bounded to 3 events)
   - Verify chronological ordering maintained
   - Test with various timestamp patterns

3. **Threat Scoring Properties (Properties 11-13):**
   - Generate random times of day (0-24 hours)
   - Test time weighting function across all hours
   - Generate random event patterns (motion, vibration, unlock)
   - Verify score calculations and classifications
   - Test boundary conditions (score = 40, 80)

4. **Response Protocol Properties (Properties 14-17):**
   - Generate random threat classifications
   - Verify all required actions executed for each classification
   - Test command generation for actuators
   - Verify broadcast message format

5. **WebSocket Properties (Properties 18-20):**
   - Simulate random client connections/disconnections
   - Verify client list management
   - Test broadcast to multiple clients
   - Verify message format consistency

6. **Command Retry Properties (Properties 6-7):**
   - Simulate random failure patterns
   - Verify retry count and exponential backoff
   - Test logging for all outcomes

**Frontend Property Tests:**

1. **Message Parsing Properties (Property 21):**
   - Generate random valid JSON messages
   - Test extraction of status and zone fields
   - Verify handling of various message formats

2. **Color Update Properties (Properties 23-25):**
   - Generate random status messages
   - Verify correct zones updated for each status
   - Test color values match specifications
   - Verify zone isolation for YELLOW_WARNING

3. **Animation Properties (Properties 24, 26):**
   - Test flashing animation frequency for RED_CRITICAL
   - Verify transition timing (1 second)
   - Test animation cleanup

### Unit Testing

**Framework:** pytest (Python) for backend, Jest (JavaScript) for frontend

**Backend Unit Tests:**

1. **Tuya Connection Manager:**
   - Test successful connection with valid credentials
   - Test connection failure with invalid credentials
   - Test device subscription with specific device IDs
   - Test command sending with example commands

2. **Threat Analyzer:**
   - Test specific threat scenarios:
     - Motion at 3:00 AM followed by vibration → RED_CRITICAL
     - Motion at 2:00 PM with no follow-up → YELLOW_WARNING
     - Door unlock at 6:00 PM → GREEN_SAFE
   - Test edge cases:
     - Empty event sequence
     - Single event in sequence
     - Events exactly 10 seconds apart

3. **Response Orchestrator:**
   - Test RED_CRITICAL protocol with mock devices
   - Test YELLOW_WARNING protocol (no actuator commands)
   - Test GREEN_SAFE protocol with mock devices
   - Test push notification sending

4. **Flask WebSocket Server:**
   - Test server initialization
   - Test client connection handling
   - Test broadcast to multiple clients
   - Test client disconnection cleanup

**Frontend Unit Tests:**

1. **WebSocket Client:**
   - Test connection establishment
   - Test message reception
   - Test reconnection logic
   - Test error handling

2. **Scene Manager:**
   - Test scene initialization
   - Test zone mesh creation (3 zones)
   - Test camera setup (orthographic, top-down)
   - Test resize handling

3. **Visualization Controller:**
   - Test specific color updates:
     - YELLOW_WARNING → LivingRoom yellow
     - RED_CRITICAL → All zones flashing red
     - GREEN_SAFE → All zones blue-white
   - Test animation start/stop
   - Test zone isolation

### Integration Testing

**Backend Integration:**
- Test end-to-end flow: Tuya event → Threat analysis → Actuator commands → WebSocket broadcast
- Use mock Tuya Cloud connection for reproducibility
- Verify timing constraints (10-second window for motion+vibration)
- Test with realistic event sequences

**Frontend Integration:**
- Test WebSocket connection to real backend server
- Verify 3D scene updates in response to backend messages
- Test reconnection after backend restart
- Verify animation performance

### Test Execution

**Backend:**
```bash
# Run all tests
pytest tests/ -v

# Run property tests only
pytest tests/ -v -m property

# Run unit tests only
pytest tests/ -v -m unit

# Run with coverage
pytest tests/ --cov=ai_agent --cov-report=html
```

**Frontend:**
```bash
# Run all tests
npm test

# Run with coverage
npm test -- --coverage

# Run in watch mode during development
npm test -- --watch
```

### Continuous Integration

- Run all tests on every commit
- Require 80% code coverage for backend
- Require 70% code coverage for frontend
- Property tests must pass with 100 iterations minimum
- Integration tests run in isolated environment with mock Tuya Cloud

### Manual Testing

**Backend:**
- Test with real Tuya devices in development environment
- Verify actuator responses (bulb colors, siren, lock)
- Test reconnection by disconnecting network
- Verify push notifications on mobile device

**Frontend:**
- Test in multiple browsers (Chrome, Firefox, Safari)
- Verify 3D rendering performance
- Test WebSocket reconnection by stopping backend
- Verify color animations and transitions
- Test on different screen sizes

