"""
AI Threat Analyzer for IoT security event processing.

This module maintains an event sequence buffer and provides methods
for threat analysis based on temporal patterns.
"""

import logging
from datetime import datetime
from typing import List, Optional
from dataclasses import dataclass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class SensorEvent:
    """
    Represents a sensor event with timestamp.
    
    Attributes:
        device_id: Unique identifier for the device
        device_type: Type of device (motion, vibration, lock)
        timestamp: When the event occurred
        data: Raw event data from Tuya
    """
    device_id: str
    device_type: str
    timestamp: datetime
    data: dict
    
    def age_seconds(self) -> float:
        """Calculate age of event in seconds from current time."""
        return (datetime.now() - self.timestamp).total_seconds()


class ThreatAnalyzer:
    """
    Analyzes sensor event sequences to detect security threats.
    
    Maintains a bounded buffer of recent events (max 3) and provides
    methods for threat pattern detection and scoring.
    """
    
    def __init__(self):
        """Initialize ThreatAnalyzer with empty event sequence."""
        self.event_sequence: List[SensorEvent] = []
        self.max_events = 3
        logger.info("ThreatAnalyzer initialized")
    
    def add_event(self, device_id: str, event_data: dict, timestamp: datetime) -> None:
        """
        Append a sensor event to the sequence with timestamp.
        
        Maintains bounded buffer by removing oldest event when exceeding
        maximum of 3 events. Preserves chronological ordering.
        
        Args:
            device_id: Device identifier
            event_data: Raw event data from device
            timestamp: When the event occurred
        """
        # Determine device type from device_id or event_data
        device_type = event_data.get('type', 'unknown')
        
        # Create sensor event
        event = SensorEvent(
            device_id=device_id,
            device_type=device_type,
            timestamp=timestamp,
            data=event_data
        )
        
        # Append event to sequence
        self.event_sequence.append(event)
        
        # Maintain bounded buffer - remove oldest if exceeding max
        if len(self.event_sequence) > self.max_events:
            removed_event = self.event_sequence.pop(0)
            logger.debug(f"Removed oldest event from buffer: {removed_event.device_id}")
        
        # Ensure chronological ordering is maintained
        # Events should be added in order, but we verify
        self.event_sequence.sort(key=lambda e: e.timestamp)
        
        logger.info(f"Added event from device {device_id}. Buffer size: {len(self.event_sequence)}")
    
    def clear_warnings(self) -> None:
        """
        Reset the threat analyzer state.
        
        Clears all events from the sequence buffer.
        """
        self.event_sequence.clear()
        logger.info("Cleared all warnings and reset event sequence")
    
    def get_event_count(self) -> int:
        """
        Get the current number of events in the buffer.
        
        Returns:
            Number of events currently stored
        """
        return len(self.event_sequence)
    
    def get_events(self) -> List[SensorEvent]:
        """
        Get a copy of the current event sequence.
        
        Returns:
            List of sensor events in chronological order
        """
        return self.event_sequence.copy()

    
    def get_time_weight(self, current_time: datetime) -> float:
        """
        Calculate time-contextual weight multiplier based on time of day.
        
        Nighttime hours (22:00-06:00) are weighted higher (1.5x) as activity
        during these hours is more suspicious. Daytime hours (06:00-22:00)
        are weighted lower (0.7x) as activity is more expected.
        
        Args:
            current_time: The datetime to evaluate
            
        Returns:
            float: Multiplier for threat score (1.5 for night, 0.7 for day)
        """
        hour = current_time.hour
        
        # Nighttime: 22:00 (10 PM) to 06:00 (6 AM)
        if hour >= 22 or hour < 6:
            weight = 1.5
            logger.debug(f"Nighttime weight applied: {weight}x at {hour:02d}:00")
        # Daytime: 06:00 (6 AM) to 22:00 (10 PM)
        else:
            weight = 0.7
            logger.debug(f"Daytime weight applied: {weight}x at {hour:02d}:00")
        
        return weight
    
    def calculate_threat_score(self, base_score: float, current_time: datetime) -> float:
        """
        Calculate final threat score by combining base score with time weight.
        
        The base score (0-100) represents the severity of the event pattern.
        This is multiplied by the time-contextual weight to produce the final score.
        
        Args:
            base_score: Base threat score (0-100)
            current_time: The datetime to evaluate for time weighting
            
        Returns:
            float: Final weighted threat score
        """
        time_weight = self.get_time_weight(current_time)
        final_score = base_score * time_weight
        
        logger.info(f"Calculated threat score: base={base_score}, weight={time_weight}, final={final_score}")
        
        return final_score
    
    def classify_threat(self, final_score: float) -> str:
        """
        Classify threat level based on final weighted score.
        
        Classification thresholds:
        - score >= 80: RED_CRITICAL (immediate threat)
        - 40 <= score < 80: YELLOW_WARNING (potential concern)
        - score < 40: GREEN_SAFE (normal activity)
        
        Args:
            final_score: The weighted threat score
            
        Returns:
            str: Status code (RED_CRITICAL, YELLOW_WARNING, or GREEN_SAFE)
        """
        if final_score >= 80:
            status = "RED_CRITICAL"
        elif final_score >= 40:
            status = "YELLOW_WARNING"
        else:
            status = "GREEN_SAFE"
        
        logger.info(f"Threat classified as {status} (score: {final_score})")
        
        return status
    
    def analyze_sequence(self, living_room_motion_id: str, window_vibration_id: str, 
                        front_door_lock_id: str) -> tuple[str, str]:
        """
        Analyze the event sequence to detect threat patterns.
        
        Detects the following patterns:
        1. Motion + Vibration: WINDOW_VIBRATION_ID within 10 seconds after LIVING_ROOM_MOTION_ID
           - Base score: 90 (potential break-in)
           - Zone: HOUSE
        2. Motion alone: LIVING_ROOM_MOTION_ID with no vibration follow-up within 10 seconds
           - Base score: 50 (potential concern)
           - Zone: LivingRoom
        3. Door unlock: FRONT_DOOR_LOCK_ID unlock event
           - Base score: 0 (safe arrival)
           - Zone: HOUSE
        
        Args:
            living_room_motion_id: Device ID for living room motion sensor
            window_vibration_id: Device ID for window vibration sensor
            front_door_lock_id: Device ID for front door lock
            
        Returns:
            tuple[str, str]: (status, zone) where status is RED_CRITICAL, YELLOW_WARNING, 
                           or GREEN_SAFE, and zone is HOUSE, LivingRoom, Foyer, or MasterBedroom
        """
        if not self.event_sequence:
            logger.debug("Empty event sequence, returning GREEN_SAFE")
            return ("GREEN_SAFE", "HOUSE")
        
        # Get the most recent event and use its timestamp for time weighting
        latest_event = self.event_sequence[-1]
        current_time = latest_event.timestamp
        
        # Check for door unlock event (GREEN_SAFE)
        if latest_event.device_id == front_door_lock_id:
            # Check if this is an unlock event
            unlock_detected = False
            if 'status' in latest_event.data and latest_event.data['status'] == 'unlocked':
                unlock_detected = True
            elif 'value' in latest_event.data and latest_event.data['value'] in [False, 'unlocked', 'unlock']:
                unlock_detected = True
            
            if unlock_detected:
                base_score = 0
                final_score = self.calculate_threat_score(base_score, current_time)
                status = self.classify_threat(final_score)
                logger.info(f"Door unlock detected: {status}")
                return (status, "HOUSE")
        
        # Check for motion + vibration pattern (RED_CRITICAL or YELLOW_WARNING)
        motion_event = None
        vibration_event = None
        
        # Find most recent motion and vibration events
        for event in reversed(self.event_sequence):
            if event.device_id == living_room_motion_id and motion_event is None:
                motion_event = event
            elif event.device_id == window_vibration_id and vibration_event is None:
                vibration_event = event
        
        # If we have both motion and vibration events
        if motion_event and vibration_event:
            # Check if vibration occurred within 10 seconds after motion
            time_diff = (vibration_event.timestamp - motion_event.timestamp).total_seconds()
            
            if 0 <= time_diff <= 10:
                # Motion + Vibration pattern detected
                base_score = 90
                final_score = self.calculate_threat_score(base_score, current_time)
                status = self.classify_threat(final_score)
                logger.info(f"Motion + Vibration pattern detected (time_diff={time_diff:.2f}s): {status}")
                return (status, "HOUSE")
        
        # If we have motion but no vibration follow-up within 10 seconds
        if motion_event:
            # Check if enough time has passed to determine no vibration follow-up
            time_since_motion = (current_time - motion_event.timestamp).total_seconds()
            
            # If more than 10 seconds have passed since motion, or if we have a vibration
            # event but it's not within the 10-second window
            if time_since_motion > 10 or (vibration_event and 
                (vibration_event.timestamp - motion_event.timestamp).total_seconds() > 10):
                # Motion alone pattern
                base_score = 50
                final_score = self.calculate_threat_score(base_score, current_time)
                status = self.classify_threat(final_score)
                logger.info(f"Motion alone detected (time_since={time_since_motion:.2f}s): {status}")
                return (status, "LivingRoom")
        
        # Default to GREEN_SAFE if no patterns detected
        base_score = 0
        final_score = self.calculate_threat_score(base_score, current_time)
        status = self.classify_threat(final_score)
        logger.debug(f"No threat pattern detected: {status}")
        return (status, "HOUSE")
