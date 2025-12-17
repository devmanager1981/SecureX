# Implementation Plan

- [x] 1. Set up project structure and dependencies





  - Create root directory structure with backend and frontend folders
  - Create requirements.txt with tuya-connector-python, Flask, Flask-SocketIO, hypothesis, pytest dependencies
  - Create frontend/index.html with Three.js CDN link
  - Create basic README.md with setup instructions
  - _Requirements: 12.1, 12.2, 12.3_

- [x] 2. Implement configuration management




  - Create config.py with placeholders for CLIENT_ID, SECRET_KEY, and five device IDs
  - Implement configuration loading function that reads from environment variables or config file
  - Add validation to check all required fields are present
  - Implement error logging and startup prevention for missing configuration
  - _Requirements: 1.1, 1.2, 1.3_

- [x] 2.1 Write property test for configuration loading


  - **Property 1: Configuration loading completeness**
  - **Validates: Requirements 1.1**

- [x] 2.2 Write property test for missing configuration rejection


  - **Property 2: Missing configuration rejection**
  - **Validates: Requirements 1.3**

- [x] 3. Implement Tuya Connection Manager





  - Create TuyaConnectionManager class with initialization method
  - Implement connect() method using tuya-connector-python SDK
  - Implement subscribe_to_devices() method for WebSocket message service
  - Implement send_command() method for device control via Tuya API
  - Add connection failure handling with exponential backoff reconnection logic
  - _Requirements: 2.1, 2.2, 2.4, 3.1, 3.2_

- [x] 3.1 Write property test for device subscription completeness


  - **Property 3: Device subscription completeness**
  - **Validates: Requirements 2.2**

- [x] 3.2 Write property test for exponential backoff reconnection

  - **Property 4: Exponential backoff reconnection**
  - **Validates: Requirements 2.4**

- [x] 3.3 Write property test for command transmission

  - **Property 5: Command transmission for required actions**
  - **Validates: Requirements 3.1, 3.2**

- [x] 3.4 Write property test for command logging

  - **Property 6: Command logging consistency**
  - **Validates: Requirements 3.3, 3.4**

- [x] 3.5 Write property test for command retry on failure

  - **Property 7: Command retry on failure**
  - **Validates: Requirements 3.4**

- [x] 4. Implement AI Threat Analyzer core





  - Create ThreatAnalyzer class with event sequence buffer (max 3 events)
  - Implement add_event() method that appends events with timestamps
  - Implement bounded buffer logic that removes oldest event when exceeding 3
  - Ensure chronological ordering is maintained
  - Implement clear_warnings() method to reset state
  - _Requirements: 4.1, 4.2, 4.3, 4.4_

- [x] 4.1 Write property test for event sequence append


  - **Property 8: Event sequence append**
  - **Validates: Requirements 4.1**

- [x] 4.2 Write property test for bounded buffer


  - **Property 9: Event sequence bounded buffer**
  - **Validates: Requirements 4.2**

- [x] 4.3 Write property test for chronological ordering


  - **Property 10: Event sequence chronological ordering**
  - **Validates: Requirements 4.3**

- [x] 5. Implement time-contextual threat scoring




  - Implement get_time_weight() method that returns multiplier based on time of day
  - Apply 1.5x multiplier for nighttime hours (22:00-06:00)
  - Apply 0.7x multiplier for daytime hours (06:00-22:00)
  - Implement calculate_threat_score() method that combines base score with time weight
  - Implement classification logic: score >= 80 → RED_CRITICAL, 40-79 → YELLOW_WARNING, < 40 → GREEN_SAFE
  - _Requirements: 4A.1, 4A.2, 4A.3, 4A.4, 4A.5_

- [x] 5.1 Write property test for time contextual weighting


  - **Property 11: Time contextual weighting function**
  - **Validates: Requirements 4A.2, 4A.3**

- [x] 5.2 Write property test for threat score classification


  - **Property 12: Threat score classification**
  - **Validates: Requirements 4A.4, 4A.5**

