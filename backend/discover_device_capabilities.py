"""
Discover device capabilities and supported commands.

This script queries the Tuya API to find out what commands
each device actually supports.
"""

from config import load_config
from tuya_connection_manager import TuyaConnectionManager
import json

def discover_device(device_id, device_name):
    """Discover capabilities for a specific device."""
    print("\n" + "="*60)
    print(f"DEVICE: {device_name}")
    print(f"ID: {device_id}")
    print("="*60)
    
    config = load_config()
    manager = TuyaConnectionManager(
        client_id=config.client_id,
        secret_key=config.secret_key,
        device_ids={}
    )
    
    if not manager.connect():
        print("✗ Failed to connect")
        return
    
    # Get device data model (shows supported properties/actions)
    print("\n1. Querying device data model...")
    try:
        response = manager.api.get(f'/v2.0/cloud/thing/{device_id}/model')
        if response.get('success'):
            model = response.get('result', {})
            print("✓ Data model retrieved")
            print(json.dumps(model, indent=2))
        else:
            print(f"✗ Failed: {response.get('msg', 'Unknown error')}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Get current device properties
    print("\n2. Querying current device properties...")
    try:
        response = manager.api.get(f'/v2.0/cloud/thing/{device_id}/shadow/properties')
        if response.get('success'):
            properties = response.get('result', {})
            print("✓ Current properties:")
            print(json.dumps(properties, indent=2))
        else:
            print(f"✗ Failed: {response.get('msg', 'Unknown error')}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Try to get device info (v1.0 API for comparison)
    print("\n3. Querying device info (v1.0 API)...")
    try:
        response = manager.api.get(f'/v1.0/devices/{device_id}')
        if response.get('success'):
            info = response.get('result', {})
            print("✓ Device info:")
            print(f"  Name: {info.get('name', 'N/A')}")
            print(f"  Online: {info.get('online', 'N/A')}")
            print(f"  Product ID: {info.get('product_id', 'N/A')}")
            
            if 'status' in info:
                print("  Current Status:")
                for status in info['status']:
                    print(f"    - {status.get('code')}: {status.get('value')}")
            
            if 'functions' in info:
                print("  Supported Functions:")
                for func in info['functions']:
                    print(f"    - {func.get('code')}: {func.get('type')} = {func.get('values', 'N/A')}")
        else:
            print(f"✗ Failed: {response.get('msg', 'Unknown error')}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    manager.disconnect()


def main():
    print("\n" + "="*60)
    print("TUYA DEVICE CAPABILITY DISCOVERY")
    print("="*60)
    print("\nThis script will query your devices to discover")
    print("what commands and properties they support.")
    print("="*60)
    
    config = load_config()
    
    devices = [
        (config.smart_bulb_id, "Smart Bulb"),
        (config.siren_id, "Siren"),
        (config.front_door_lock_id, "Door Lock"),
        (config.living_room_motion_id, "Motion Sensor"),
        (config.window_vibration_id, "Vibration Sensor"),
    ]
    
    print("\nSelect device to discover:")
    for i, (device_id, name) in enumerate(devices, 1):
        print(f"{i}. {name} ({device_id})")
    print("0. Discover all devices")
    
    choice = input("\nSelect (0-5): ")
    
    try:
        if choice == "0":
            for device_id, name in devices:
                discover_device(device_id, name)
                print("\n" + "-"*60)
        elif choice in ["1", "2", "3", "4", "5"]:
            idx = int(choice) - 1
            discover_device(devices[idx][0], devices[idx][1])
        else:
            print("Invalid choice")
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
