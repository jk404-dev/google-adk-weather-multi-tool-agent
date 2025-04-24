import os
import requests
from dotenv import load_dotenv 

load_dotenv() 
api_key = os.getenv("WEATHER_API_KEY")
print(f"Debug: API Key loaded as: {api_key}")   

def get_weather(city):
    if not api_key:
        return {"error": "WEATHER_API_KEY not found in environment."}

    # Use WeatherAPI.com endpoint and 'key' parameter
    url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={city}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        data = response.json()
        return data
    except requests.exceptions.HTTPError as http_err:
        # Try to return the error json from the API if possible
        try:
            error_data = response.json()
        except ValueError:
            error_data = {"error": {"message": f"HTTP Error: {http_err}", "code": response.status_code}}
        print(f"HTTP error occurred: {http_err} - {response.status_code}")
        return error_data # Return API error message if available
    except requests.exceptions.RequestException as req_err:
        print(f"Request error occurred: {req_err}")
        return {"error": f"Request Error: {req_err}"}
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return {"error": f"Unexpected Error: {e}"}


print(get_weather("New York"))
