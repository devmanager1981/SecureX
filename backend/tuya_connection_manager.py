"""
Tuya Connection Manager for IoT device communication.

This module handles connection to Tuya Cloud, device subscription,
and command transmission with retry logic.
"""

import logging
import time
import os
from typing import Callable, Dict, List, Optional
from tuya_connector import TuyaOpenAPI, TuyaOpenPulsar, TuyaCloudPulsarTopic, TUYA_LOGGER
from dotenv import load_dotenv
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Set Tuya SDK logger to WARNING to reduce noise
TUYA_LOGGER.setLevel(logging.WARNING)


class TuyaConnectionManager:
    """
    Manages connection to Tuya Cloud and device communication.
    
    Handles WebSocket subscriptions for real-time events and REST API
    commands for device control with exponential backoff reconnection.
    """
    
    def __init__(self, client_id: str, secret_key: str, device_ids: Dict[str, str]):
        """
        Initialize Tuya Connection Manager.
        
        Args:
            client_id: Tuya API client ID
            secret_key: Tuya API secret key
            device_ids: Dictionary mapping device names to device IDs
        """
        self.client_id = os.getenv("CLIENT_ID")
        self.secret_key = os.getenv("SECRET_KEY")
        self.device_ids = device_ids
        self.api: Optional[TuyaOpenAPI] = None
        self.mq: Optional[TuyaOpenPulsar] = None
        self.message_callback: Optional[Callable] = None
        self.connected = False
        
        # Exponential backoff parameters
        self.max_retry_delay = 16  # Maximum delay in seconds
        self.base_retry_delay = 1  # Initial delay in seconds
        self.max_connection_attempts = 5  # Maximum connection attempts before giving up
        
        logger.info("TuyaConnectionManager initialized")
    
    def connect(self) -> bool:
        """
        Establish connection to Tuya Cloud with exponential backoff retry.
        
        Returns:
            bool: True if connection successful, False if max attempts reached
        """
        retry_delay = self.base_retry_delay
        attempt = 0
        
        while attempt < self.max_connection_attempts:
            try:
                attempt += 1
                logger.info(f"Attempting to connect to Tuya Cloud (attempt {attempt}/{self.max_connection_attempts})...")
                
                # Initialize Tuya OpenAPI
                # Using India datacenter endpoint - adjust based on your region
                # Options: 
                # US: https://openapi.tuyaus.com
                # EU: https://openapi.tuyaeu.com
                # CN: https://openapi.tuyacn.com
                # IN: https://openapi.tuyain.com
                self.api = TuyaOpenAPI(
                    endpoint="https://openapi.tuyain.com",
                    access_id=self.client_id,
                    access_secret=self.secret_key
                )
                
                # Authenticate
                response = self.api.connect()
                
                if not response.get('success', False):
                    raise ConnectionError(f"Tuya API authentication failed: {response}")
                
                logger.info("Successfully connected to Tuya Cloud")
                self.connected = True
                return True
                
            except Exception as e:
                logger.error(f"Connection attempt {attempt} failed: {e}")
                
                if attempt < self.max_connection_attempts:
                    logger.info(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    # Exponential backoff with max cap
                    retry_delay = min(retry_delay * 2, self.max_retry_delay)
        
        logger.error(f"Failed to connect after {self.max_connection_attempts} attempts")
        return False
    
    def subscribe_to_devices(self, device_ids: List[str]) -> None:
        """
        Subscribe to device status changes using polling.
        
        For SaaS projects, Pulsar WebSocket often fails. We use polling instead
        to check device status periodically and detect changes.
        
        Args:
            device_ids: List of device IDs to subscribe to
            
        Raises:
            RuntimeError: If not connected to Tuya Cloud
        """
        if not self.connected or not self.api:
            raise RuntimeError("Must connect to Tuya Cloud before subscribing to devices")
        
        try:
            logger.info(f"Subscribing to {len(device_ids)} devices using polling...")
            
            # Store device IDs for polling
            self.subscribed_devices = device_ids
            
            # Initialize last known state for each device
            self.device_states = {}
            for device_id in device_ids:
                try:
                    response = self.api.get(f'/v1.0/iot-03/devices/{device_id}/status')
                    if response.get('success'):
                        self.device_states[device_id] = response.get('result', [])
                except Exception as e:
                    logger.warning(f"Could not get initial state for {device_id}: {e}")
                    self.device_states[device_id] = []
            
            logger.info(f"Successfully subscribed to {len(device_ids)} devices via polling")
            logger.info("Note: Using polling mode (checking every 2 seconds)")
            
        except Exception as e:
            logger.error(f"Failed to subscribe to devices: {e}")
            raise
    
    def poll_device_changes(self) -> None:
        """
        Poll devices for status changes and trigger callbacks.
        
        This method should be called periodically (e.g., every 2 seconds)
        to check for device status changes.
        """
        if not self.connected or not self.api:
            return
        
        if not hasattr(self, 'subscribed_devices'):
            return
        
        for device_id in self.subscribed_devices:
            try:
                # Get current device status
                response = self.api.get(f'/v1.0/iot-03/devices/{device_id}/status')
                
                if not response.get('success'):
                    continue
                
                current_state = response.get('result', [])
                last_state = self.device_states.get(device_id, [])
                
                # Check if state has changed
                if current_state != last_state:
                    logger.info(f"Device {device_id} state changed")
                    
                    # Update stored state
                    self.device_states[device_id] = current_state
                    
                    # Trigger callback if set
                    if self.message_callback:
                        # Format message similar to Pulsar format
                        message = {
                            'devId': device_id,
                            'device_id': device_id,
                            'status': {item['code']: item['value'] for item in current_state},
                            'data': current_state,
                            'timestamp': time.time()
                        }
                        self.message_callback(message)
                
            except Exception as e:
                logger.debug(f"Error polling device {device_id}: {e}")
    
    def send_command(self, device_id: str, commands: Dict) -> bool:
        """
        Send control command to a device with retry logic.
        
        Uses v1.0 API for device control (recommended by Tuya support).
        
        Args:
            device_id: Target device ID
            commands: Command dictionary in Tuya format
                     {"commands": [{"code": "switch_led", "value": true}]}
            
        Returns:
            bool: True if command sent successfully, False otherwise
        """
        if not self.connected or not self.api:
            logger.error("Cannot send command: Not connected to Tuya Cloud")
            return False
        
        max_retries = 3
        retry_delay = 2  # seconds
        
        for attempt in range(1, max_retries + 1):
            try:
                logger.info(f"Sending command to device {device_id} (attempt {attempt}/{max_retries})")
                logger.debug(f"Command: {commands}")
                
                # Use v1.0 API for device control (as per Tuya support documentation)
                # Endpoint: POST /v1.0/iot-03/devices/{device_id}/commands
                response = self.api.post(
                    f'/v1.0/iot-03/devices/{device_id}/commands',
                    commands
                )
                
                if response.get('success', False):
                    logger.info(f"Command sent successfully to device {device_id}")
                    return True
                else:
                    error_msg = response.get('msg', 'Unknown error')
                    logger.error(f"Command failed: {error_msg}")
                    
                    if attempt < max_retries:
                        logger.info(f"Retrying in {retry_delay} seconds...")
                        time.sleep(retry_delay)
                    
            except Exception as e:
                logger.error(f"Exception sending command to device {device_id}: {e}")
                
                if attempt < max_retries:
                    logger.info(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
        
        logger.error(f"Failed to send command to device {device_id} after {max_retries} attempts")
        return False
    
    def on_message(self, callback: Callable) -> None:
        """
        Register callback for incoming device messages.
        
        Args:
            callback: Function to call when message received
        """
        self.message_callback = callback
        
        # If already subscribed, add listener to existing message queue
        if self.mq:
            self.mq.add_message_listener(callback)
        
        logger.info("Message callback registered")
    
    def reconnect(self) -> bool:
        """
        Attempt to reconnect to Tuya Cloud.
        
        Returns:
            bool: True if reconnection successful
        """
        logger.info("Attempting to reconnect...")
        self.connected = False
        
        # Close existing connections
        if self.mq:
            try:
                self.mq.stop()
            except Exception as e:
                logger.warning(f"Error stopping message queue: {e}")
        
        # Reconnect
        return self.connect()
    
    def disconnect(self) -> None:
        """Disconnect from Tuya Cloud and clean up resources."""
        logger.info("Disconnecting from Tuya Cloud...")
        
        if self.mq:
            try:
                self.mq.stop()
            except Exception as e:
                logger.warning(f"Error stopping message queue: {e}")
        
        self.connected = False
        logger.info("Disconnected from Tuya Cloud")
