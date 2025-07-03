import os
import requests
import sqlite3
from google import genai
from google.genai import types
from dotenv import load_dotenv

def initialize_environment():
    """Initialize environment variables and API clients"""
    load_dotenv()
    
    # Set and call upon environment variables from API's
    my_api_key = os.getenv('API_KEY')
    geoapify_key = os.getenv('GEOAPIFY_KEY')

    # Initialize genAI client (Google Gemini API)
    genai.api_key = my_api_key
    client = genai.Client(api_key=my_api_key)
    
    return client, geoapify_key

def get_travel_recommendation(client, user_query):
    """Get travel recommendation from Gemini AI"""
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            system_instruction="You are a travel agent. Recommend a destination and provide:\n. First line: DESTINATION_NAME\n. Second line: LATITUDE,LONGITUDE without any symbols\n. Followed by a brief description and cost breakdown."
        ),
        contents=user_query,
    )
    return response

def get_lat_lon(response):
    lines = response.split('\n')
    destination = lines[0].strip()
    lat, lon = map(float, lines[1].strip().split(','))
    return lat, lon

def get_destination(response):
    lines = response.split('\n')
    destination = lines[0].strip()
    return destination

def process_recommendation(response, geoapify_key):
    """Process the AI recommendation and get a list of places of possible interest"""
    print("\nResponse:")
    response = response.text
    print(response)
    
    # Get the coordinates from the outputted places and locations
    destination = get_destination(response)
    lat, lon = get_lat_lon(response)
    
    # Get and show places of interest to user
    print(f"\nTop Tourist/Entertainment Spots in {destination}:")
    places_info = get_places(lat, lon, geoapify_key)
    print(places_info)
    
    return destination


def show_previous_recommendations():
    """Show previous recommendations from database"""
    print("\nWould you like to see previous recommendations? (yes/no)")
    if input().lower() == 'yes':
        print("View options:")
        print("1. All recommendations")
        print("2. Recommendations by continent")
        choice = input("Enter choice (1 or 2): ")
        
        if choice == '1':
            print(show_all_recommendations())
        elif choice == '2':
            continent = input("Enter continent name: ").strip()
            print(show_recommendations_by_continent(continent))
        else:
            print("Invalid choice")

def main():
    """Main function to run the travel recommendation program"""
    # Initialize database and create environment
    create_places_database()
    client, geoapify_key = initialize_environment()
    
    # Get the user input
    user_query = input("Please enter details about your dream travel destination!\nFeel free to include: \n-Budget \n-Where you are traveling from + Max distance \n-Interests (beaches, hiking, trying new foods)\n")
    
    # Get and process the recommendation from the Gemini API 
    response = get_travel_recommendation(client, user_query)
    process_recommendation(response, geoapify_key)
    
    # Debug database and show previous recommendations
    debug_database()
    show_previous_recommendations()

