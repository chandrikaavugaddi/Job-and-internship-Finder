import os
from dotenv import load_dotenv
import json
import re
import time
import uuid
from datetime import datetime
import pymongo
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from tenacity import retry, stop_after_attempt, wait_exponential
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc

from config import *

load_dotenv()

class JobAggregator:
    def __init__(self):
        self.mongo_uri = os.getenv('MONGODB_URI', MONGODB_URI)
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client["careerhub"]
        self.jobs = self.db["jobs"]
        self.jobs.create_index("applicationLink", unique=True)
        self.jobs.create_index("branch")
        self.session = requests.Session()
        retry_strategy = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        self.session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'})
        self.scraped_count = 0

    def _is_valid_title(self, title):
        if not title or len(title.strip()) < 10 or not isinstance(title, str):
            return False
        title_lower = title.lower()
        # Strict exclude
        if any(re.search(pat, title_lower) for pat in EXCLUDE_KEYWORDS):
            return False
        # Require student keywords
        student_keywords = ['fresher', 'entry level', 'intern', 'trainee', '2026', 'final year', 'graduating batch']
        has_student = any(kw in title_lower for kw in student_keywords)
        return has_student

    def _classify_branch(self, title):
        title_lower = title.lower()
        for dept, pat in BRANCH_PATTERNS.items():
            if re.search(pat, title_lower, re.IGNORECASE):
                return dept
        return None  # Skip misclassified

    def _get_type_and_year(self, title, duration=None):
        title_lower = title.lower()
        is_intern_kw = ['intern', 'trainee', 'stipend', 'apprenticeship', '6 months']
        duration_short = duration and (('month' in duration.lower() and int(duration.split()[0]) <= 6) if duration.isdigit() else False)
        if duration_short or any(kw in title_lower for kw in is_intern_kw):
            return "Internship", ["1st", "2nd", "3rd", "4th"]
        return "Job", ["4th Year", "2026 Graduating"]

    def _normalize_company(self, company):
        if company:
            return re.sub(r'\s+', ' ', company.strip()).title()
        return None

    def _upsert_job(self, job_doc):
        doc = {k: v for k, v in job_doc.items() if v}  # Remove None
        if not doc.get('title') or not doc.get('company') or not doc.get('applicationLink'):
            print("[-] Skip: Missing title/company/link")
            return False
        doc['scrapedAt'] = datetime.utcnow()
        try:
            result = self.jobs.update_one(
                {"applicationLink": doc['applicationLink']},
                {"$set": doc},
                upsert=True
            )
            if result.upserted_id:
                self.scraped_count += 1
                print(f"[+] {doc['branch']} | {doc['title'][:40]}... | {doc['company']}")
            return True
        except Exception as e:
            print(f"[-] DB upsert error: {e}")
            return False

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def _api_get(self, url):
        resp = self.session.get(url, timeout=10)
        resp.raise_for_status()
        if 'application/json' in resp.headers.get('content-type', ''):
            return resp.json()
        return resp

    def fetch_lever(self):
        print("[*] Fetching Lever ATS...")
        self.source = "Lever ATS"
        companies = [
            "stripe", "gusto", "helios", "hospitality", "postmates", "wework", "lattice", "vercel"
        ] * 3  # ~24 calls for volume
        for company in companies:
            url = f"https://api.lever.co/v0/postings/{company}"
            try:
                postings = self._api_get(url)
                if isinstance(postings, list):
                    for post in postings[:4]:
                        title = post.get('text', '') 
                        if self._is_valid_title(title):
                            branch = self._classify_branch(title)
                            if branch:
                                typ, year = self._get_type_and_year(title)
                                link = post.get('applyUrl') or post.get('hostedApplyUrl', '')
                                company_name = self._normalize_company(post.get('company', {}).get('name', company.title()))
                                doc = {
                                    "jobId": str(uuid.uuid4()),
                                    "title": title[:200],
                                    "company": company_name,
                                    "location": post.get('categories', {}).get('Location', 'India'),
                                    "applicationLink": link,
                                    "type": typ,
                                    "branch": branch,
                                    "eligibleYear": year,
                                    "source": self.source
                                }
                                self._upsert_job(doc)
            except Exception as e:
                print(f"[-] Lever {company}: {str(e)[:50]}")
        print("[+] Lever complete.")

    def fetch_greenhouse(self):
        print("[*] Fetching Greenhouse ATS...")
        self.source = "Greenhouse ATS"
        companies = ["stripe", "gusto", "lattice", "helios", "abnormal"] * 4
        for company in companies:
            url = f"https://boards-api.greenhouse.io/v1/boards/{company}/jobs"
            try:
                jobs_data = self._api_get(url)
                jobs = jobs_data if isinstance(jobs_data, list) else jobs_data.get('jobs', [])
                for job in jobs[:4]:
                    title = job.get('title', '')
                    if self._is_valid_title(title):
                        branch = self._classify_branch(title)
                        if branch:
                            typ, year = self._get_type_and_year(title)
                            link = job.get('absolute_url', '')
                            company_name = self._normalize_company(job.get('organization') or company.title())
                            doc = {
                                "jobId": str(uuid.uuid4()),
                                "title": title,
                                "company": company_name,
                                "location": job.get('location', {}).get('name', 'India'),
                                "applicationLink": link,
                                "type": typ,
                                "branch": branch,
                                "eligibleYear": year,
                                "source": self.source
                            }
                            self._upsert_job(doc)
            except Exception as e:
                print(f"[-] Greenhouse {company}: {str(e)[:50]}")
        print("[+] Greenhouse complete.")

    def fetch_smartrecruiters(self):
        print("[*] Fetching SmartRecruiters...")
        self.source = "SmartRecruiters"
        companies = ["accenture", "bosch"]  # Limited public, CSE/EEE
        for company in companies:
            url = f"https://jobs.smartrecruiters.com/{company}/search"
            try:
                resp = self.session.get(url, timeout=10)
                soup = BeautifulSoup(resp.text, 'lxml')
                links = soup.select('a[href*="/job/"]')[:10]
                for a in links:
                    title = a.text.strip()
                    link = 'https://jobs.smartrecruiters.com' + a['href'] if a['href'].startswith('/') else a['href']
                    if self._is_valid_title(title) and link:
                        branch = self._classify_branch(title)
                        if branch:
                            typ, year = self._get_type_and_year(title)
                            doc = {
                                "jobId": str(uuid.uuid4()),
                                "title": title,
                                "company": company.title(),
                                "location": "India",
                                "applicationLink": link,
                                "type": typ,
                                "branch": branch,
                                "eligibleYear": year,
                                "source": self.source
                            }
                            self._upsert_job(doc)
            except Exception as e:
                print(f"[-] SmartRecruiters {company}: {e}")
        print("[+] SmartRecruiters complete.")

    def fetch_adzuna(self):
        print("[*] Fetching Adzuna API...")
        self.source = "Adzuna"
        app_id = os.getenv('ADZUNA_APP_ID', 'cc210008')
        app_key = os.getenv('ADZUNA_APP_KEY', '4104b85e9edf66c02a3207b1627a399b')
        dept_queries = {
            "CSE/IT": ["software developer fresher", "sde intern", "data analyst entry level"],
            "ECE": ["embedded engineer intern", "electronics fresher"],
            "EEE": ["electrical engineer fresher", "power electronics intern"],
            "Mechanical": ["mechanical engineer intern", "cad design fresher"],
            "Civil": ["civil engineer intern", "structural fresher"]
        }
        for branch, queries in dept_queries.items():
            for q in queries:
                url = f"https://api.adzuna.com/v1/api/jobs/in/search/1?app_id={app_id}&app_key={app_key}&what={q}&results_per_page=20"
                try:
                    data = self._api_get(url)
                    for item in data.get('results', [])[:8]:
                        title = item['title']
                        if self._is_valid_title(title):
                            classified = self._classify_branch(title)
                            if classified == branch:
                                typ, year = self._get_type_and_year(title)
                                link = item['redirect_url']
                                doc = {
                                    "jobId": str(uuid.uuid4()),
                                    "title": title,
                                    "company": self._normalize_company(item['company']['display_name']),
                                    "location": item['location']['display_name'],
                                    "applicationLink": link,
                                    "type": typ,
                                    "branch": branch,
                                    "eligibleYear": year,
                                    "source": self.source
                                }
                                self._upsert_job(doc)
                except Exception as e:
                    print(f"[-] Adzuna {q}: {e}")
        print("[+] Adzuna complete.")

    def fetch_government(self):
        print("[*] Fetching Government sources...")
        self.source = "Government"
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        driver = webdriver.Chrome(options=options)
        portals = [
            {"name": "AICTE", "url": "https://internship.aicte-india.org/recentlyposted.php", "sel": ".internship-card"},
            {"name": "NATS", "url": "http://www.nats.education.gov.in/notifications.php", "sel": ".news-item"}
        ]
        for portal in portals:
            try:
                driver.get(portal['url'])
                time.sleep(5)
                elements = driver.find_elements(By.CSS_SELECTOR, portal['sel'])
                for el in elements:
                    title = el.text.strip()[:200]
                    links = el.find_elements(By.TAG_NAME, "a")
                    if links:
                        link = links[0].get_attribute('href') or ''
                        if self._is_valid_title(title) and link:
                            branch = self._classify_branch(title)
                            if branch:
                                typ, year = self._get_type_and_year(title)
                                doc = {
                                    "jobId": str(uuid.uuid4()),
                                    "title": title,
                                    "company": f"Govt of India - {portal['name']}",
                                    "location": "India",
                                    "applicationLink": link,
                                    "type": typ,
                                    "branch": branch,
                                    "eligibleYear": year,
                                    "source": self.source
                                }
                                self._upsert_job(doc)
            except Exception as e:
                print(f"[-] Govt {portal['name']}: {e}")
        driver.quit()
        print("[+] Government complete.")

    def fetch_company_pages(self):
        print("[*] Fetching Company Career Pages...")
        self.source = "Company Career Pages"
        targets = [
            ("Amazon University", "https://www.amazon.jobs/en/business_categories/university-recruiting", "a.job-link"),
            ("Google Careers", "https://www.google.com/about/careers/applications/jobs/results/?q=fresher", "li[data-ocid]"),
            ("Microsoft Graduate", "https://careers.microsoft.com/v2/global/en/graduate.html", "div.job-tile a"),
            ("Intel Internships", "https://intel.wd1.myworkdayjobs.com/External?q=intern", "a[data-automation-id='jobTitle']"),
            ("Qualcomm Careers", "https://www.qualcomm.com/company/careers/internships", "div.job-title a"),
            ("ABB Graduate", "https://careers.abb/global/en/search-results?keywords=graduate", "div.job-title a"),  # EEE
            ("Siemens Intern", "https://jobs.siemens.com/careers?query=intern", "a.job-title"),  # EEE
            ("Tata Motors", "https://careers.tatamotors.com/", "a[href*='job']"),  # Mech
            ("L&T Construction", "https://www.larsentoubro.com/careers/", "div.job-card a"),  # Civil/Mech
            ("TCS iON", "https://www.tcsion.com/hub/national-qualifier-test/", "a.cta-button")  # CSE
        ]
        options = uc.ChromeOptions()
        options.add_argument("--headless")
        driver = uc.Chrome(options=options)
        for company, url, selector in targets:
            try:
                driver.get(url)
                WebDriverWait(driver, 10).until(EC.any_of(EC.presence_of_element_located((By.TAG_NAME, "body")), EC.presence_of_element_located((By.CSS_SELECTOR, selector))))
                time.sleep(3)
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for e in elements[:8]:
                    title = e.text.strip()
                    link = e.get_attribute("href")
                    if self._is_valid_title(title) and link:
                        branch = self._classify_branch(title)
                        if branch:
                            typ, year = self._get_type_and_year(title)
                            doc = {
                                "jobId": str(uuid.uuid4()),
                                "title": title,
                                "company": company,
                                "location": "India",
                                "applicationLink": link,
                                "type": typ,
                                "branch": branch,
                                "eligibleYear": year,
                                "source": self.source
                            }
                            self._upsert_job(doc)
            except Exception as e:
                print(f"[-] Company {company}: {e}")
        driver.quit()
        print("[+] Company pages complete.")

    def run_all(self):
        print("🚀 Production Job Aggregation System - B.Tech 2026 Batch")
        print(f"DB: {self.mongo_uri}")
        methods = [
            self.fetch_lever, self.fetch_greenhouse, self.fetch_smartrecruiters,
            self.fetch_adzuna, self.fetch_government, self.fetch_company_pages
        ]
        for method in methods:
            method()
        print(f"\n✅ Session complete. Total new/updated jobs: {self.scraped_count}")
        # Final stats
        pipeline = [
            {"$match": {"branch": {"$in": ["CSE/IT", "ECE", "EEE", "Mechanical", "Civil"]}}},
            {"$group": {"_id": "$branch", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        stats = list(self.jobs.aggregate(pipeline))
        print("Jobs per department:")
        for s in stats:
            print(f"  {s['_id']}: {s['count']}")
        if any(s['count'] < 20 for s in stats):
            print("⚠️  Some departments <20 jobs - re-run or expand queries.")
        self.client.close()

if __name__ == "__main__":
    aggregator = JobAggregator()
    aggregator.run_all()

