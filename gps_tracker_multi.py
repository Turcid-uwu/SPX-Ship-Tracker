import requests
import json
import time
from datetime import datetime

# Configuration
URL = "https://sxcontent9668.azureedge.us/cms-assets/starship_tracker_public.json"
RENEW_INTERVAL = 10  # Seconds between updates

def fetch_current_coords():
    """
    Fetches the JSON data from the API and extracts current latitude and longitude
    for all ships in the data. Returns a dictionary of ship_id to coordinates.
    Returns an empty dict if an error occurs.
    """
    try:
        # Set a timeout for the request (e.g., 5 seconds)
        response = requests.get(URL, timeout=5)
        
        # Check for HTTP errors (4xx or 5xx)
        response.raise_for_status()
        
        # Parse the JSON data
        data = response.json()
        
        # Initialize coordinates dictionary
        all_ship_coords = {}
        
        # Iterate through each ship ID in the JSON (e.g., "ship40", "ship41", etc.)
        if isinstance(data, dict):
            for ship_id in data.keys():
                try:
                    ship_data = data[ship_id]
                    current_data = ship_data.get('current')
                    
                    if current_data:
                        latitude = current_data.get('latitude')
                        longitude = current_data.get('longitude')
                        altitude = current_data.get('altitude')
                        speed = current_data.get('speed')
                        
                        if latitude is not None and longitude is not None and altitude is not None:
                            all_ship_coords[ship_id] = {
                                'latitude': latitude,
                                'longitude': longitude,
                                'altitude': altitude,
                                'speed': speed
                            }
                except (TypeError, AttributeError):
                    # Skip ships with missing or malformed data
                    continue
            
            return all_ship_coords
            
    except requests.exceptions.RequestException as e:
        print(f"Network Error: {e}")
    except json.JSONDecodeError as e:
        print(f"JSON Parsing Error: {e}")
    except Exception as e:
        print(f"Unexpected Error: {e}")
    
    return {}

def main():
    print("=" * 50)
    print("Multi-Ship GPS Tracker")
    print("=" * 50)
    print(f"Updating locations every {RENEW_INTERVAL} seconds.\n")
    
    while True:
        all_ships = fetch_current_coords()
        
        if all_ships:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]")
            print(f"Tracking {len(all_ships)} ship(s):")
            print("-" * 50)
            
            for ship_id in sorted(all_ships.keys()):
                info = all_ships[ship_id]
                print(f"\n  {ship_id}:")
                print(f"    Latitude: {info['latitude']}")
                print(f"    Longitude: {info['longitude']}")
                
                if float(info['altitude'] < 0):
                    print(f"    Altitude: 0 KM")
                else:
                    print(f"    Altitude: {round(float(info['altitude'] / 1000), 2)} KM")

                print(f"    Speed: {round(float(info['speed']), 0)} KM/H")

                print("\n\n")
        else:
            print("Warning: Could not retrieve GPS data for any ships. Retrying...")
        
        # Wait before the next loop
        time.sleep(RENEW_INTERVAL)
        

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopping tracker...")
