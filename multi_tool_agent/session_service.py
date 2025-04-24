from google.adk.sessions import InMemorySessionService

# Define constants for identifying the interaction context
APP_NAME = "weather_tutorial_app"
USER_ID = "user_1" # Example User ID (consider making dynamic)
SESSION_ID = "session_001" # Example Session ID (consider making dynamic)

# Define constants for the stateful session
USER_ID_STATEFUL = "user_state_demo"
SESSION_ID_STATEFUL = "session_state_demo_001"

initial_state = {
    "user_preference_temperature_unit": "Celsius"
}

# Create the stateful session service instance
session_service_stateful = InMemorySessionService()

# Initialize the specific stateful session (optional, can be done on first use)
session_stateful = session_service_stateful.create_session(
    app_name=APP_NAME,
    user_id=USER_ID_STATEFUL,
    session_id=SESSION_ID_STATEFUL,
    state=initial_state
)
print(f"Stateful Session created/initialized: App='{APP_NAME}', User='{USER_ID_STATEFUL}', Session='{SESSION_ID_STATEFUL}'")
