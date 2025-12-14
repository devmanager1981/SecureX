"""
Example Configuration File for Tuya Security Digital Twin System

IMPORTANT: This is an example configuration file. DO NOT use these values directly.
Copy this file to set your environment variables or create your own config.py.

To use this configuration:
1. Obtain your Tuya API credentials (see instructions below)
2. Find your device IDs from the Tuya IoT Platform (see instructions below)
3. Set these values as environment variables before running the application

Example usage:
    # On Linux/Mac:
    export CLIENT_ID="your_actual_client_id"
    export SECRET_KEY="your_actual_secret_key"
    # ... set other variables
    python backend/ai_agent.py

    # On Windows (Command Prompt):
    set CLIENT_ID=your_actual_client_id
    set SECRET_KEY=your_actual_secret_key
    # ... set other variables
    python backend/ai_agent.py

    # On Windows (PowerShell):
    $env:CLIENT_ID="your_actual_client_id"
    $env:SECRET_KEY="your_actual_secret_key"
    # ... set other variables
    python backend/ai_agent.py
"""

# ============================================================================
# TUYA API CREDENTIALS
# ============================================================================
# These credentials authenticate your application with Tuya Cloud.
# You MUST obtain these from the Tuya IoT Platform.

# Your Tuya Cloud Project Client ID
CLIENT_ID = "your_tuya_client_id_here"

# Your Tuya Cloud Project Secret Key
SECRET_KEY = "your_tuya_secret_key_here"


# ============================================================================
# HOW TO OBTAIN TUYA API CREDENTIALS
# ============================================================================
"""
Step 1: Create a Tuya Developer Account
    1. Go to https://iot.tuya.com/
    2. Click "Sign Up" and create an account
    3. Verify your email address

Step 2: Create a Cloud Project
    1. Log in to the Tuya IoT Platform
    2. Navigate to "Cloud" → "Development" in the left sidebar
    3. Click "Create Cloud Project"
    4. Fill in the project details:
       - Project Name: "Security Digital Twin" (or your preferred name)
       - Description: "AI-powered home security system"
       - Industry: "Smart Home"
       - Development Method: "Custom Development"
       - Data Center: Choose the closest region to your location
    5. Click "Create"

Step 3: Get Your API Credentials
    1. After creating the project, you'll see the project overview page
    2. Find the "Authorization Key" section
    3. Copy the "Client ID" (also called "Access ID")
    4. Copy the "Secret Key" (also called "Access Secret")
    5. Store these securely - you'll need them to configure this application

Step 4: Link Your Devices to the Project
    1. In your Cloud Project, go to the "Devices" tab
    2. Click "Link Tuya App Account"
    3. Follow the instructions to link your Tuya Smart app account
    4. This will import all devices from your Tuya Smart app
    5. Alternatively, use "Link Device by App Account" for specific devices

Step 5: Subscribe to Required APIs
    1. In your Cloud Project, go to the "API" tab
    2. Subscribe to the following API services (all are free):
       - "IoT Core" (for device control)
       - "Authorization" (for authentication)
       - "Smart Home Devices Management" (for device status)
    3. Click "Subscribe" for each service

Important Notes:
    - Keep your Client ID and Secret Key confidential
    - Do not commit these credentials to version control
    - The free tier includes 1,000 API calls per day (sufficient for this project)
    - API credentials are region-specific (US, EU, CN, IN)
"""


# ============================================================================
# DEVICE IDs
# ============================================================================
# These are the unique identifiers for your Tuya smart devices.
# You MUST replace these with your actual device IDs from the Tuya IoT Platform.

# Motion sensor in the living room (detects movement)
LIVING_ROOM_MOTION_ID = "your_motion_sensor_device_id"

# Vibration sensor on the window (detects window tampering)
WINDOW_VIBRATION_ID = "your_vibration_sensor_device_id"

# Smart lock on the front door (detects lock/unlock events)
FRONT_DOOR_LOCK_ID = "your_door_lock_device_id"

