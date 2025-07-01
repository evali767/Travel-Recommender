import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
load_dotenv()

# Set environment variables
my_api_key = os.getenv('API_KEY')

genai.api_key = my_api_key

# Create a genAI client using the key from our environment variable
client = genai.Client(
    api_key=my_api_key,
)

# Get user input from terminal
user_query = input("Please enter details about your dream travel destination!\n Feel free to include: \n-Budget \n-Where you are travelling from + Max distance \n-Interests (beaches, hiking, trying new foods)\n")

# Specify the model to use and the messages to send
response = client.models.generate_content(
    model="gemini-2.5-flash",
    config=types.GenerateContentConfig(
      system_instruction="You are a travel agent and can help the user choose their dream travel destination. Return a destination for the traveller as well as one to two sentences about the destination. Also include an outline of costs."
    ),
    contents=user_query,
)

# prints the AI generated response
print("\nResponse:")
print(response.text)