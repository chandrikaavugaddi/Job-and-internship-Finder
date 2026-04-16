import schedule
import time
from scraper import JobScraper

def job():
    print("Running scheduled scraping...")
    scraper = JobScraper()
    scraper.run()

schedule.every(1).hours.do(job)

print("Scheduler started...")

while True:
    schedule.run_pending()
    time.sleep(60)
