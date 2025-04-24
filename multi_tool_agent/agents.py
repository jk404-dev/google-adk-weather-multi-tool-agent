import os
import logging
from dotenv import load_dotenv
from google.adk.agents import Agent
from .tools import get_weather, say_hello, say_goodbye # Relative imports
from .guardrails import block_keyword_guardrail # Relative import

load_dotenv()

# Get Model Name (used by all agents defined here)
AGENT_MODEL_NAME = os.environ.get("MODEL_GEMINI_2_0_FLASH", "gemini-1.5-flash-latest")
if not os.environ.get("MODEL_GEMINI_2_0_FLASH"):
    logging.warning(f"Warning: MODEL_GEMINI_2_0_FLASH env var not set in agents.py. Defaulting to '{AGENT_MODEL_NAME}'")

# --- Sub Agents --- #

# --- Greeting Agent --- #
greeting_agent = None
try:
    greeting_agent = Agent(
        model=AGENT_MODEL_NAME,
        name="greeting_agent",
        instruction="You are the Greeting Agent. Your ONLY task is to provide a friendly greeting using the 'say_hello' tool. Do nothing else.",
        description="Handles simple greetings and hellos using the 'say_hello' tool.",
        tools=[say_hello],
    )
    print(f"✅ Sub-Agent '{greeting_agent.name}' defined.")
except Exception as e:
    print(f"❌ Could not define Greeting agent. Check Model/API Key ({AGENT_MODEL_NAME}). Error: {e}")
    greeting_agent = None # Ensure it's None if failed

# --- Farewell Agent --- #
farewell_agent = None
try:
    farewell_agent = Agent(
        model=AGENT_MODEL_NAME,
        name="farewell_agent",
        instruction="You are the Farewell Agent. Your ONLY task is to provide a polite goodbye message using the 'say_goodbye' tool. Do not perform any other actions.",
        description="Handles simple farewells and goodbyes using the 'say_goodbye' tool.",
        tools=[say_goodbye],
    )
    print(f"✅ Sub-Agent '{farewell_agent.name}' defined.")
except Exception as e:
    print(f"❌ Could not define Farewell agent. Check Model/API Key ({AGENT_MODEL_NAME}). Error: {e}")
    farewell_agent = None # Ensure it's None if failed

# --- Root Agent --- #
root_agent = None

# Check prerequisites before creating the root agent
if greeting_agent and farewell_agent:
    try:
        root_agent = Agent(
            name="weather_agent_v5_model_guardrail",
            model=AGENT_MODEL_NAME,
            description="Main agent: Handles weather, delegates greetings/farewells, includes input keyword guardrail.",
            instruction="You are a weather assistant. Your primary goal is to answer the user's specific question concisely. \
                        **FIRST**, determine if the user is asking for a specific weather detail (like temperature, wind, humidity) or general weather ('how is the weather?'). \
                        **SECOND**, use the 'get_weather' tool ONLY to get the necessary data for the requested city. This tool returns a *very detailed report*. \
                        **THIRD**, look at the user's original question again. \
                        **FOURTH**, from the detailed tool report, extract ONLY the specific piece of information the user asked for. \
                        **FIFTH**, present ONLY that single piece of information in your answer (e.g., 'The temperature in London is X°C.', 'The wind in Paris is blowing from the X at Y kph.'). \
                        **EXCEPTION:** If the user asked a general question like 'What's the weather like?', then and ONLY then should you provide the full, detailed report from the tool. \
                        Also delegate simple greetings to 'greeting_agent' and farewells to 'farewell_agent'.",
            tools=[get_weather], # Use the imported tool
            sub_agents=[agent for agent in [greeting_agent, farewell_agent] if agent is not None], # Filter out None agents
            output_key="last_weather_report",
            before_model_callback=block_keyword_guardrail # Use the imported guardrail
        )
        print(f"✅ Root Agent '{root_agent.name}' defined with before_model_callback.")
    except Exception as e:
        print(f"❌ Could not define Root agent. Error: {e}")
        root_agent = None # Ensure it's None if failed

else:
    print("❌ Cannot define root agent. One or more sub-agents (greeting_agent, farewell_agent) failed initialization.")
