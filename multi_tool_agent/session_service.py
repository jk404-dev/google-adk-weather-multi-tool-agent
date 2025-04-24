from google.adk.sessions import InMemorySessionService
# Import constants from config
from .config import (
    APP_NAME,
    USER_ID_STATEFUL,
    SESSION_ID_STATEFUL,
    initial_state
)
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
