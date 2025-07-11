# Travel-Recommender
CLI based travel recommender created with Python using Google Gemini API and Geoapify Places API


### Features  
**Google AI-Powered Destination Suggestions** - Get personalized travel recommendations based on budget, interests, and preferences.  
**Nearby Tourist Spots** – Automatically fetches top attractions (tourism, entertainment) near the recommended location using Geoapify's Places API.  
**Database Storage** – Saves all attraction recommendations in a local SQLite database (travel.db) for easy access.  
**User-Friendly CLI-based Program** – Simple terminal interaction with option to view full recommendations. 






### Setup & Installation
#### Install required libraries
`pip install google-generativeai requests python-dotenv`


#### Get API Keys
[Google Gemini API](https://ai.google.dev/gemini-api/docs)   
[Geoapify Places API](https://apidocs.geoapify.com/docs/places/)


#### Create a .env file in the project directory
Put the following in the .env file:
```
API_KEY=your_google_gemini_api_key
GEOAPIFY_KEY=your_geoapify_api_key
```


#### Run the project
`python travel_recommendation.py`
