import os
import sys
import logging
from dotenv import load_dotenv

# Load .env file once here for all modules
load_dotenv()

# --- API Keys & Model --- #

# Google API Key (Required)
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    print("CRITICAL ERROR: GOOGLE_API_KEY environment variable not set. Exiting.")
    sys.exit(1)

# Weather API Key (Required by tools.py)
WEATHER_API_KEY = os.environ.get("WEATHER_API_KEY")
if not WEATHER_API_KEY:
    # Log a warning here, the tool itself will return an error message if called
    logging.warning("Config Warning: WEATHER_API_KEY environment variable not set. Weather tool will fail.")

# Agent Model Name (Optional, has default)
DEFAULT_MODEL = "gemini-1.5-flash-latest"
AGENT_MODEL_NAME = os.environ.get("MODEL_GEMINI_2_0_FLASH", DEFAULT_MODEL)
if not os.environ.get("MODEL_GEMINI_2_0_FLASH"):
    logging.warning(f"Config Warning: MODEL_GEMINI_2_0_FLASH env var not set. Defaulting to '{AGENT_MODEL_NAME}'")

# --- Session Configuration --- #
APP_NAME = "weather_tutorial_app"

# Example User/Session IDs (Consider making dynamic in a real application)
USER_ID_DEFAULT = "user_1"
SESSION_ID_DEFAULT = "session_001"

# Stateful Session Constants
USER_ID_STATEFUL = "user_state_demo"
SESSION_ID_STATEFUL = "session_state_demo_001"

initial_state = {
    "user_preference_temperature_unit": "Celsius"
}

print("Configuration loaded.") 