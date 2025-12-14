"""
AI Agent - Main integration module for Tuya Security Digital Twin system.

This module wires together all components:
- TuyaConnectionManager for device communication
- ThreatAnalyzer for event processing and threat detection
- ResponseOrchestrator for executing response protocols
- WebSocketServer for broadcasting status updates to frontend

The agent processes Tuya device events in real-time, analyzes threat patterns,
and coordinates appropriate responses.
"""

import logging
import signal
import sys
import time
from datetime import datetime
from typing import Optional
# dotenv import removed - handled in config.py

from config import load_config
from tuya_connection_manager import TuyaConnectionManager
from threat_analyzer import ThreatAnalyzer
from response_orchestrator import ResponseOrchestrator
from websocket_server import WebSocketServer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AIAgent:
    """
    Main AI Agent that integrates all system components.
    
    Coordinates the flow of data from Tuya devices through threat analysis
    to response execution and frontend visualization.
    """
    
    def __init__(self):
        """Initialize AI Agent and all components."""
        logger.info("Initializing AI Agent...")
        
        # Load configuration
        try:
            self.config = load_config()
            logger.info("Configuration loaded successfully")
        except ValueError as e:
            logger.error(f"Configuration error: {e}")
            sys.exit(1)
        
        # Initialize components
        self.tuya_manager: Optional[TuyaConnectionManager] = None
        self.threat_analyzer: Optional[ThreatAnalyzer] = None
        self.response_orchestrator: Optional[ResponseOrchestrator] = None
        self.websocket_server: Optional[WebSocketServer] = None
        
        # Shutdown flag
        self.shutdown_requested = False
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        logger.info("AI Agent initialized")
    
    def _signal_handler(self, signum, frame):
        """
        Handle shutdown signals for graceful termination.
        
        Args:
            signum: Signal number
            frame: Current stack frame
        """
        logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        self.shutdown_requested = True
    
    def _on_tuya_message(self, msg):
        """
        Callback for incoming Tuya device messages.
        
        Processes device events, adds them to threat analyzer, analyzes
        the sequence, and triggers appropriate responses.
        
        Args:
            msg: Message from Tuya Cloud containing device event data
        """
        try:
            logger.debug(f"Received Tuya message: {msg}")
            
            # Extract device information from message
            # Tuya message format varies, handle common structures
            device_id = None
            event_data = {}
            
            if isinstance(msg, dict):
                # Extract device_id from various possible locations
                device_id = msg.get('devId') or msg.get('device_id') or msg.get('deviceId')
                
                # Extract event data
                if 'status' in msg:
                    event_data = msg['status']
                elif 'data' in msg:
                    event_data = msg['data']
                else:
                    event_data = msg
            
            if not device_id:
                logger.warning(f"Could not extract device_id from message: {msg}")
                return
            
            logger.info(f"Processing event from device: {device_id}")
            
            # Handle all device events - both sensors and actuators
            all_devices = [
                self.config.living_room_motion_id,
                self.config.window_vibration_id,
                self.config.front_door_lock_id,
                self.config.smart_bulb_id,
                self.config.siren_id
            ]
            
            # Broadcast device state change to frontend
            self._broadcast_device_update(device_id, event_data)
            
            # Only process sensor events for threat analysis
            sensor_devices = [
                self.config.living_room_motion_id,
                self.config.window_vibration_id,
                self.config.front_door_lock_id
            ]
            
            if device_id not in sensor_devices:
                logger.info(f"Device state updated (actuator): {device_id}")
                return
            
            # Add event to threat analyzer with current timestamp
            timestamp = datetime.now()
            self.threat_analyzer.add_event(device_id, event_data, timestamp)
            
            # Analyze the event sequence
            status, zone = self.threat_analyzer.analyze_sequence(
                living_room_motion_id=self.config.living_room_motion_id,
                window_vibration_id=self.config.window_vibration_id,
                front_door_lock_id=self.config.front_door_lock_id
            )
            
            logger.info(f"Threat analysis result: {status} in {zone}")
            
            # Execute appropriate response protocol
            if status == "RED_CRITICAL":
                self.response_orchestrator.execute_red_protocol(zone)
            elif status == "YELLOW_WARNING":
                self.response_orchestrator.execute_yellow_protocol(zone)
            elif status == "GREEN_SAFE":
                self.response_orchestrator.execute_green_protocol(zone)
            else:
                logger.warning(f"Unknown status: {status}")
        
        except Exception as e:
            logger.error(f"Error processing Tuya message: {e}", exc_info=True)
    
    def _broadcast_device_update(self, device_id: str, event_data: dict):
        """
        Broadcast device state update to frontend clients.
        
        Args:
            device_id: ID of the device that changed state
            event_data: New state data from the device
        """
        try:
            # Map device IDs to friendly names and locations
            device_mapping = {
                self.config.living_room_motion_id: {'name': 'Motion Sensor', 'location': 'Living Room', 'type': 'motion'},
                self.config.window_vibration_id: {'name': 'Window Sensor', 'location': 'Master Bedroom', 'type': 'window'},
                self.config.front_door_lock_id: {'name': 'Door Lock', 'location': 'Foyer', 'type': 'door-lock'},
                self.config.smart_bulb_id: {'name': 'Smart Bulb', 'location': 'Master Bedroom', 'type': 'bulb'},
                self.config.siren_id: {'name': 'Siren', 'location': 'Foyer', 'type': 'siren'}
            }
            
            device_info = device_mapping.get(device_id)
            if not device_info:
                logger.warning(f"Unknown device ID: {device_id}")
                return
            
            # Create device update message
            update_message = {
                'type': 'device_update',
                'device_id': device_id,
                'device_type': device_info['type'],
                'device_name': device_info['name'],
                'location': device_info['location'],
                'state': event_data,
                'timestamp': datetime.now().isoformat()
            }
            
            # Broadcast to all connected clients
            if self.websocket_server:
                self.websocket_server.get_socketio().emit('device_update', update_message)
                logger.info(f"Broadcasted device update: {device_info['name']} in {device_info['location']}")
        
        except Exception as e:
            logger.error(f"Error broadcasting device update: {e}", exc_info=True)
    
    def initialize_components(self):
        """
        Initialize all system components and wire them together.
        
        Creates instances of:
        - WebSocketServer for frontend communication
        - TuyaConnectionManager for device communication
        - ThreatAnalyzer for event processing
        - ResponseOrchestrator for response coordination
        """
        logger.info("Initializing system components...")
        
        # Initialize WebSocket server first (needed by ResponseOrchestrator)
        self.websocket_server = WebSocketServer(host='0.0.0.0', port=5000)
        logger.info("WebSocket server initialized")
        
        # Initialize Tuya Connection Manager
        device_ids = {
            'LIVING_ROOM_MOTION_ID': self.config.living_room_motion_id,
            'WINDOW_VIBRATION_ID': self.config.window_vibration_id,
            'FRONT_DOOR_LOCK_ID': self.config.front_door_lock_id,
            'SMART_BULB_ID': self.config.smart_bulb_id,
            'SIREN_ID': self.config.siren_id
        }
        
        self.tuya_manager = TuyaConnectionManager(
            client_id=self.config.client_id,
            secret_key=self.config.secret_key,
            device_ids=device_ids
        )
        logger.info("Tuya Connection Manager initialized")
        
        # Initialize Threat Analyzer
        self.threat_analyzer = ThreatAnalyzer()
        logger.info("Threat Analyzer initialized")
        
        # Initialize Response Orchestrator
        self.response_orchestrator = ResponseOrchestrator(
            tuya_manager=self.tuya_manager,
            socketio=self.websocket_server.get_socketio(),
            smart_bulb_id=self.config.smart_bulb_id,
            siren_id=self.config.siren_id,
            front_door_lock_id=self.config.front_door_lock_id
        )
        logger.info("Response Orchestrator initialized")
        
        logger.info("All components initialized successfully")
    
    def connect_to_tuya(self):
        """
        Establish connection to Tuya Cloud and subscribe to devices.
        
        Connects to Tuya Cloud, subscribes to all configured devices,
        and registers the message callback for event processing.
        """
        logger.info("Connecting to Tuya Cloud...")
        
        # Connect to Tuya Cloud (with exponential backoff retry)
        if not self.tuya_manager.connect():
            logger.error("Failed to connect to Tuya Cloud")
            sys.exit(1)
        
        logger.info("Connected to Tuya Cloud successfully")
        
        # Register message callback
        self.tuya_manager.on_message(self._on_tuya_message)
        logger.info("Message callback registered")
        
        # Subscribe to all configured devices
        device_id_list = [
            self.config.living_room_motion_id,
            self.config.window_vibration_id,
            self.config.front_door_lock_id,
            self.config.smart_bulb_id,
            self.config.siren_id
        ]
        
        self.tuya_manager.subscribe_to_devices(device_id_list)
        logger.info(f"Subscribed to {len(device_id_list)} devices")
    
    def run(self):
        """
        Main event loop - start all services and process events.
        
        Starts the WebSocket server in a separate thread and enters
        the main event loop to process Tuya events in real-time.
        """
        logger.info("Starting AI Agent...")
        
        # Initialize all components
        self.initialize_components()
        
        # Connect to Tuya Cloud
        self.connect_to_tuya()
        
        # Start WebSocket server in background thread
        import threading
        websocket_thread = threading.Thread(
            target=self.websocket_server.run,
            kwargs={'debug': False},
            daemon=True
        )
        websocket_thread.start()
        logger.info("WebSocket server started in background thread")
        
        # Main event loop
        logger.info("AI Agent is now running. Press Ctrl+C to stop.")
        logger.info("Polling devices every 2 seconds for status changes...")
        logger.info("=" * 60)
        
        try:
            while not self.shutdown_requested:
                # Poll devices for status changes
                self.tuya_manager.poll_device_changes()
                
                # Sleep for 2 seconds before next poll
                time.sleep(2)
                
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received")
        
        finally:
            self.shutdown()
    
    def shutdown(self):
        """
        Perform graceful shutdown of all components.
        
        Disconnects from Tuya Cloud, stops the WebSocket server,
        and cleans up resources.
        """
        logger.info("Shutting down AI Agent...")
        
        # Disconnect from Tuya Cloud
        if self.tuya_manager:
            try:
                self.tuya_manager.disconnect()
                logger.info("Disconnected from Tuya Cloud")
            except Exception as e:
                logger.error(f"Error disconnecting from Tuya: {e}")
        
        # Note: WebSocket server will be stopped when the main thread exits
        # since it's running in a daemon thread
        
        logger.info("AI Agent shutdown complete")
        logger.info("=" * 60)


def main():
    """
    Main entry point for the AI Agent application.
    
    Creates and runs the AI Agent, handling any startup errors.
    """
    logger.info("=" * 60)
    logger.info("Tuya Security Digital Twin - AI Agent")
    logger.info("=" * 60)
    
    try:
        agent = AIAgent()
        agent.run()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