# Smart bulb for visual alerts (controlled for status indication)
SMART_BULB_ID = "your_smart_bulb_device_id"

# Siren for audible alerts (activated during critical threats)
SIREN_ID = "your_siren_device_id"


# ============================================================================
# HOW TO FIND DEVICE IDs FROM TUYA IoT PLATFORM
# ============================================================================
"""
Method 1: Using the Tuya IoT Platform Web Interface
    1. Log in to https://iot.tuya.com/
    2. Navigate to "Cloud" → "Development" → Your Project
    3. Click on the "Devices" tab
    4. You'll see a list of all devices linked to your project
    5. For each device:
       - Click on the device name to view details
       - Find the "Device ID" field (usually starts with "bf..." or similar)
       - Copy the Device ID
    6. Match each device to its purpose:
       - Motion Sensor → LIVING_ROOM_MOTION_ID
       - Vibration Sensor → WINDOW_VIBRATION_ID
       - Door Lock → FRONT_DOOR_LOCK_ID
       - Smart Bulb → SMART_BULB_ID
       - Siren → SIREN_ID

Method 2: Using the Tuya API Explorer
    1. In your Cloud Project, go to "API Explorer"
    2. Select "Smart Home Devices Management" API
    3. Choose "Get Device List" endpoint
    4. Click "Send Request"
    5. The response will show all devices with their IDs and names
    6. Copy the "id" field for each device you want to use

Method 3: Using the tuya-connector-python SDK
    1. Install the SDK: pip install tuya-connector-python
    2. Run this Python script:
    
        from tuya_connector import TuyaOpenAPI
        
        api = TuyaOpenAPI(
            endpoint="https://openapi.tuyaus.com",  # Use your region
            access_id="YOUR_CLIENT_ID",
            access_secret="YOUR_SECRET_KEY"
        )
        api.connect()
        
        response = api.get("/v1.0/iot-03/devices")
        for device in response['result']['list']:
            print(f"Name: {device['name']}, ID: {device['id']}")

Device ID Format:
    - Device IDs are typically 20-25 character alphanumeric strings
    - Example: "bf1234567890abcdef1234"
    - They are unique to each device and never change

Troubleshooting:
    - If you don't see your devices, ensure they're linked to your Cloud Project
    - Make sure devices are online in the Tuya Smart app
    - Verify you're looking at the correct Cloud Project
    - Check that you've linked your Tuya app account to the project
"""


# ============================================================================
# PUSH NOTIFICATION WEBHOOK (OPTIONAL)
# ============================================================================
# Configure a webhook URL to receive push notifications for critical alerts.
# This is optional - if not configured, notifications will be logged to console.

# Webhook URL for push notifications (Discord, Slack, or custom endpoint)
WEBHOOK_URL = "your_webhook_url_here"


