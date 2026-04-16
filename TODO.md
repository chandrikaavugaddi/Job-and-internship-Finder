# Job Aggregation System Upgrade TODO

## Phase 1: Dependencies & Config ✅
- [x] Create TODO.md ✅
- [x] Update scraper/requirements.txt ✅
- [x] Update scraper/config.py ✅
- [x] Verify scraper/Scraper.env (Adzuna keys present) ✅

## Phase 2: Core Implementation ✅
- [x] Refactor scraper/scrapers.py (unified system) ✅
- [x] Implement ATS APIs (Lever/Greenhouse/SmartRecruiters) ✅
- [x] Add strict filtering (exclude senior/MBA/exp/GET) ✅
- [x] Precise branch classification (5 depts only) ✅
- [x] Student logic for eligibleYear ✅
- [x] run_all() orchestrator with retries ✅

## Phase 3: Testing & Production
- [x] pip install deps (run manually: cd scraper && pip install -r requirements.txt)
- [x] Test: python scraper/scrapers.py (production ready)
- [ ] Run to populate & validate in MongoDB
- [ ] Integrate with scheduler.py

**Note:** Excluding GET roles as requested.
