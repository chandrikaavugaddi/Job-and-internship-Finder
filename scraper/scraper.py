"""import uuid
import time
import requests
import pymongo
from datetime import datetime

from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# ---------------- DATABASE ----------------

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["careerhub"]
jobs = db["jobs"]

indexes = jobs.index_information()

if "applicationLink_1" not in indexes:
    jobs.create_index(
        [("applicationLink", 1)],
        unique=True,
        sparse=True
    )

# ---------------- DRIVER ----------------

def create_driver():

    options = webdriver.ChromeOptions()

    options.add_argument("--headless")
    options.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    return driver


# ---------------- SAVE FUNCTION ----------------

def save_job(title, company, link, source):

    if jobs.find_one({"applicationLink": link}):
        return

    if "intern" in title.lower():
        job_type = "internship"
    else:
        job_type = "job"

    category = "government" if "gov" in source.lower() else "private"

    doc = {

        "jobId": str(uuid.uuid4()),
        "title": title,
        "company": company,
        "applicationLink": link,
        "type": job_type,
        "category": category,
        "source": source,
        "scrapedAt": datetime.now()

    }

    jobs.insert_one(doc)

    print("Saved:", title)


# ---------------- LINKEDIN SCRAPER ----------------

def scrape_linkedin():

    driver = create_driver()

    url = "https://www.linkedin.com/jobs/search/?keywords=software%20engineer&location=India"

    driver.get(url)

    time.sleep(5)

    soup = BeautifulSoup(driver.page_source,"html.parser")

    cards = soup.select(".base-card")

    for c in cards:

        try:

            title = c.select_one(".base-search-card__title").text.strip()
            company = c.select_one(".base-search-card__subtitle").text.strip()
            link = c.find("a")["href"]

            save_job(title,company,link,"LinkedIn")

        except:
            pass

    driver.quit()


# ---------------- INTERNSHALA SCRAPER ----------------

def scrape_internshala():

    url = "https://internshala.com/internships/computer-science-internship"

    res = requests.get(url,headers={"User-Agent":"Mozilla/5.0"})

    soup = BeautifulSoup(res.text,"html.parser")

    cards = soup.select(".individual_internship")

    for c in cards:

        try:

            title = c.select_one(".job-internship-name").text.strip()
            company = c.select_one(".company-name").text.strip()

            link = "https://internshala.com" + c.find("a")["href"]

            save_job(title,company,link,"Internshala")

        except:
            pass


# ---------------- AICTE GOVT SCRAPER ----------------

def scrape_aicte():

    url = "https://internship.aicte-india.org/"

    res = requests.get(url)

    soup = BeautifulSoup(res.text,"html.parser")

    links = soup.find_all("a")

    for l in links:

        text = l.text.strip()
        href = l.get("href")

        if not href:
            continue

        if "intern" in text.lower():

            save_job(
                text,
                "Govt of India",
                href,
                "AICTE"
            )


# ---------------- COMPANY PORTAL SCRAPER ----------------

def scrape_company_portals():

    companies = {

        "Google":"https://careers.google.com/jobs/results/",
        "Amazon":"https://www.amazon.jobs",
        "Microsoft":"https://careers.microsoft.com"
    }

    for company,url in companies.items():

        res = requests.get(url,headers={"User-Agent":"Mozilla/5.0"})

        soup = BeautifulSoup(res.text,"html.parser")

        links = soup.find_all("a")

        for l in links:

            text = l.text.strip()
            href = l.get("href")

            if not href:
                continue

            if "engineer" in text.lower() or "developer" in text.lower():

                save_job(text,company,href,company)


# ---------------- MAIN ----------------

def main():

    print("Scraping Internshala...")
    scrape_internshala()

    print("Scraping LinkedIn...")
    scrape_linkedin()

    print("Scraping AICTE...")
    scrape_aicte()

    print("Scraping Company Portals...")
    scrape_company_portals()

    print("Total Jobs:",jobs.count_documents({}))


if __name__ == "__main__":

    main()




import time
import uuid
import re
import random
from datetime import datetime, timedelta

import pymongo
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium_stealth import stealth
from webdriver_manager.chrome import ChromeDriverManager

# ================= DATABASE CONFIG =================
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["careerhub"]
jobs_col = db["jobs"]

# ================= FILTERS & RULES =================
# Targets roles students can actually apply for
ROLE_WHITELIST = [
    "engineer", "developer", "analyst", "intern", "trainee", 
    "sde", "frontend", "backend", "fullstack", "data science"
]
JUNK_BLACKLIST = [
    "news", "alert", "summit", "hackathon", "dividend", "feedback", 
    "disclaimer", "legal", "policy", "webinar", "course", "training", "vlog"
]
STOP_WORDS = ["Engineer", "Developer", "Intern", "Analyst", "Lead", "Architect", "Specialist"]

class FinalScraper:
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        
        # Mimic a high-authority browser
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
        
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), 
            options=chrome_options
        )
        
        # Apply Stealth to bypass LinkedIn/Internshala bot detection
        stealth(self.driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
        )

    def clean_title(self, title):
        """'''Removes noise from job titles.'''"""
        for sep in [" - ", " | ", "(", ","]:
            if sep in title: title = title.split(sep)[0]
        for word in STOP_WORDS:
            match = re.search(rf"\b{word}\b", title, re.IGNORECASE)
            if match: return title[:match.end()].strip()
        return title.strip()

    def is_valid_it_job(self, title, link):
       """'''Checks if the link is a real technical job for students.'''"""
        if not title or not link or len(title) < 5:
            return False
            
        t_lower, l_lower = title.lower(), link.lower()
        has_role = any(role in t_lower for role in ROLE_WHITELIST)
        has_junk = any(junk in t_lower or junk in l_lower for junk in JUNK_BLACKLIST)
        
        return has_role and not has_junk

    def scrape_site(self, company, url):
        print(f"[*] Crawling {company}...")
        count = 0
        try:
            self.driver.get(url)
            # Give time for heavy JS sites (Google/Microsoft) to render
            time.sleep(random.uniform(7, 10)) 
            
            # Simple scroll to trigger lazy-loaded cards
            self.driver.execute_script("window.scrollTo(0, 500);")
            
            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            
            for a in soup.find_all("a", href=True):
                raw_text = a.get_text().strip()
                link = a['href']

                # CRITICAL: Ignore null/invalid links that cause DB errors
                if not link or link.startswith("#") or "javascript" in link:
                    continue

                if link.startswith("/"):
                    base = "/".join(url.split("/")[:3])
                    link = base + link

                if self.is_valid_it_job(raw_text, link):
                    final_title = self.clean_title(raw_text)
                    t_l = final_title.lower()
                    
                    # Student Classification
                    job_type = "Internship" if "intern" in t_l or "trainee" in t_l else "Fulltime"
                    
                    # Branch Logic
                    if any(x in t_l for x in ["software", "developer", "sde", "frontend", "backend"]):
                        branches = ["CSE", "IT", "ECE"]
                    elif any(x in t_l for x in ["data", "analyst", "python"]):
                        branches = ["CSE", "IT", "EEE"]
                    else:
                        branches = ["CSE", "IT", "ECE", "EEE", "MECH", "CIVIL"]

                    job_doc = {
                        "jobId": str(uuid.uuid4()),
                        "companyName": company,
                        "jobTitle": final_title,
                        "branch": branches,
                        "jobType": job_type,
                        "eligibleYear": ["2nd", "3rd", "4th"] if job_type == "Internship" else ["4th"],
                        "location": "India/Remote",
                        "applicationLink": link,  # Matches your unique index
                        "sourceWebsite": company,
                        "postedDate": datetime.now(),
                        "expiryDate": datetime.now() + timedelta(days=30)
                    }

                    # Upsert: Prevents duplicates based on the link
                    res = jobs_col.update_one(
                        {"applicationLink": link}, 
                        {"$setOnInsert": job_doc}, 
                        upsert=True
                    )
                    if res.upserted_id:
                        count += 1
            return count
        except Exception as e:
            print(f"[-] Error at {company}: {e}")
            return 0

    def run(self):
        # Targets focused on Paid Jobs and Student Internships
        targets = [
            ("Unstop", "https://unstop.com/internships?term=internship&status=open"),
            ("Internshala", "https://internshala.com/internships/engineering-internship"),
            ("AICTE", "https://internship.aicte-india.org/internship_search.php"),
            ("Amazon_Student", "https://www.amazon.jobs/en/teams/university-recruiting"),
            ("Cisco_Student", "https://jobs.cisco.com/jobs/SearchJobs/?21181=%5B169482%5D&21181_format=1505"),
            ("Google_India", "https://www.google.com/about/careers/applications/jobs/results/?location=India"),
            ("TCS_NextStep", "https://www.tcs.com/careers/india"),
            ("LinkedIn_Intern", "https://www.linkedin.com/jobs/search/?keywords=Software%20Engineer%20Intern&location=India")
        ]

        # First, clean up any 'None' links that might have crashed the DB before
        jobs_col.delete_many({"applicationLink": None})
        print("[!] Database sanitized (Removed null links).")

        for company, url in targets:
            found = self.scrape_site(company, url)
            print(f"[+] {company}: {found} new records stored.")

        self.driver.quit()
        self.cleanup_db()

    def cleanup_db(self):
        """'''Removes expired jobs automatically.'''"""
        res = jobs_col.delete_many({"expiryDate": {"$lt": datetime.now()}})
        print(f"[!] Cleanup: Removed {res.deleted_count} expired records.")

if __name__ == "__main__":
    FinalScraper().run()"""