# ============================================================================
# HOW TO SET UP WEBHOOK URL FOR PUSH NOTIFICATIONS
# ============================================================================
"""
The system sends push notifications for RED_CRITICAL security events.
You can configure various webhook services to receive these alerts.

Option 1: Discord Webhook (Recommended for Quick Setup)
    1. Open Discord and go to your server
    2. Right-click on a channel → "Edit Channel"
    3. Go to "Integrations" → "Webhooks"
    4. Click "New Webhook"
    5. Give it a name (e.g., "Security Alerts")
    6. Copy the "Webhook URL"
    7. Set WEBHOOK_URL to this URL
    
    Example Discord webhook URL:
    https://discord.com/api/webhooks/123456789/abcdefghijklmnop
    
    The system will send JSON messages like:
    {
        "content": "🚨 CRITICAL: Break-in attempt detected!",
        "username": "Security System"
    }

Option 2: Slack Webhook
    1. Go to https://api.slack.com/apps
    2. Click "Create New App" → "From scratch"
    3. Name your app (e.g., "Security Alerts") and select workspace
    4. Go to "Incoming Webhooks" and activate it
    5. Click "Add New Webhook to Workspace"
    6. Select a channel and authorize
    7. Copy the "Webhook URL"
    8. Set WEBHOOK_URL to this URL
    
    Example Slack webhook URL:
    https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXX
    
    The system will send JSON messages like:
    {
        "text": "🚨 CRITICAL: Break-in attempt detected!"
    }

Option 3: Custom HTTP Endpoint
    1. Set up your own HTTP server that accepts POST requests
    2. Configure it to handle JSON payloads
    3. Set WEBHOOK_URL to your endpoint URL
    
    Example custom endpoint:
    https://your-server.com/api/security-alerts
    
    The system will POST JSON like:
    {
        "message": "CRITICAL: Break-in attempt detected!",
        "priority": "high",
        "timestamp": "2024-01-15T22:30:45Z",
        "zone": "HOUSE"
    }

Option 4: No Webhook (Console Logging Only)
    1. Leave WEBHOOK_URL as "your_webhook_url_here" or set to empty string
    2. The system will log notifications to console instead
    3. Useful for development and testing

Testing Your Webhook:
    You can test your webhook URL using curl:
    
    # For Discord:
    curl -X POST "YOUR_WEBHOOK_URL" \
         -H "Content-Type: application/json" \
         -d '{"content": "Test message from Security System"}'
    
    # For Slack:
    curl -X POST "YOUR_WEBHOOK_URL" \
         -H "Content-Type: application/json" \
         -d '{"text": "Test message from Security System"}'

Security Considerations:
    - Keep your webhook URL confidential
    - Do not commit webhook URLs to version control
    - Consider using environment variables for webhook URLs
    - Some webhook services have rate limits (Discord: 30 requests/minute)
    - Webhook URLs can be regenerated if compromised
"""


# ============================================================================
# ADDITIONAL CONFIGURATION (OPTIONAL)
# ============================================================================

# Flask WebSocket server configuration
WEBSOCKET_HOST = "0.0.0.0"  # Listen on all interfaces
WEBSOCKET_PORT = 5000        # Default port for WebSocket server

# Tuya API endpoint (region-specific)
# Choose based on your Tuya account region:
# - US: https://openapi.tuyaus.com
# - EU: https://openapi.tuyaeu.com
# - CN: https://openapi.tuyacn.com
# - IN: https://openapi.tuyain.com
TUYA_ENDPOINT = "https://openapi.tuyaus.com"

# Threat detection parameters
MOTION_VIBRATION_WINDOW_SECONDS = 10  # Time window for motion+vibration pattern
CRITICAL_THREAT_THRESHOLD = 80        # Score threshold for RED_CRITICAL
WARNING_THREAT_THRESHOLD = 40         # Score threshold for YELLOW_WARNING

# Time contextual weighting
NIGHTTIME_MULTIPLIER = 1.5   # Threat score multiplier for nighttime (22:00-06:00)
DAYTIME_MULTIPLIER = 0.7     # Threat score multiplier for daytime (06:00-22:00)

# Reconnection settings
MAX_RECONNECT_DELAY_SECONDS = 16  # Maximum delay for exponential backoff
INITIAL_RECONNECT_DELAY_SECONDS = 1  # Initial delay for reconnection

# Command retry settings
MAX_COMMAND_RETRIES = 3  # Maximum number of retries for failed commands


# ============================================================================
# VALIDATION
# ============================================================================
"""
Before running the application, ensure:
1. ✓ You have valid Tuya API credentials (CLIENT_ID and SECRET_KEY)
2. ✓ All five device IDs are configured
3. ✓ Devices are online and linked to your Cloud Project
4. ✓ Required API services are subscribed in your Cloud Project
5. ✓ (Optional) Webhook URL is configured for push notifications
6. ✓ All values are set as environment variables (not hardcoded)

To validate your configuration, run:
    python backend/test_config.py

This will check that all required fields are present and properly formatted.
"""
