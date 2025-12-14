"""
Check Tuya API permissions and connection details.

This script helps diagnose permission issues with Tuya Cloud/SaaS projects.
"""

from config import load_config
from tuya_connection_manager import TuyaConnectionManager

def check_connection():
    """Check if we can connect to Tuya Cloud."""
    print("\n" + "="*60)
    print("TUYA CONNECTION CHECK")
    print("="*60)
    
    config = load_config()
    
    print(f"\nClient ID: {config.client_id[:10]}...")
    print(f"Secret Key: {config.secret_key[:10]}...")
    print(f"Endpoint: https://openapi.tuyain.com (India)")
    
    manager = TuyaConnectionManager(
        client_id=config.client_id,
        secret_key=config.secret_key,
        device_ids={}
    )
    
    print("\nAttempting to connect...")
    if manager.connect():
        print("✓ Connection successful!")
        
        # Try to get device list
        print("\nAttempting to fetch device list...")
        try:
            response = manager.api.get("/v1.0/iot-03/devices")
            
            if response.get('success'):
                devices = response.get('result', {}).get('list', [])
                print(f"✓ Found {len(devices)} devices")
                
                if devices:
                    print("\nDevices found:")
                    for device in devices:
                        print(f"  - {device.get('name', 'Unknown')}: {device.get('id', 'N/A')}")
                else:
                    print("\n⚠ No devices found in this project")
                    print("This might mean:")
                    print("  1. Devices are not linked to this Cloud/SaaS project")
                    print("  2. You're using a SaaS project and need to link via Asset")
                    print("  3. Devices are in a different project")
            else:
                print(f"✗ Failed to get device list: {response.get('msg', 'Unknown error')}")
                
        except Exception as e:
            print(f"✗ Error fetching devices: {e}")
        
        # Try to get user info
        print("\nAttempting to fetch user info...")
        try:
            response = manager.api.get("/v1.0/users")
            if response.get('success'):
                print("✓ User info retrieved successfully")
            else:
                print(f"⚠ User info: {response.get('msg', 'Unknown')}")
        except Exception as e:
            print(f"⚠ Could not fetch user info: {e}")
        
        manager.disconnect()
        
    else:
        print("✗ Connection failed!")
        return
    
    print("\n" + "="*60)
    print("DEVICE ID CHECK")
    print("="*60)
    
    print("\nDevice IDs in your .env file:")
    print(f"  Motion Sensor: {config.living_room_motion_id}")
    print(f"  Vibration Sensor: {config.window_vibration_id}")
    print(f"  Door Lock: {config.front_door_lock_id}")
    print(f"  Smart Bulb: {config.smart_bulb_id}")
    print(f"  Siren: {config.siren_id}")
    
    print("\n" + "="*60)
    print("RECOMMENDATIONS")
    print("="*60)
    
    print("\nIf you're using a SaaS project:")
    print("  1. Go to IoT Platform → Your Project → Authorization tab")
    print("  2. Enable 'Device Control' and 'Device Management' permissions")
    print("  3. Go to 'Asset' or 'User' management")
    print("  4. Link your devices to the Asset/User")
    print("  5. Make sure Tuya Spatial app is linked to the same account")
    
    print("\nIf devices are not found:")
    print("  1. Verify device IDs are correct")
    print("  2. Check that devices are linked to THIS project")
    print("  3. Try linking Tuya Spatial app account to the project")
    print("  4. Check 'Project SaaS' → 'App' tab for app configuration")


if __name__ == "__main__":
    try:
        check_connection()
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
