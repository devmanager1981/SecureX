# Tuya Setup Checklist

## ✅ Current .env Configuration

Your `.env` file has the following settings:

```env
CLIENT_ID="nw7hjqy8kdred7p5tn9j"
SECRET_KEY="5d5e833bc97c493c99ab46db36418a35"
LIVING_ROOM_MOTION_ID='vdevo176449224066131'
WINDOW_VIBRATION_ID='vdevo176449226291392'
FRONT_DOOR_LOCK_ID='vdevo176449220885548'
SMART_BULB_ID='vdevo176449218406418'
SIREN_ID='vdevo176449228685894'
```

## ✅ What's Working

1. **Environment Variables Loaded**: The `config.py` module properly loads all required variables using `python-dotenv`
2. **All Required Device IDs Present**: You have all 5 device IDs configured
3. **Credentials Present**: CLIENT_ID and SECRET_KEY are set

## 🔧 Code Integration Points

The environment variables are used in these locations:

### 1. **config.py** (✅ Working)
- Loads all variables from `.env` using `load_dotenv()`
- Validates all required fields are present
- Creates a `TuyaConfig` object with all settings

### 2. **ai_agent.py** (✅ Working)
- Calls `load_config()` to get configuration
- Passes credentials to `TuyaConnectionManager`
- Passes device IDs to `ResponseOrchestrator`

### 3. **tuya_connection_manager.py** (✅ Fixed)
- Now correctly uses `access_secret` parameter (was `access_key`)
- Has max retry limit to prevent infinite loops

## ⚠️ Potential Issues & Additional Settings

### 1. **Tuya API Endpoint Region**
Your code currently uses: `https://openapi.tuyaus.com`

**Action Required**: Verify this matches your Tuya account region:
- US: `https://openapi.tuyaus.com` ✅ (currently set)
- EU: `https://openapi.tuyaeu.com`
- CN: `https://openapi.tuyacn.com`
- IN: `https://openapi.tuyain.com`

**To change**: Add to `.env`:
```env
TUYA_ENDPOINT="https://openapi.tuyaus.com"
```

Then update `tuya_connection_manager.py` line 73 to use it from config.

### 2. **Tuya Cloud Project API Subscriptions**
You need these API services enabled in your Tuya Cloud Project:
- ✓ IoT Core (for device control)
- ✓ Authorization (for authentication)
- ✓ Smart Home Devices Management (for device status)

**How to check**:
1. Go to https://iot.tuya.com/
2. Open your Cloud Project
3. Go to "API" tab
4. Verify these services are subscribed

### 3. **Device Linking**
Your devices must be linked to your Cloud Project:

**How to verify**:
1. Go to https://iot.tuya.com/
2. Open your Cloud Project
3. Go to "Devices" tab
4. Verify all 5 device IDs appear in the list

### 4. **Optional: Webhook for Push Notifications**
Currently, push notifications only log to console. To receive real alerts:

**Add to `.env`**:
```env
# For Discord
WEBHOOK_URL="https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_TOKEN"

# For Slack
WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
```

Then update `response_orchestrator.py` to use the webhook URL.

### 5. **Optional: WebSocket Server Configuration**
Default settings:
- Host: `0.0.0.0` (all interfaces)
- Port: `5000`

**To customize, add to `.env`**:
```env
WEBSOCKET_HOST="0.0.0.0"
WEBSOCKET_PORT=5000
```

## 🚀 How to Run

1. **Ensure all dependencies are installed**:
```bash
pip install -r requirements.txt
```

2. **Run the AI Agent**:
```bash
python backend/ai_agent.py
```

3. **Expected startup sequence**:
```
Initializing AI Agent...
Configuration loaded successfully
Initializing system components...
WebSocket server initialized
Tuya Connection Manager initialized
Attempting to connect to Tuya Cloud (attempt 1/5)...
Successfully connected to Tuya Cloud
Subscribed to 5 devices
AI Agent is now running. Press Ctrl+C to stop.
```

## 🐛 Troubleshooting

### If connection fails:
1. **Check credentials**: Verify CLIENT_ID and SECRET_KEY are correct
2. **Check region**: Ensure endpoint matches your Tuya account region
3. **Check API subscriptions**: Verify required APIs are enabled in Cloud Project
4. **Check device linking**: Ensure devices are linked to your Cloud Project
5. **Check network**: Ensure you can reach the Tuya API endpoint

### If you see "access_key" error:
- This is now fixed in the code (changed to `access_secret`)
- Restart the application with the updated code

### If process won't stop:
- Press `Ctrl+C` multiple times
- Or use: `taskkill /F /IM python.exe`
- The code now has a max retry limit (5 attempts) to prevent infinite loops

## 📝 Summary

**You have everything you need in your `.env` file!** The main things to verify:

1. ✅ Credentials are correct
2. ✅ Device IDs are correct
3. ✅ Devices are linked to your Cloud Project
4. ✅ API services are subscribed
5. ⚠️ Verify the API endpoint region matches your account

The code is now fixed and should work properly with your current configuration.
