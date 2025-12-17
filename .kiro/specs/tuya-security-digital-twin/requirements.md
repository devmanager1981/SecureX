# Requirements Document

## Introduction

This document specifies the requirements for a full-stack IoT security system that integrates Tuya smart home devices with AI-powered threat analysis and real-time 3D visualization. The system monitors virtual sensor devices, analyzes event sequences to detect security threats, controls actuator devices in response to threats, and provides a digital twin visualization of the home security status using Three.js.

## Glossary

- **Backend System**: The Python-based server application that connects to Tuya Cloud, processes device events, and serves WebSocket connections
- **Frontend System**: The web-based 3D visualization application built with Three.js
- **Tuya Cloud**: The cloud platform providing IoT device management and real-time event streaming
- **Digital Twin**: A 3D virtual representation of the physical home that reflects real-time security status
- **Threat Analyzer**: The component that evaluates sensor event sequences to determine security threat levels using time-contextual weighting
- **Time Contextual Weighting**: A threat scoring mechanism that adjusts threat severity based on time of day
- **Threat Score**: A numerical value representing the calculated security risk level based on event patterns and temporal context
- **Actuator**: A controllable IoT device (smart bulb, siren, door lock) that responds to security events
- **Push Alert**: A notification message sent to the user's device to inform them of critical security events
- **Sensor**: A monitoring IoT device (motion detector, vibration sensor, door lock status) that reports events
- **Event Sequence**: A time-ordered collection of sensor events used for threat pattern detection
- **Status Code**: A classification of security state (RED_CRITICAL, YELLOW_WARNING, GREEN_SAFE)
- **Zone**: A labeled area of the home (LivingRoom, Foyer, MasterBedroom, HOUSE)

## Requirements

### Requirement 1

**User Story:** As a system administrator, I want to configure Tuya API credentials and device identifiers, so that the Backend System can authenticate and communicate with my specific IoT devices.

#### Acceptance Criteria

1. WHEN the Backend System initializes THEN the Backend System SHALL load configuration values for CLIENT_ID and SECRET_KEY
2. WHEN the Backend System initializes THEN the Backend System SHALL load device identifiers for LIVING_ROOM_MOTION_ID, WINDOW_VIBRATION_ID, FRONT_DOOR_LOCK_ID, SMART_BULB_ID, and SIREN_ID
3. WHEN configuration values are missing THEN the Backend System SHALL log an error message and prevent startup

### Requirement 2

**User Story:** As a developer, I want the Backend System to establish a WebSocket connection to Tuya Cloud, so that I can receive real-time device status updates without polling.

#### Acceptance Criteria

1. WHEN the Backend System starts THEN the Backend System SHALL initialize a connection to Tuya Cloud using the tuya-connector-python SDK
2. WHEN the Tuya Cloud connection is established THEN the Backend System SHALL subscribe to WebSocket message service for all five configured device IDs
3. WHEN a device status change occurs THEN the Tuya Cloud SHALL push a real-time event message to the Backend System
4. WHEN the WebSocket connection fails THEN the Backend System SHALL attempt reconnection with exponential backoff

### Requirement 3

**User Story:** As a security system operator, I want the Backend System to send control commands to actuator devices, so that the system can respond automatically to security threats.

#### Acceptance Criteria

1. WHEN the Threat Analyzer determines an action is required THEN the Backend System SHALL invoke the send_command function with device_id and commands parameters
2. WHEN send_command is invoked THEN the Backend System SHALL transmit the control command to the specified device via Tuya Cloud API
3. WHEN a command transmission succeeds THEN the Backend System SHALL log the successful action
4. WHEN a command transmission fails THEN the Backend System SHALL log the error and retry up to three times

### Requirement 4

**User Story:** As a security analyst, I want the Threat Analyzer to maintain a sequence of recent sensor events, so that temporal patterns can be detected for threat assessment.

#### Acceptance Criteria

1. WHEN a sensor event is received THEN the Threat Analyzer SHALL append the event to an in-memory sequence with timestamp
2. WHEN the event sequence exceeds three events THEN the Threat Analyzer SHALL remove the oldest event to maintain a maximum length of three
3. WHEN an event is added to the sequence THEN the Threat Analyzer SHALL preserve the chronological order of events
4. WHEN the Backend System restarts THEN the Threat Analyzer SHALL initialize with an empty event sequence

### Requirement 4A

**User Story:** As a security analyst, I want the Threat Analyzer to incorporate time-of-day context into threat assessment, so that the system can distinguish between normal and suspicious activity patterns based on temporal context.

#### Acceptance Criteria

1. WHEN the Threat Analyzer evaluates an event sequence THEN the Threat Analyzer SHALL retrieve the current time of day
2. WHEN calculating a threat score THEN the Threat Analyzer SHALL apply time contextual weighting where nighttime hours (10:00 PM to 6:00 AM) increase the threat score multiplier
3. WHEN calculating a threat score THEN the Threat Analyzer SHALL apply time contextual weighting where daytime hours (6:00 AM to 10:00 PM) decrease the threat score multiplier
4. WHEN the final threat score exceeds the critical threshold THEN the Threat Analyzer SHALL classify the threat as RED_CRITICAL
5. WHEN the final threat score is between warning and critical thresholds THEN the Threat Analyzer SHALL classify the threat as YELLOW_WARNING

### Requirement 5

**User Story:** As a homeowner, I want the system to detect critical break-in attempts, so that immediate protective actions can be taken and I am notified immediately.

#### Acceptance Criteria

