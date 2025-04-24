import os
import requests
import logging
from google.adk.tools.tool_context import ToolContext
from .config import WEATHER_API_KEY 

def get_weather(city: str, tool_context: ToolContext) -> dict:
    """Retrieves the current weather report for a specified city using WeatherAPI.com."""
    print(f"--- Tool: get_weather called for {city} ---")

    # --- Check for API Key ---
    if not WEATHER_API_KEY:
        print("--- Tool Error: WEATHER_API_KEY environment variable not set. ---")
        return {"status": "error", "error_message": "Weather API key is missing. Cannot fetch weather."}

    # --- Read temperature preference from state ---
    preferred_unit_state = tool_context.state.get("user_preference_temperature_unit", "Celsius") # Default to Celsius
    print(f"--- Tool: Reading state 'user_preference_temperature_unit': {preferred_unit_state} ---")

    # Determine the temperature symbol based on preference
    if preferred_unit_state == "Fahrenheit":
        temp_symbol = "°F"
    else: # Default to Celsius
        temp_symbol = "°C"

    # --- Call WeatherAPI.com API ---
    base_url = "http://api.weatherapi.com/v1/current.json" # <<< WeatherAPI URL
    params = {
        "q": city,
        "key": WEATHER_API_KEY, # <<< WeatherAPI uses 'key'
        # No 'units' parameter needed for WeatherAPI, it returns both C/F
    }

    try:
        print(f"--- Tool: Calling WeatherAPI.com API for {city} ---")
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # --- Process Successful Response ---
        data = response.json()
        print(f"--- Tool: API Response Data (partial): {str(data)[:200]}... ---")

        if data.get("current") and data["current"].get("condition"):
            current_data = data["current"]
            condition_data = current_data["condition"]
            description = condition_data.get("text", "N/A")
            temp_c = current_data.get("temp_c")
            temp_f = current_data.get("temp_f")
            feelslike_c = current_data.get("feelslike_c")
            feelslike_f = current_data.get("feelslike_f")
            humidity = current_data.get("humidity")
            wind_kph = current_data.get("wind_kph")
            wind_mph = current_data.get("wind_mph")
            wind_dir = current_data.get("wind_dir")
            uv_index = current_data.get("uv")
            pressure_mb = current_data.get("pressure_mb")
            pressure_in = current_data.get("pressure_in")
            precip_mm = current_data.get("precip_mm")
            precip_in = current_data.get("precip_in")
            vis_km = current_data.get("vis_km")
            vis_miles = current_data.get("vis_miles")
            gust_kph = current_data.get("gust_kph")
            gust_mph = current_data.get("gust_mph")
            windchill_c = current_data.get("windchill_c") # May not always be present/relevant
            windchill_f = current_data.get("windchill_f")
            heatindex_c = current_data.get("heatindex_c") # May not always be present/relevant
            heatindex_f = current_data.get("heatindex_f")
            dewpoint_c = current_data.get("dewpoint_c")
            dewpoint_f = current_data.get("dewpoint_f")
            last_updated = current_data.get("last_updated")

            # Select temperature and units based on state preference
            if preferred_unit_state == "Fahrenheit":
                temp = temp_f
                feels_like_temp = feelslike_f
                wind_speed = wind_mph
                wind_unit = "mph"
                pressure = pressure_in
                pressure_unit = "inHg"
                precip = precip_in
                precip_unit = "in"
                visibility = vis_miles
                visibility_unit = "miles"
                gust_speed = gust_mph
                wind_chill_temp = windchill_f
                heat_index_temp = heatindex_f
                dew_point_temp = dewpoint_f
            else: # Default to Celsius
                temp = temp_c
                feels_like_temp = feelslike_c
                wind_speed = wind_kph
                wind_unit = "kph"
                pressure = pressure_mb
                pressure_unit = "mb"
                precip = precip_mm
                precip_unit = "mm"
                visibility = vis_km
                visibility_unit = "km"
                gust_speed = gust_kph
                wind_chill_temp = windchill_c
                heat_index_temp = heatindex_c
                dew_point_temp = dewpoint_c

            # Build the report string piece by piece
            report_parts = []

            # Main condition and temp
            if temp is not None:
                 report_parts.append(f"The weather in {city.capitalize()} is {description} with a temperature of {temp:.1f}{temp_symbol}.")
            else:
                 report_parts.append(f"The weather in {city.capitalize()} is {description}.")
                 print("--- Tool Warning: Temperature data (temp_c/temp_f) missing in API response. ---")

            # Feels like temp
            if feels_like_temp is not None:
                report_parts.append(f"It feels like {feels_like_temp:.1f}{temp_symbol}.")

            # Humidity
            if humidity is not None:
                report_parts.append(f"Humidity is at {humidity}%." )

            # Wind
            if wind_speed is not None and wind_dir:
                report_parts.append(f"Wind is blowing from the {wind_dir} at {wind_speed:.1f} {wind_unit}.")
            elif wind_speed is not None:
                 report_parts.append(f"Wind speed is {wind_speed:.1f} {wind_unit}.")

            # UV Index
            if uv_index is not None:
                 report_parts.append(f"The UV index is {uv_index}.")

            # Pressure
            if pressure is not None:
                report_parts.append(f"Pressure is {pressure:.2f} {pressure_unit}.")

            # Precipitation
            if precip is not None:
                report_parts.append(f"Precipitation is {precip:.2f} {precip_unit}.")

            # Visibility
            if visibility is not None:
                report_parts.append(f"Visibility is {visibility:.1f} {visibility_unit}.")

            # Wind Gust
            if gust_speed is not None:
                 report_parts.append(f"Wind gusts up to {gust_speed:.1f} {wind_unit}.")

            # Dew Point
            if dew_point_temp is not None:
                 report_parts.append(f"Dew point is {dew_point_temp:.1f}{temp_symbol}.")

            # Wind Chill (only if significantly different from temp and feels_like)
            if wind_chill_temp is not None and feels_like_temp is not None and wind_chill_temp < feels_like_temp - 1: # Heuristic condition
                 report_parts.append(f"Wind chill makes it feel like {wind_chill_temp:.1f}{temp_symbol}.")

            # Heat Index (only if significantly different from temp and feels_like)
            if heat_index_temp is not None and feels_like_temp is not None and heat_index_temp > feels_like_temp + 1: # Heuristic condition
                 report_parts.append(f"Heat index makes it feel like {heat_index_temp:.1f}{temp_symbol}.")

            # Last Updated
            if last_updated:
                report_parts.append(f"(Last updated: {last_updated})")

            # Join the parts into a single report string
            report = " ".join(report_parts)

            result = {"status": "success", "report": report}
            print(f"--- Tool: Generated report in {preferred_unit_state}. Result: {result} ---")

            # Update state (optional)
            tool_context.state["last_city_checked"] = city # Updated key name slightly
            print(f"--- Tool: Updated state 'last_city_checked': {city} ---")
            return result
        else:
            print("--- Tool Error: Unexpected API response format from WeatherAPI.com. ---")
            return {"status": "error", "error_message": f"Received unexpected weather data format for '{city}'."}

    except requests.exceptions.HTTPError as http_err:
        status_code = response.status_code
        # WeatherAPI Error Handling (Consult their docs for specifics)
        if status_code == 400: # Often used for location not found or bad request
            try:
                error_data = response.json()
                error_message = error_data.get("error", {}).get("message", "request issue")
                print(f"--- Tool Error: WeatherAPI returned 400: {error_message} ---")
                # Check if it's a location not found error (code 1006)
                if error_data.get("error", {}).get("code") == 1006:
                     return {"status": "error", "error_message": f"Sorry, I couldn't find weather information for '{city}'."}
                else:
                     return {"status": "error", "error_message": f"There was a problem with the weather request for '{city}': {error_message}"}
            except ValueError: # Handle cases where error response isn't JSON
                print(f"--- Tool Error: WeatherAPI returned 400, but error response wasn't valid JSON. ---")
                return {"status": "error", "error_message": f"There was an unspecified problem with the weather request for '{city}'."}

        elif status_code == 401 or status_code == 403: # API key issues
             print(f"--- Tool Error: WeatherAPI returned {status_code} (API key issue). ---")
             return {"status": "error", "error_message": "There was an authentication issue with the weather service. Please check the API key."}
        else:
            print(f"--- Tool Error: HTTP error occurred: {http_err} (Status: {status_code}) ---")
            return {"status": "error", "error_message": f"An HTTP error occurred while fetching weather for '{city}'. Status: {status_code}"}
    except requests.exceptions.ConnectionError as conn_err:
        print(f"--- Tool Error: Connection error occurred: {conn_err} ---")
        return {"status": "error", "error_message": f"Could not connect to the weather service to get information for '{city}'."}
    except requests.exceptions.Timeout as timeout_err:
        print(f"--- Tool Error: Request timed out: {timeout_err} ---")
        return {"status": "error", "error_message": f"The request to the weather service timed out for '{city}'."}
    except requests.exceptions.RequestException as req_err:
        # Catch any other request-related errors
        print(f"--- Tool Error: An ambiguous request error occurred: {req_err} ---")
        return {"status": "error", "error_message": f"An error occurred while requesting weather data for '{city}'."}
    except Exception as e:
        # Catch any other unexpected errors during processing
        print(f"--- Tool Error: An unexpected error occurred in get_weather: {e} ---")
        logging.exception("Unexpected error in get_weather tool") # Log the full traceback for debugging
        return {"status": "error", "error_message": f"An unexpected error occurred while processing the weather request for '{city}'."}

def say_hello(name: str = "there") -> str:
    """Provides a simple greeting, optionally addressing the user by name.

    Args:
        name (str, optional): The name of the person to greet. Defaults to "there".

    Returns:
        str: A friendly greeting message.
    """
    print(f"--- Tool: say_hello called with name: {name} ---")
    return f"Hello, {name}!"

def say_goodbye() -> str:
    """Provides a simple farewell message to conclude the conversation."""
    print(f"--- Tool: say_goodbye called ---")
    return "Goodbye! Have a great day."
