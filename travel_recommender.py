import os
import requests
import sqlite3
from google import genai
from google.genai import types
from dotenv import load_dotenv
load_dotenv()

# Set environment variables
my_api_key = os.getenv('API_KEY')
geoapify_key = os.getenv('GEOAPIFY_KEY')

genai.api_key = my_api_key

# Create a genAI client using the key from our environment variable
client = genai.Client(
    api_key=my_api_key,
)

# create database to store all places 

# initialize database
def create_places_database():
    conn = sqlite3.connect('travel.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS places
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  destination TEXT,
                  name TEXT,
                  address TEXT,
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

# store places function to put places into the databse we initialized
def store_places(destination, places_data, max_places=25):
    """Store places in database for future reference"""
    conn = sqlite3.connect('travel.db')
    c = conn.cursor()
    
    for place in places_data['features'][:max_places]: 
        c.execute('''INSERT INTO places 
                    (destination, name, address)
                    VALUES (?, ?, ?)''',
                (destination,
                 place['properties'].get('name', 'Unnamed location'),
                 place['properties'].get('formatted', 'Address not available')))
    
    conn.commit()
    conn.close()


def get_places(lat, lon, radius=5000, categories="tourism,entertainment"):
    # uses geoapify's places API to fetch places of interest from the tourism and entertainment categories
    base_url = "https://api.geoapify.com/v2/places"

    params = {
        'categories': categories,
        # search within radius of 5000 meters
        'filter': f'circle:{lon},{lat},{radius}', 
        'limit': 25,
        'apiKey': geoapify_key
    }


    response = requests.get(base_url, params=params)
    response.raise_for_status()
    data = response.json()
    
    if not data.get('features'):
        return "No notable tourist spots found nearby."
            
    places_info = []
    for place in data['features'=][:5]:
        name = place['properties'].get('name', 'Unnamed location')
        categories = ", ".join(place['properties'].get('categories', []))
        address = place['properties'].get('formatted', 'Address not available')
        places_info.append(f"- {name}: {address}")
    store_places(f"{lat},{lon}", data)
        
    return "\n".join(places_info)

# call database when func starts
create_places_database()

# Get user input from terminal
user_query = input("Please enter details about your dream travel destination!\nFeel free to include: \n-Budget \n-Where you are traveling from + Max distance \n-Interests (beaches, hiking, trying new foods)\n")

# Specify the model to use and the messages to send
response = client.models.generate_content(
    model="gemini-2.5-flash",
    config=types.GenerateContentConfig(
      system_instruction="You are a travel agent. Recommend a destination and provide:\n. First line: DESTINATION_NAME\n. Second line: LATITUDE,LONGITUDE without any symbols\n. Followed by a brief description and cost breakdown."
    ),
    contents=user_query,
)

# prints the AI generated response
print("\nResponse:")
print(response.text)



#extract coordinates (assuming that the Google AI returns the format LATITUDE,LONGITUDE in second line)
lines = response.text.split('\n')
destination = lines[0].strip()
lat, lon = map(float, lines[1].strip().split(','))
print(f"\nTop Tourist/Entertainment Spots in {destination}:")
places_info = get_places(lat, lon)
print(places_info)