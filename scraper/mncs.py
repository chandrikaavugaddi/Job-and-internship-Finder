import time
import uuid
import requests
import pymongo
import json
from datetime import datetime
from google import genai
from pydantic import BaseModel
from typing import List

# ================= CONFIGURATION =================
# 1. MongoDB Setup
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["careerhub"]
jobs_col = db["jobs"]

# Ensure unique index on link to prevent duplicates
jobs_col.create_index("applyLink", unique=True)

# 2. Gemini API Setup (New v1 SDK)
# Replace with your actual key
GEMINI_API_KEY = "AIzaSyCBDB1VmIf0zaJzZ3tgmWnxy8W-HOU4FF4"
ai_client = genai.Client(api_key=GEMINI_API_KEY)

# 3. Adzuna API Setup
ADZUNA_ID = "cc210008"
ADZUNA_KEY = "4104b85e9edf66c02a3207b1627a399b"

# ================= DATA SCHEMAS =================
class JobResult(BaseModel):
    index: int
    eligible: bool
    branch: str  # e.g., CSE, ECE, Any
    type: str    # e.g., Internship, Full-time

class AIResponse(BaseModel):
    results: List[JobResult]

# ================= CORE LOGIC =================
class CareerHubModern:
    def __init__(self):
        self.raw_leads = []

    def fetch_adzuna_leads(self):
        """Gathers 200+ raw leads from Adzuna India"""
        print("[*] Connecting to Adzuna...")
        search_terms = ["Software", "Intern", "Developer", "Engineer"]
        
        for q in search_terms:
            url = "https://api.adzuna.com/v1/api/jobs/in/search/1"
            params = {
                "app_id": ADZUNA_ID, 
                "app_key": ADZUNA_KEY, 
                "results_per_page": 50, 
                "what": q
            }
            try:
                res = requests.get(url, params=params)
                if res.status_code == 200:
                    data = res.json().get('results', [])
                    for item in data:
                        self.raw_leads.append({
                            "title": item.get('title', 'N/A'),
                            "company": item.get('company', {}).get('display_name', 'MNC'),
                            "link": item.get('redirect_url'),
                            "loc": item.get('location', {}).get('display_name', 'India')
                        })
            except Exception as e:
                print(f"[-] Fetch error: {e}")

        # Remove duplicates
        seen = set()
        self.raw_leads = [x for x in self.raw_leads if not (x['link'] in seen or seen.add(x['link']))]
        print(f"[+] Total unique leads found: {len(self.raw_leads)}")

    def filter_with_ai(self, job_batch):
        """Uses Gemini to filter jobs for the 2026-2029 batch"""
        titles_text = "\n".join([f"{i}: {j['title']}" for i, j in enumerate(job_batch)])
        
        prompt = f"""
        Analyze these job titles for college students (2026-2029 graduates).
        REJECT: Senior, Lead, Manager, GET (Graduate Trainee), 2024/2025 batch.
        ACCEPT: Internships (2026-2029) and Fresher/Entry-level (2026 only).
        
        LIST:
        {titles_text}
        """

        try:
            response = ai_client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt,
                config={
                    'response_mime_type': 'application/json',
                    'response_schema': AIResponse,
                }
            )
            # The .parsed attribute automatically validates the JSON against our Pydantic class
            return response.parsed.results
        except Exception as e:
            if "429" in str(e):
                print("[!] Rate Limit Hit. Sleeping 60s...")
                time.sleep(60)
            else:
                print(f"[-] AI Error: {e}")
            return []

    def run(self):
        self.fetch_adzuna_leads()
        if not self.raw_leads:
            print("[ERROR] No leads found. Check Adzuna API Keys.")
            return

        # Small batches of 10 to stay under Free Tier Token-Per-Minute limits
        batch_size = 10
        total_saved = 0

        for i in range(0, len(self.raw_leads), batch_size):
            batch = self.raw_leads[i:i+batch_size]
            print(f"[*] Processing batch {i//batch_size + 1}...")
            
            ai_data = self.filter_with_ai(batch)
            
            if not ai_data:
                continue

            for res in ai_data:
                if res.eligible and res.index < len(batch):
                    target = batch[res.index]
                    doc = {
                        "jobId": str(uuid.uuid4()),
                        "jobTitle": target['title'],
                        "companyName": target['company'],
                        "applyLink": target['link'],
                        "location": target['loc'],
                        "jobType": res.type,
                        "branch": [res.branch],
                        "eligibleYear": ["2026-2029"],
                        "syncedAt": datetime.utcnow()
                    }
                    try:
                        # Update if exists, insert if new
                        jobs_col.update_one({"applyLink": doc["applyLink"]}, {"$set": doc}, upsert=True)
                        total_saved += 1
                    except Exception as e:
                        print(f"[-] DB Error: {e}")

            # Mandatory 10-second cooldown for Free Tier stability
            time.sleep(10)

        print(f"\n[SUCCESS] Pipeline complete. Saved {total_saved} valid jobs to 'careerhub.jobs'.")

if __name__ == "__main__":
    CareerHubModern().run()