"""APP_ID = "cc210008"
APP_KEY = "4104b85e9edf66c02a3207b1627a399b" """



import time
import uuid
import re
import requests
import pymongo
import undetected_chromedriver as uc
from datetime import datetime
from selenium.webdriver.common.by import By

# ================= DATABASE CONFIG =================
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["careerhub"]
jobs_col = db["jobs"]

# ================= FILTERS (2026-2029) =================
JUNK_KEYWORDS = [
    "senior", "sr.", "lead", "manager", "head", "principal", 
    "years exp", "architect", "expert", "2025 batch", "2024 batch", 
    "class of 2025", "immediate joiner", "sales", "hr"
]

BRANCH_RULES = {
    "CSE/IT": r"(software|developer|python|java|web|computer|it|data|ai|ml|fullstack|node|react)",
    "ECE": r"(electronics|embedded|vlsi|communication|signal|ece|hardware|microcontroller|semiconductor)",
    "EEE": r"(electrical|power|grid|circuit|eee|control system|transformer|renewable)",
    "Mechanical": r"(mechanical|manufacturing|cad|solidworks|thermal|production|mech|auto)",
    "Civil": r"(civil|construction|structural|site engineer|infra)"
}

class CareerHubFinal:
    def __init__(self):
        self.adzuna_id = "cc210008"
        self.adzuna_key = "4104b85e9edf66c02a3207b1627a399b"
        options = uc.ChromeOptions()
        options.add_argument("--headless")
        self.driver = uc.Chrome(options=options, version_main=145)

    def get_metadata(self, title):
        title_lower = title.lower()
        if any(word in title_lower for word in JUNK_KEYWORDS):
            return None 

        branches = [b for b, pattern in BRANCH_RULES.items() if re.search(pattern, title_lower)]
        if not branches: branches = ["General Engineering"]
        
        is_intern = any(x in title_lower for x in ["intern", "trainee", "stipend", "apprentice"])
        j_type = "Internship" if is_intern else "Full-time Job"
        years = ["1st", "2nd", "3rd", "4th"] if is_intern else ["4th (2026 Batch)"]
            
        return branches, j_type, years

    def save_job(self, doc):
        # PREVENT E11000: Skip if link is missing
        if not doc.get("applyLink"):
            return

        try:
            # Use 'applyLink' consistently
            jobs_col.update_one(
                {"applyLink": doc["applyLink"]}, 
                {"$set": doc}, 
                upsert=True
            )
            print(f"[+] Saved: {doc['jobTitle'][:30]}...")
        except Exception as e:
            print(f"[-] MongoDB Error: {e}")

    def sync_adzuna(self):
        print("[*] Syncing Adzuna API...")
        queries = ["Software Engineer Fresher", "Graduate Engineer Trainee", "ECE Intern", "Electrical Graduate"]
        for q in queries:
            url = f"https://api.adzuna.com/v1/api/jobs/in/search/1?app_id={self.adzuna_id}&app_key={self.adzuna_key}&results_per_page=50&what={q}"
            try:
                data = requests.get(url).json()
                for item in data.get('results', []):
                    meta = self.get_metadata(item['title'])
                    if meta:
                        branches, j_type, years = meta
                        doc = {
                            "jobId": str(uuid.uuid4()),
                            "jobTitle": item['title'],
                            "companyName": item['company'].get('display_name', 'MNC'),
                            "location": item['location'].get('display_name', 'India'),
                            "applyLink": item['redirect_url'], # Standardized field name
                            "jobType": j_type,
                            "branch": branches,
                            "eligibleYear": years,
                            "syncedAt": datetime.utcnow()
                        }
                        self.save_job(doc)
            except Exception as e: print(f"API Error: {e}")

    def scrape_mncs(self):
        print("[*] Syncing Direct MNCs...")
        self.driver.get("https://www.amazon.jobs/en/business_categories/university-recruiting")
        time.sleep(5)
        links = self.driver.find_elements(By.TAG_NAME, "a")
        for link in links[:15]:
            title = link.text
            href = link.get_attribute("href")
            if title and href and "job" in href:
                meta = self.get_metadata(title)
                if meta:
                    branches, j_type, years = meta
                    self.save_job({
                        "jobId": str(uuid.uuid4()),
                        "jobTitle": title,
                        "companyName": "Amazon",
                        "applyLink": href,
                        "jobType": j_type,
                        "branch": branches,
                        "eligibleYear": years,
                        "syncedAt": datetime.utcnow()
                    })

    def run(self):
        self.sync_adzuna()
        self.scrape_mncs()
        self.driver.quit()

if __name__ == "__main__":
    CareerHubFinal().run()