# Configuration for Job Scraper

# MongoDB Connection String
MONGODB_URI = "mongodb://localhost:27017/careerhub"

# API Keys (load from .env)
ADZUNA_APP_ID = ""
ADZUNA_APP_KEY = ""

# ATS Board IDs (public endpoints)
LEVER_COMPANIES = ["lever.co", "uselever.com"]  # Full list in code
GREENHOUSE_BOARDS = ["boards-api.greenhouse.io"]
SMARTRECRUITERS_COMPANIES = []

# Exclude Keywords (strict)
EXCLUDE_KEYWORDS = [
    r"senior|sr\.|lead|manager|director|principal|architect|expert",
    r"mba|management|marketing|sales|hr|finance",
    r"\d{1,} years? exp|\d{1,} years? experience",
    r"graduate engineer trainee|get|trainee engineer"
]

# Branch Classification (strict regex, avoid misclass)
BRANCH_PATTERNS = {
    "CSE/IT": r"(software|developer|sde|python|java|javascript|web|fullstack|backend|frontend|data|ai|ml|cloud|devops|cybersecurity)",
    "ECE": r"(electronics|embedded|vlsi|fpga|communication|rf|signal processing|microcontroller|arm|iot hardware)",
    "EEE": r"(electrical|power systems|renewables|control systems|electrical drives|power electronics|high voltage)",
    "Mechanical": r"(mechanical|automotive|cad|solidworks|ansys|thermal|manufacturing|production|mechatronics)",
    "Civil": r"(civil|structural|geotechnical|construction|transportation|water resources|earthquake|survey)"
}

# Include Keywords
INCLUDE_KEYWORDS = [
    r"fresher|entry level|2026 batch|final year|intern|trainee|graduate program"
]
# For MongoDB Atlas: mongodb+srv://username:password@cluster.mongodb.net/careerhub

# Company URLs to scrape (add more as needed)
COMPANY_URLS = [
    "https://careers.tcs.com/",
    "https://careers.infosys.com/",
    "https://www.wipro.com/careers/"
]

# Job Type Keywords
JOB_TYPES = {
    'internship': 'Internship',
    'intern': 'Internship',
    'graduate': 'Graduate Program',
    'full-time': 'Full-time',
    'contract': 'Contract'
}

# Eligible Year Keywords
ELIGIBLE_YEARS = {
    '1st': '1st Year',
    'first': '1st Year',
    '2nd': '2nd Year',
    'second': '2nd Year',
    '3rd': '3rd Year',
    'third': '3rd Year',
    '4th': '4th Year',
    'fourth': '4th Year',
    'final': '4th Year'
}