1. WHEN WINDOW_VIBRATION_ID reports an event within ten seconds after LIVING_ROOM_MOTION_ID reports an event THEN the Threat Analyzer SHALL calculate a threat score using time contextual weighting
2. WHEN the calculated threat score exceeds the critical threshold THEN the Threat Analyzer SHALL classify the threat as RED_CRITICAL
3. WHEN the threat is classified as RED_CRITICAL THEN the Backend System SHALL send a command to SMART_BULB_ID to activate red strobe mode
4. WHEN the threat is classified as RED_CRITICAL THEN the Backend System SHALL send a command to SIREN_ID to activate
5. WHEN the threat is classified as RED_CRITICAL THEN the Backend System SHALL send a command to FRONT_DOOR_LOCK_ID to lock
6. WHEN the threat is classified as RED_CRITICAL THEN the Backend System SHALL send a critical push alert notification to the user
7. WHEN the threat is classified as RED_CRITICAL THEN the Backend System SHALL broadcast a WebSocket message with status RED_CRITICAL and zone HOUSE

### Requirement 6

**User Story:** As a homeowner, I want the system to detect potential security concerns and take pre-emptive non-alarming actions, so that I can be alerted to investigate unusual activity while the system provides graduated response.

#### Acceptance Criteria

1. WHEN LIVING_ROOM_MOTION_ID reports an event and no WINDOW_VIBRATION_ID event follows within ten seconds THEN the Threat Analyzer SHALL classify the threat as YELLOW_WARNING
2. WHEN the threat is classified as YELLOW_WARNING THEN the Backend System SHALL send a command to SMART_BULB_ID to activate soft pulsing yellow at low brightness
3. WHEN the threat is classified as YELLOW_WARNING THEN the Backend System SHALL broadcast a WebSocket message with status YELLOW_WARNING and zone LivingRoom
4. WHEN the threat is classified as YELLOW_WARNING THEN the Backend System SHALL NOT send commands to SIREN_ID or FRONT_DOOR_LOCK_ID

### Requirement 7

**User Story:** As a homeowner, I want the system to recognize when I arrive home safely, so that the environment adjusts to a welcoming state.

#### Acceptance Criteria

1. WHEN FRONT_DOOR_LOCK_ID status changes to unlocked THEN the Threat Analyzer SHALL classify the status as GREEN_SAFE
2. WHEN the status is classified as GREEN_SAFE THEN the Backend System SHALL send a command to SMART_BULB_ID to set warm white color at twenty percent brightness
3. WHEN the status is classified as GREEN_SAFE THEN the Backend System SHALL clear all active warning states
4. WHEN the status is classified as GREEN_SAFE THEN the Backend System SHALL broadcast a WebSocket message with status GREEN_SAFE and zone HOUSE

### Requirement 8

**User Story:** As a frontend developer, I want the Backend System to provide a WebSocket server endpoint, so that the Frontend System can receive real-time security status updates.

#### Acceptance Criteria

1. WHEN the Backend System starts THEN the Backend System SHALL create a Flask WebSocket server listening on port 5000
2. WHEN a client connects to the WebSocket endpoint THEN the Backend System SHALL accept the connection
3. WHEN a security status change occurs THEN the Backend System SHALL broadcast a JSON message containing status and zone fields to all connected clients
4. WHEN a client disconnects THEN the Backend System SHALL remove the client from the broadcast list

### Requirement 9

**User Story:** As a user, I want to view a 3D representation of my home, so that I can understand the physical layout and security zones.

#### Acceptance Criteria

1. WHEN the Frontend System loads THEN the Frontend System SHALL initialize a Three.js scene with orthographic top-down camera view
2. WHEN the scene is initialized THEN the Frontend System SHALL render three labeled box-shaped meshes representing Foyer, LivingRoom, and MasterBedroom zones
3. WHEN the scene is rendered THEN the Frontend System SHALL display zone labels clearly visible to the user
4. WHEN the user views the scene THEN the Frontend System SHALL maintain a consistent wireframe visual style

### Requirement 10

**User Story:** As a user, I want the 3D visualization to connect to the Backend System, so that security status updates are reflected in real-time.

#### Acceptance Criteria

1. WHEN the Frontend System loads THEN the Frontend System SHALL establish a WebSocket connection to ws://localhost:5000/ws
2. WHEN the WebSocket connection is established THEN the Frontend System SHALL listen for incoming JSON messages
3. WHEN a JSON message is received THEN the Frontend System SHALL parse the status and zone fields
4. WHEN the WebSocket connection fails THEN the Frontend System SHALL attempt reconnection every five seconds

### Requirement 11

**User Story:** As a user, I want the 3D zones to change color based on security status, so that I can quickly assess the current threat level.

#### Acceptance Criteria

1. WHEN a message with status YELLOW_WARNING and zone LivingRoom is received THEN the Frontend System SHALL change only the LivingRoom mesh color to yellow
2. WHEN a message with status RED_CRITICAL is received THEN the Frontend System SHALL change all three zone meshes to flashing red animation
3. WHEN a message with status GREEN_SAFE is received THEN the Frontend System SHALL change all three zone meshes to subtle blue-white color
4. WHEN a zone color changes THEN the Frontend System SHALL animate the transition smoothly over one second

### Requirement 12

**User Story:** As a developer, I want clear dependency specifications, so that I can set up the development environment correctly.

#### Acceptance Criteria

1. WHEN the project is distributed THEN the Backend System SHALL include a requirements.txt file listing tuya-connector-python and Flask dependencies
2. WHEN the project is distributed THEN the Frontend System SHALL load Three.js library via CDN link in the HTML file
3. WHEN dependencies are installed from requirements.txt THEN the Backend System SHALL have all necessary packages to run without errors
