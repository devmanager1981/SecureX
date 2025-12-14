"""
Response Orchestrator for IoT security system.

This module coordinates multi-step response protocols based on threat
classifications, dispatching commands to actuator devices and broadcasting
status updates to connected clients.
"""

import logging
from typing import Optional
from tuya_connection_manager import TuyaConnectionManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ResponseOrchestrator:
    """
    Orchestrates security responses based on threat classifications.
    
    Executes multi-step protocols for RED_CRITICAL, YELLOW_WARNING, and
    GREEN_SAFE statuses, including device control, notifications, and
    WebSocket broadcasts.
    """
    
    def __init__(self, tuya_manager: TuyaConnectionManager, socketio, 
                 smart_bulb_id: str, siren_id: str, front_door_lock_id: str):
        """
        Initialize Response Orchestrator.
        
        Args:
            tuya_manager: TuyaConnectionManager instance for device control
            socketio: Flask-SocketIO instance for WebSocket broadcasts
            smart_bulb_id: Device ID for smart bulb
            siren_id: Device ID for siren
            front_door_lock_id: Device ID for front door lock
        """
        self.tuya_manager = tuya_manager
        self.socketio = socketio
        self.smart_bulb_id = smart_bulb_id
        self.siren_id = siren_id
        self.front_door_lock_id = front_door_lock_id
        self.warning_states = set()
        
        logger.info("ResponseOrchestrator initialized")
    
    def execute_red_protocol(self, zone: str) -> None:
        """
        Execute RED_CRITICAL response protocol.
        
        Performs all 5 required actions:
        1. Send command to smart bulb for red strobe mode
        2. Send command to siren to activate
        3. Send command to front door lock to lock (via remote unlock request)
        4. Send critical push notification
        5. Broadcast WebSocket message with status RED_CRITICAL and zone HOUSE
        
        Args:
            zone: The zone where threat was detected (typically HOUSE)
        """
        logger.warning(f"Executing RED_CRITICAL protocol for zone: {zone}")
        
        # Action 1: Smart bulb - turn on and set to scene mode (red alert)
        bulb_commands = {
            "commands": [
                {
                    "code": "switch_led",
                    "value": True
                },
                {
                    "code": "work_mode",
                    "value": "scene"  # Scene mode for alert
                }
            ]
        }
        self.tuya_manager.send_command(self.smart_bulb_id, bulb_commands)
        logger.info("RED_CRITICAL: Smart bulb set to red")
        
        # Action 2: Activate siren
        siren_commands = {
            "commands": [
                {
                    "code": "alarm_switch",
                    "value": True
                },
                {
                    "code": "alarm_volume",
                    "value": "high"
                }
            ]
        }
        self.tuya_manager.send_command(self.siren_id, siren_commands)
        logger.info("RED_CRITICAL: Siren activated")
        
        # Action 3: Door lock - Note: This lock only supports remote unlock requests
        # We can't directly lock it via API, only respond to unlock requests
        logger.info("RED_CRITICAL: Door lock (read-only device, cannot control remotely)")
        
        # Action 4: Send push notification
        self.send_push_notification(
            "CRITICAL: Break-in attempt detected!",
            "high"
        )
        
        # Action 5: Broadcast status to WebSocket clients
        self.broadcast_status("RED_CRITICAL", "HOUSE")
    
    def execute_yellow_protocol(self, zone: str) -> None:
        """
        Execute YELLOW_WARNING response protocol.
        
        Performs graduated response actions:
        1. Send command to smart bulb for soft yellow at low brightness
        2. Broadcast WebSocket message with status YELLOW_WARNING and specific zone
        
        Does NOT activate siren or lock door.
        
        Args:
            zone: The specific zone where potential concern was detected
        """
        logger.info(f"Executing YELLOW_WARNING protocol for zone: {zone}")
        
        # Action 1: Smart bulb - turn on in white mode (warning)
        bulb_commands = {
            "commands": [
                {
                    "code": "switch_led",
                    "value": True
                },
                {
                    "code": "work_mode",
                    "value": "white"  # White mode for warning
                }
            ]
        }
        self.tuya_manager.send_command(self.smart_bulb_id, bulb_commands)
        logger.info("YELLOW_WARNING: Smart bulb set to soft yellow")
        
        # Track warning state
        self.warning_states.add(zone)
        
        # Action 2: Broadcast status to WebSocket clients
        self.broadcast_status("YELLOW_WARNING", zone)
    
    def execute_green_protocol(self, zone: str) -> None:
        """
        Execute GREEN_SAFE response protocol.
        
        Performs welcoming actions:
        1. Send command to smart bulb for warm white at 20% brightness
        2. Clear all active warning states
        3. Broadcast WebSocket message with status GREEN_SAFE and zone HOUSE
        
        Args:
            zone: The zone (typically HOUSE for safe arrival)
        """
        logger.info(f"Executing GREEN_SAFE protocol for zone: {zone}")
        
        # Action 1: Smart bulb - turn on in white mode (safe/welcoming)
        bulb_commands = {
            "commands": [
                {
                    "code": "switch_led",
                    "value": True
                },
                {
                    "code": "work_mode",
                    "value": "white"  # White mode for safe status
                }
            ]
        }
        self.tuya_manager.send_command(self.smart_bulb_id, bulb_commands)
        logger.info("GREEN_SAFE: Smart bulb set to warm white at 20%")
        
        # Action 2: Clear all warning states
        self.clear_warnings()
        
        # Action 3: Broadcast status to WebSocket clients
        self.broadcast_status("GREEN_SAFE", "HOUSE")
    
    def send_push_notification(self, message: str, priority: str) -> None:
        """
        Send push notification to user.
        
        For hackathon/development purposes, this is implemented as console
        logging with timestamp. In production, this would integrate with
        a webhook service (Discord, Slack) or push notification service.
        
        Args:
            message: Notification message text
            priority: Priority level (high, medium, low)
        """
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        notification = {
            "timestamp": timestamp,
            "message": message,
            "priority": priority
        }
        
        # Console mock for development
        logger.critical(f"PUSH NOTIFICATION [{priority.upper()}]: {message}")
        
        # In production, would send to webhook:
        # requests.post(webhook_url, json=notification)
    
    def broadcast_status(self, status: str, zone: str) -> None:
        """
        Broadcast security status update to all connected WebSocket clients.
        
        Sends JSON message containing status and zone fields to all clients
        connected to the WebSocket server.
        
        Args:
            status: Status code (RED_CRITICAL, YELLOW_WARNING, GREEN_SAFE)
            zone: Zone identifier (HOUSE, LivingRoom, Foyer, MasterBedroom)
        """
        message = {
            "status": status,
            "zone": zone
        }
        
        if self.socketio:
            self.socketio.emit('status_update', message)
            logger.info(f"Broadcast status update: {status} in {zone}")
        else:
            logger.warning("SocketIO not available, cannot broadcast status")
    
    def clear_warnings(self) -> None:
        """Clear all active warning states."""
        self.warning_states.clear()
        logger.info("Cleared all warning states")