- [x] 6. Implement pattern detection and threat analysis





  - Implement analyze_sequence() method that detects motion + vibration pattern
  - Check if WINDOW_VIBRATION_ID occurs within 10 seconds after LIVING_ROOM_MOTION_ID
  - Assign base_score = 90 for motion + vibration pattern
  - Assign base_score = 50 for motion alone (no follow-up within 10 seconds)
  - Assign base_score = 0 for FRONT_DOOR_LOCK_ID unlock event
  - Return tuple of (status, zone) from analyze_sequence()
  - _Requirements: 5.1, 6.1, 7.1_

- [x] 6.1 Write property test for motion-vibration pattern scoring


  - **Property 13: Motion-vibration pattern scoring**
  - **Validates: Requirements 5.1**

- [x] 6.2 Write property test for door unlock classification


  - **Property 16: Door unlock GREEN_SAFE classification**
  - **Validates: Requirements 7.1**

- [x] 7. Implement Response Orchestrator




  - Create ResponseOrchestrator class with references to TuyaConnectionManager and SocketIO
  - Implement execute_red_protocol() method with all 5 actions (bulb strobe, siren, lock, notification, broadcast)
  - Implement execute_yellow_protocol() method with bulb pulsing yellow and broadcast
  - Implement execute_green_protocol() method with bulb warm white, clear warnings, broadcast
  - Implement send_push_notification() as webhook to Discord/Slack or console mock
  - Implement broadcast_status() method to send JSON to all WebSocket clients
  - _Requirements: 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 6.2, 6.3, 7.2, 7.3, 7.4_

- [x] 7.1 Write property test for RED_CRITICAL response protocol


  - **Property 14: RED_CRITICAL response protocol completeness**
  - **Validates: Requirements 5.3, 5.4, 5.5, 5.6, 5.7**

- [x] 7.2 Write property test for YELLOW_WARNING graduated response


  - **Property 15: YELLOW_WARNING graduated response**
  - **Validates: Requirements 6.1, 6.2, 6.3, 6.4**

- [x] 7.3 Write property test for GREEN_SAFE response protocol


  - **Property 17: GREEN_SAFE response protocol**
  - **Validates: Requirements 7.2, 7.3, 7.4**

- [x] 8. Implement Flask WebSocket server





  - Create Flask app with Flask-SocketIO extension
  - Implement /ws WebSocket endpoint
  - Implement connection handler that adds clients to broadcast list
  - Implement disconnection handler that removes clients from list
  - Implement broadcast function that sends JSON to all connected clients
  - Add health check endpoint at GET /
  - _Requirements: 8.1, 8.2, 8.3, 8.4_

- [x] 8.1 Write property test for client connection acceptance


  - **Property 18: WebSocket client connection acceptance**
  - **Validates: Requirements 8.2**

- [x] 8.2 Write property test for broadcast message format


  - **Property 19: Broadcast message format**
  - **Validates: Requirements 8.3**

- [x] 8.3 Write property test for client cleanup on disconnection


  - **Property 20: Client cleanup on disconnection**
  - **Validates: Requirements 8.4**

- [x] 9. Integrate components in main ai_agent.py





  - Create main ai_agent.py that initializes all components
  - Wire TuyaConnectionManager to receive events and pass to ThreatAnalyzer
  - Wire ThreatAnalyzer output to ResponseOrchestrator
  - Wire ResponseOrchestrator to Flask WebSocket server for broadcasts
  - Implement event loop that processes Tuya events in real-time
  - Add graceful shutdown handling
  - _Requirements: 2.3, 4.1, 5.1_

- [x] 10. Checkpoint - Ensure backend tests pass





  - Ensure all tests pass, ask the user if questions arise

- [x] 11. Implement frontend Three.js scene setup




  - Create frontend/index.html with basic HTML structure
  - Add Three.js library via CDN
  - Initialize Three.js scene with orthographic camera (top-down view)
  - Set up renderer and attach to DOM
  - Implement window resize handler
  - Create animation loop
  - _Requirements: 9.1, 12.2_

