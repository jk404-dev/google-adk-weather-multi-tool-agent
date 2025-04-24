import asyncio
import logging
from google.adk.runners import Runner
from google.genai import types

# Import components from other modules
from .session_service import session_service_stateful, APP_NAME, USER_ID_STATEFUL, SESSION_ID_STATEFUL
from .agents import root_agent # Import the main agent

import warnings
warnings.filterwarnings("ignore")

logging.basicConfig(level=logging.INFO)
# --- Runner Definition --- #
runner = None
if root_agent and session_service_stateful:
    try:
        runner = Runner(
            agent=root_agent, # Use the imported root agent
            app_name=APP_NAME, # Use the imported app name
            session_service=session_service_stateful # Use the imported service
        )
        print(f"✅ Runner created for agent '{runner.agent.name}' using stateful session service.")
    except Exception as e:
        print(f"❌ Failed to create Runner. Error: {e}")
else:
    if not root_agent:
        print("❌ Cannot create Runner because root_agent is not defined or failed initialization.")
    if not session_service_stateful:
        print("❌ Cannot create Runner because session_service_stateful is not defined.")


# --- Async Execution Logic --- #

async def call_agent_async(query: str, runner_instance, user_id, session_id):
    """Sends a query to the agent and prints the final response."""
    if not runner_instance:
        print("Error: Runner is not initialized. Cannot call agent.")
        return

    print(f"\n>>> User Query: {query}")

    # Prepare the user's message in ADK format
    content = types.Content(role='user', parts=[types.Part(text=query)])

    final_response_text = "Agent did not produce a final response." # Default

    try:
        # Key Concept: run_async executes the agent logic and yields Events.
        # We iterate through events to find the final answer.
        async for event in runner_instance.run_async(user_id=user_id, session_id=session_id, new_message=content):
            # You can uncomment the line below to see *all* events during execution
            # print(f"  [Event] Author: {event.author}, Type: {type(event).__name__}, Final: {event.is_final_response()}, Content: {event.content}")

            # Key Concept: is_final_response() marks the concluding message for the turn.
            if event.is_final_response():
                if event.content and event.content.parts:
                   # Assuming text response in the first part
                   final_response_text = event.content.parts[0].text
                elif event.actions and event.actions.escalate: # Handle potential errors/escalations
                   final_response_text = f"Agent escalated: {event.error_message or 'No specific message.'}"
                # Add more checks here if needed (e.g., specific error codes)
                break # Stop processing events once the final response is found
    except Exception as e:
        print(f"\n--- Error during agent execution: {e} ---")
        logging.exception("Error in runner.run_async")
        final_response_text = "An error occurred during agent processing."

    print(f"<<< Agent Response: {final_response_text}")


async def run_conversation(): # Renamed for clarity
    """Runs a predefined conversation flow for testing."""
    if not runner:
        print("Error: Runner not available. Cannot run conversation.")
        return

    print("\n--- Running Test Conversation ---")

    # Use the runner for the agent with the callback and the existing stateful session ID
    # Define a helper lambda for cleaner interaction calls
    interaction_func = lambda query: call_agent_async(query,
                                                      runner,
                                                      USER_ID_STATEFUL,
                                                      SESSION_ID_STATEFUL
                                                    )
    # 1. Normal request
    print("--- Turn 1: Requesting weather in London --- ")
    await interaction_func("What is the weather in London?")

    # 2. Request containing the blocked keyword (Callback intercepts)
    print("\n--- Turn 2: Requesting with blocked keyword --- ")
    await interaction_func("BLOCK the request for weather in Tokyo")

    # 3. Normal greeting (Callback allows root agent, delegation happens)
    print("\n--- Turn 3: Sending a greeting --- ")
    await interaction_func("Hello again")

# --- Main Execution Block --- #
if __name__ == "__main__":
    if runner: # Only attempt to run if the runner was successfully created
        try:
            asyncio.run(run_conversation())
        except Exception as e:
            print(f"An error occurred during conversation execution: {e}")
            logging.exception("Error running conversation")
    else:
        print("Execution skipped because the Runner could not be initialized.")