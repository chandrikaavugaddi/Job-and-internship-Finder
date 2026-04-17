import time
import uuid
import requests
import pymongo
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

# ================= DATABASE =================
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["careerhub"]
jobs_col = db["jobs"]

# Ensure index (run once safely)
jobs_col.create_index("applyLink", unique=True, sparse=True)

# ================= FAST FILTER =================

def fast_filter(title):
    title = title.lower()

    reject_words = ["senior", "lead", "manager", "director", "head"]
    if any(word in title for word in reject_words):
        return False

    accept_words = [
        "intern", "trainee", "fresher",                                         
        "engineer", "developer", "analyst", "associate"
    ]
    return any(word in title for word in accept_words)

# ================= BRANCH DETECTION =================

def detect_branch(title):
    title = title.lower()

    if any(x in title for x in ["software", "developer", "data", "it", "web"]):
        return "CSE"
    elif "electrical" in title:
        return "EEE"
    elif "electronics" in title:
        return "ECE"
    elif "mechanical" in title:
        return "Mechanical"
    elif "civil" in title:
        return "Civil"
    else:
        return "General"

# ================= SAVE FUNCTION =================

def save_job(doc):
    link = doc.get("applyLink")
    if not link:*
        return

    try:
        jobs_col.update_one(
            {"applyLink": link},
            {"$setOnInsert": doc},
            upsert=True
        )
        print(f"[SAVED] {doc['jobTitle'][:60]}")
    except Exception as e:
        print(f"DB Error: {e}")

# ================= ADZUNA SCRAPER =================

ADZUNA_APP_ID = "cc210008"
ADZUNA_APP_KEY = "4104b85e9edf66c02a3207b1627a399b"

QUERIES = [
    "Software Engineer Intern",
    "Data Analyst Intern",
    "Frontend Developer",
    "Backend Developer",
    "Electrical Engineer",
    "Mechanical Engineer",
    "Civil Engineer"
]

def fetch_page(query, page):
    url = f"https://api.adzuna.com/v1/api/jobs/in/search/{page}?app_id={ADZUNA_APP_ID}&app_key={ADZUNA_APP_KEY}&results_per_page=20&what={query}"

    try:
        res = requests.get(url, timeout=10)
        data = res.json()

        for item in data.get("results", []):
            title = item.get("title", "")

            if not fast_filter(title):
                continue

            doc = {
                "jobId": str(uuid.uuid4()),
                "jobTitle": title,
                "companyName": item.get("company", {}).get("display_name", "Unknown"),
                "applyLink": item.get("redirect_url"),
                "jobType": "Internship" if "intern" in title.lower() else "Job",
                "branch": [detect_branch(title)],
                "eligibleYear": ["2026-2029"],
                "location": item.get("location", {}).get("display_name"),
                "salary": item.get("salary_max"),
                "syncedAt": datetime.utcnow()
            }

            save_job(doc)

    except Exception as e:
        print(f"Error (Page {page}): {e}")

# ================= MAIN RUNNER =================

def run_scraper():
    print("🚀 Starting High-Speed Job Scraper...")

    start = time.time()

    with ThreadPoolExecutor(max_workers=10) as executor:
        tasks = []

        for query in QUERIES:
            for page in range(1, 11):  # 🔥 10 pages per query
                tasks.append(executor.submit(fetch_page, query, page))

        for task in tasks:
            task.result()

    end = time.time()

    print(f"\n✅ Completed in {round(end - start, 2)} seconds")

# ================= RUN =================

if __name__ == "__main__":
    run_scraper()