- [x] 12. Implement 3D zone meshes





  - Create three box-shaped meshes for Foyer, LivingRoom, MasterBedroom
  - Position meshes in top-down layout (Foyer at origin, LivingRoom below, MasterBedroom at bottom)
  - Add text labels for each zone using CSS2DRenderer or sprite labels
  - Apply wireframe material with default light gray color
  - Add meshes to scene
  - _Requirements: 9.2_

- [x] 13. Implement frontend WebSocket client





  - Create WebSocketClient class that connects to ws://localhost:5000/ws
  - Implement connection establishment on page load
  - Implement message listener that parses JSON
  - Implement reconnection logic with 5-second interval on failure
  - Add connection status indicator in UI
  - _Requirements: 10.1, 10.2, 10.3, 10.4_

- [x] 13.1 Write property test for message parsing


  - **Property 21: WebSocket message parsing**
  - **Validates: Requirements 10.3**

- [x] 13.2 Write property test for reconnection timing


  - **Property 22: Frontend reconnection timing**
  - **Validates: Requirements 10.4**

- [x] 14. Implement Visualization Controller





  - Create VisualizationController class with reference to scene meshes
  - Implement updateDigitalTwin(status, zone) method
  - Implement setZoneColor() method for zone-specific color changes
  - Implement flashAllZones() method for RED_CRITICAL flashing animation at 2Hz
  - Implement smooth color transitions over 1 second using Tween.js or manual interpolation
  - Wire WebSocket message handler to call updateDigitalTwin()
  - _Requirements: 11.1, 11.2, 11.3, 11.4_

- [x] 14.1 Write property test for zone-specific color update


  - **Property 23: Zone-specific color update**
  - **Validates: Requirements 11.1**

- [x] 14.2 Write property test for house-wide RED_CRITICAL animation


  - **Property 24: House-wide RED_CRITICAL animation**
  - **Validates: Requirements 11.2**

- [x] 14.3 Write property test for house-wide GREEN_SAFE color update


  - **Property 25: House-wide GREEN_SAFE color update**
  - **Validates: Requirements 11.3**

- [x] 14.4 Write property test for color transition timing


  - **Property 26: Color transition animation timing**
  - **Validates: Requirements 11.4**

- [x] 15. Add CSS styling to frontend





  - Create embedded CSS for full-screen 3D canvas
  - Style connection status indicator
  - Add basic typography and layout
  - Ensure responsive design for different screen sizes
  - _Requirements: 9.3, 9.4_

- [x] 16. Create example configuration file





  - Create config.example.py with placeholder values
  - Document how to obtain Tuya API credentials
  - Document how to find device IDs from Tuya IoT Platform
  - Add instructions for setting up webhook URL for push notifications
  - _Requirements: 1.1, 1.2_

- [x] 17. Write project documentation




  - Create comprehensive README.md with project overview
  - Add setup instructions for backend (pip install, configuration)
  - Add setup instructions for frontend (open in browser)
  - Document the three threat scenarios with examples
  - Add architecture diagram
  - Include troubleshooting section
  - _Requirements: All_

- [x] 18. Final checkpoint - End-to-end testing



  - Ensure all tests pass, ask the user if questions arise

- [x] 19. Generate Tuya Real Integration Test Suite




  - Register a new Pytest marker named `integration` in `pytest.ini`
  - Create `backend/test_tuya_integration.py` with integration tests
  - Add fixture with `@pytest.mark.skipif` to skip tests unless `TUYA_RUN_INTEGRATION` environment variable is set to `'true'`
  - Implement Test 1: Authentication failure test that attempts to initialize un-mocked `TuyaConnectionManager` with placeholder credentials and asserts authentication error (HTTP 401)
  - Implement Test 2: Device reachability failure test that attempts to fetch status of `LIVING_ROOM_MOTION_ID` and asserts device not found error
  - Implement Test 3: Actuator command failure test that attempts to send command to `SMART_BULB_ID` and asserts failure response
  - _Requirements: 1.1, 2.1, 3.1_
