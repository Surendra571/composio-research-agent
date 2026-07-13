import json
import os
import time
from google import genai
from google.genai import types
from pydantic import BaseModel
from typing import Literal

# Define the exact output structure needed for the dashboard matrix
class AppResearchSchema(BaseModel):
    id: int
    name: str
    category: str
    description: str
    auth_method: str
    access_model: Literal["Self-serve", "Gated"]
    api_surface: str
    buildability_verdict: str
    docs_url: str

# Directly initialize the client with your key to prevent environment variable issues
client = genai.Client(api_key="YOUR_ACTUAL_GEMINI_API_KEY")

def research_app(app):
    print(f"🚀 [Stage 1] Researching {app['name']}...")
    
    prompt = f"""
    Research the app '{app['name']}' ({app['hint_url']}) in the category '{app['category']}'.
    Find the developer docs and extract structural information about their API surface, auth methods, and access models.
    """

    response = client.models.generate_content(
        model='gemini-3.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=AppResearchSchema,
            temperature=0.1
        ),
    )
    
    data = json.loads(response.text)
    data['id'] = app['id']
    return data

def main():
    if not os.path.exists("data/apps_list.json"):
        print("Error: data/apps_list.json not found! Please create it first.")
        return

    with open("data/apps_list.json", "r") as f:
        apps = json.load(f)
    
    results = []
    for app in apps:
        try:
            data = research_app(app)
            results.append(data)
            # Add a 4-second delay to respect the free tier rate limits
            print("Waiting 4 seconds to respect rate limits...")
            time.sleep(4)
        except Exception as e:
            print(f"Error processing {app['name']}: {e}")
            time.sleep(4)
        
    os.makedirs("data", exist_ok=True)
    with open("data/research_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("Step 1 Complete! Raw data saved to data/research_results.json")

if __name__ == "__main__":
    main()