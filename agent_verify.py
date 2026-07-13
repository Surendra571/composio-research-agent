import json
import os
import time
from google import genai
from google.genai import types

client = genai.Client(api_key="YOUR_ACTUAL_GEMINI_API_KEY")

def verify_and_correct(app_data):
    print(f"🔍 [Stage 2] Programmatic QA Verification for {app_data['name']}...")
    
    prompt = f"""
    You are a Quality Assurance Agent verifying AI agent toolkit integration data.
    Review this extracted profile data for accuracy based on official developer specifications:
    {json.dumps(app_data)}
    
    Return a strict JSON object with two fields:
    1. "is_accurate": true/false
    2. "corrected_data": (If false, provide the updated fields in the original dictionary layout. If true, return the input dictionary).
    """

    response = client.models.generate_content(
        model='gemini-3.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.1
        ),
    )
    
    return json.loads(response.text)

def main():
    if not os.path.exists("data/research_results.json"):
        print("Error: data/research_results.json does not exist! Run agent_research.py first.")
        return
        
    with open("data/research_results.json", "r") as f:
        research_data = json.load(f)
    
    verified_data = []
    
    for app in research_data:
        if not app or "name" not in app:
            continue
            
        try:
            verification = verify_and_correct(app)
            if not verification.get("is_accurate", True):
                print(f"⚠️ Correction applied for {app['name']}!")
                verified_data.append(verification["corrected_data"])
            else:
                print(f"✅ {app['name']} is verified accurate.")
                verified_data.append(app)
            
            # Wait 4 seconds between verifications to stay under rate limits
            time.sleep(4)
        except Exception as e:
            print(f"Error verifying {app['name']}: {e}")
            verified_data.append(app)
            time.sleep(4)
            
    with open("data/verified_results.json", "w") as f:
        json.dump(verified_data, f, indent=2)
    print("Step 2 Complete! Polished data saved to data/verified_results.json")

if __name__ == "__main__":
    main()