# Database functions to create and update database (travel.db)
def create_places_database():
    conn = sqlite3.connect('travel.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS places
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  destination TEXT,
                  name TEXT,
                  address TEXT,
                  continent TEXT,
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

# Function to identify and categorize places by their continent 
def get_continent(lat, lon):
    lat, lon = float(lat), float(lon)
    if ( (-168 <= lon <= -52) and (7 <= lat <= 72) ) or ( (-180 <= lon <= -130) and (51 <= lat <= 72) ):
        return "North America"
    elif (-82 <= lon <= -34) and (-56 <= lat <= 13):
        return "South America"
    elif (-25 <= lon <= 60) and (35 <= lat <= 75):
        return "Europe"
    elif (-20 <= lon <= 55) and (-35 <= lat <= 38):
        return "Africa"
    elif ( (25 <= lon <= 180) and (5 <= lat <= 75) ) or ( (100 <= lon <= 180) and (-10 <= lat <= 75) ) or ( (-180 <= lon <= -130) and (51 <= lat <= 72) ):
        return "Asia"
    elif (110 <= lon <= 180) and (-50 <= lat <= 10) or (lon >= 130 and -50 <= lat <= -10):
        return "Australia"
    elif -90 <= lat <= -60:
        return "Antarctica"
    else:
        return "Unknown"

# Function to store the places reccomended into the database (travel.db)
def store_places(destination, places_data, geoapify_key, max_places=5):
    """Store places with city names instead of coordinates"""
    conn = sqlite3.connect('travel.db')
    c = conn.cursor()
    lat, lon = map(float, destination.split(','))
    continent = get_continent(lat, lon)
    city_name = get_city_name(lat, lon, geoapify_key)
    
    for place in places_data[:max_places]: 
        c.execute('''INSERT INTO places 
                    (destination, name, address, continent)
                    VALUES (?, ?, ?, ?)''',
                (city_name,
                 place['properties'].get('name', 'Unnamed location'),
                 place['properties'].get('formatted', 'Address not available'),
                 continent))
    conn.commit()
    conn.close()

# Function to show the reccomendations by coninent in the database
def show_recommendations_by_continent(continent):
    """Show recommendations from database grouped by city"""
    conn = sqlite3.connect('travel.db')
    c = conn.cursor()
    
    continent_variations = {
        'america': ['North America', 'South America'],
        'north america': ['North America'],
        'south america': ['South America'],
        'europe': ['Europe'],
        'africa': ['Africa'],
        'asia': ['Asia'],
        'australia': ['Australia'],
        'oceania': ['Australia'],
        'antarctica': ['Antarctica']
    }
    
    continent_lower = continent.lower()
    if continent_lower in continent_variations:
        continents_to_search = continent_variations[continent_lower]
        placeholders = ','.join(['?' for _ in continents_to_search])
        query = f"""
            SELECT destination, name, address 
            FROM places 
            WHERE continent IN ({placeholders})
            ORDER BY destination, name
        """
        c.execute(query, continents_to_search)
    else:
        query = """
            SELECT destination, name, address 
            FROM places 
            WHERE LOWER(continent) = LOWER(?)
            ORDER BY destination, name
        """
        c.execute(query, (continent,))
    
    results = c.fetchall()
    conn.close()
    
    if not results:
        return f"No recommendations found for {continent}."
    
    # Group by destination (cities in our case)
    grouped = {}
    for dest, name, address in results:
        if dest not in grouped:
            grouped[dest] = []
        grouped[dest].append((name, address))
    
    # Format output
    output = [f"\nRecommendations in {continent}:"]
    for dest, places in grouped.items():
        output.append(f"\n{dest}:")
        for name, address in places:
            output.append(f"- {name}: {address}")
    
    return "\n".join(output)

# Function to show all recommendations in the database
def show_all_recommendations():
    """Show all recommendations from database grouped by city"""
    conn = sqlite3.connect('travel.db')
    c = conn.cursor()
    
    c.execute("""
        SELECT destination, name, address, continent 
        FROM places 
        ORDER BY continent, destination, name
    """)
    results = c.fetchall()
    conn.close()
    
    if not results:
        return "No recommendations found in database."
    
    # Group by continent and then by destination
    grouped = {}
    for dest, name, address, continent in results:
        if continent not in grouped:
            grouped[continent] = {}
        if dest not in grouped[continent]:
            grouped[continent][dest] = []
        grouped[continent][dest].append((name, address))
    
    # Format output
    output = ["\nAll stored recommendations:"]
    for continent, destinations in grouped.items():
        output.append(f"\n{continent}:")
        for dest, places in destinations.items():
            output.append(f"\n  {dest}:")
            for name, address in places:
                output.append(f"  - {name}: {address}")
    
    return "\n".join(output)


def get_city_name(lat, lon, geoapify_key):
    """Convert coordinates to city name using Geoapify's reverse geocoding"""
    base_url = "https://api.geoapify.com/v1/geocode/reverse"
    params = {
        'lat': lat,
        'lon': lon,
        'apiKey': geoapify_key,
        'format': 'json'
    }
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if data.get('results'):
            # Try to get city name if not fall back to country 
            city = data['results'][0].get('city', '')
            country = data['results'][0].get('country', '')
            if city and country:
                return f"{city}, {country}"
            elif country:
                return country
        return f"{lat},{lon}"  # fallback to coordinates if no location found
    except Exception as e:
        print(f"Error reverse geocoding: {e}")
        return f"{lat},{lon}"

# Function to show information about database (how many recs are there and the varying continents)
def debug_database():
    conn = sqlite3.connect('travel.db')
    c = conn.cursor()
    c.execute("SELECT DISTINCT continent FROM places")
    continents = c.fetchall()
    print(f"Continents in database: {[c[0] for c in continents]}")
    c.execute("SELECT COUNT(*) FROM places")
    count = c.fetchone()[0]
    print(f"Total places in database: {count}")
    conn.close()

# Function to get nearby places of interest with the Geoapify API
def get_places(lat, lon, geoapify_key, radius=8000, categories="tourism,entertainment"):
    base_url = "https://api.geoapify.com/v2/places"
    params = {
        'categories': categories,
        'filter': f'circle:{lon},{lat},{radius}', 
        'limit': 5,
        'apiKey': geoapify_key
    }
    response = requests.get(base_url, params=params)
    response.raise_for_status()
    data = response.json()
    if not data.get('features'):
        return "No notable tourist spots found nearby."
    places_info = []
    for place in data['features'][:5]:
        name = place['properties'].get('name', 'Unnamed location')
        categories = ", ".join(place['properties'].get('categories', []))
        address = place['properties'].get('formatted', 'Address not available')
        places_info.append(f"- {name}: {address}")
    store_places(f"{lat},{lon}", data['features'], geoapify_key, 5)
    return "\n".join(places_info)

if __name__ == "__main__":
    main()