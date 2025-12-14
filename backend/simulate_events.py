"""
Simulate device events for testing the AI Agent.

Since virtual sensors are read-only, this script manually triggers
the AI agent's event processing logic with simulated events.
"""

from datetime import datetime
from threat_analyzer import ThreatAnalyzer
from response_orchestrator import ResponseOrchestrator
from tuya_connection_manager import TuyaConnectionManager
from websocket_server import WebSocketServer
from config import load_config
import time

def simulate_motion_detection():
    """Simulate motion sensor detection."""
    print("\n🚶 Simulating MOTION DETECTION...")
    
    config = load_config()
    analyzer = ThreatAnalyzer()
    
    # Simulate motion event
    motion_event = {
        'type': 'motion',
        'code': 'pir_state',
        'value': 'pir',
        'timestamp': datetime.now().isoformat()
    }
    
    analyzer.add_event(config.living_room_motion_id, motion_event, datetime.now())
    
    # Wait 11 seconds (past the 10-second window for motion+vibration)
    print("Waiting 11 seconds to analyze...")
    time.sleep(11)
    
    # Analyze
    status, zone = analyzer.analyze_sequence(
        config.living_room_motion_id,
        config.window_vibration_id,
        config.front_door_lock_id
    )
    
    print(f"✓ Analysis Result: {status} in {zone}")
    return status, zone


def simulate_motion_plus_vibration():
    """Simulate motion + vibration (break-in attempt)."""
    print("\n🚨 Simulating BREAK-IN ATTEMPT (Motion + Vibration)...")
    
    config = load_config()
    analyzer = ThreatAnalyzer()
    
    # Simulate motion event
    print("1. Motion detected...")
    motion_event = {
        'type': 'motion',
        'code': 'pir_state',
        'value': 'pir',
        'timestamp': datetime.now().isoformat()
    }
    analyzer.add_event(config.living_room_motion_id, motion_event, datetime.now())
    
    # Wait 5 seconds (within the 10-second window)
    print("2. Waiting 5 seconds...")
    time.sleep(5)
    
    # Simulate vibration event
    print("3. Window vibration detected...")
    vibration_event = {
        'type': 'vibration',
        'code': 'shock_state',
        'value': 'vibration',
        'timestamp': datetime.now().isoformat()
    }
    analyzer.add_event(config.window_vibration_id, vibration_event, datetime.now())
    
    # Analyze
    status, zone = analyzer.analyze_sequence(
        config.living_room_motion_id,
        config.window_vibration_id,
        config.front_door_lock_id
    )
    
    print(f"✓ Analysis Result: {status} in {zone}")
    return status, zone


def simulate_door_unlock():
    """Simulate door unlock (safe arrival)."""
    print("\n🚪 Simulating DOOR UNLOCK (Safe Arrival)...")
    
    config = load_config()
    analyzer = ThreatAnalyzer()
    
    # Simulate door unlock event
    unlock_event = {
        'type': 'lock',
        'code': 'unlock_app',
        'status': 'unlocked',
        'value': 1,
        'timestamp': datetime.now().isoformat()
    }
    
    analyzer.add_event(config.front_door_lock_id, unlock_event, datetime.now())
    
    # Analyze
    status, zone = analyzer.analyze_sequence(
        config.living_room_motion_id,
        config.window_vibration_id,
        config.front_door_lock_id
    )
    
    print(f"✓ Analysis Result: {status} in {zone}")
    return status, zone


def simulate_with_response():
    """Simulate events and trigger actual device responses."""
    print("\n" + "="*60)
    print("FULL SIMULATION WITH DEVICE CONTROL")
    print("="*60)
    print("\nThis will simulate events AND control actual devices!")
    print("="*60)
    
    config = load_config()
    
    # Initialize components
    print("\nInitializing components...")
    tuya_manager = TuyaConnectionManager(
        client_id=config.client_id,
        secret_key=config.secret_key,
        device_ids={}
    )
    
    if not tuya_manager.connect():
        print("✗ Failed to connect to Tuya")
        return
    
    print("✓ Connected to Tuya Cloud")
    
    # Initialize WebSocket server (optional, for frontend)
    socketio = None  # Set to None if no WebSocket needed
    
    # Initialize response orchestrator
    orchestrator = ResponseOrchestrator(
        tuya_manager=tuya_manager,
        socketio=socketio,
        smart_bulb_id=config.smart_bulb_id,
        siren_id=config.siren_id,
        front_door_lock_id=config.front_door_lock_id
    )
    
    # Test scenarios
    print("\n" + "="*60)
    print("SCENARIO 1: Motion Only (YELLOW WARNING)")
    print("="*60)
    
    status, zone = simulate_motion_detection()
    
    if status == "YELLOW_WARNING":
        print("\n🟡 Executing YELLOW WARNING protocol...")
        orchestrator.execute_yellow_protocol(zone)
        print("✓ Yellow protocol executed (bulb should be in white mode)")
    
    time.sleep(3)
    
    print("\n" + "="*60)
    print("SCENARIO 2: Motion + Vibration (RED CRITICAL)")
    print("="*60)
    
    status, zone = simulate_motion_plus_vibration()
    
    if status == "RED_CRITICAL":
        print("\n🔴 Executing RED CRITICAL protocol...")
        orchestrator.execute_red_protocol(zone)
        print("✓ Red protocol executed (bulb in scene mode, siren activated)")
    
    time.sleep(3)
    
    print("\n" + "="*60)
    print("SCENARIO 3: Door Unlock (GREEN SAFE)")
    print("="*60)
    
    status, zone = simulate_door_unlock()
    
    if status == "GREEN_SAFE":
        print("\n🟢 Executing GREEN SAFE protocol...")
        orchestrator.execute_green_protocol(zone)
        print("✓ Green protocol executed (bulb in white mode)")
    
    tuya_manager.disconnect()
    print("\n✓ Simulation complete!")


def main():
    print("\n" + "="*60)
    print("EVENT SIMULATION FOR AI AGENT TESTING")
    print("="*60)
    print("\nSelect simulation:")
    print("1. Motion only (YELLOW WARNING)")
    print("2. Motion + Vibration (RED CRITICAL)")
    print("3. Door unlock (GREEN SAFE)")
    print("4. Full simulation with device control")
    print("0. Exit")
    
    choice = input("\nSelect (0-4): ")
    
    try:
        if choice == "1":
            simulate_motion_detection()
        elif choice == "2":
            simulate_motion_plus_vibration()
        elif choice == "3":
            simulate_door_unlock()
        elif choice == "4":
            simulate_with_response()
        elif choice == "0":
            print("Exiting...")
        else:
            print("Invalid choice")
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
