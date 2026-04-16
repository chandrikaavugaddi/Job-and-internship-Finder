## Overview

CareerHub is a web-based platform designed exclusively for B.Tech students to view internship and job opportunities without requiring login or registration. The system automatically collects opportunities from public company career websites and displays them in a clean, student-focused interface.

## Features

- **Academic Year Selection**: Choose 1st/2nd/3rd year for internships, 4th year for jobs + internships
- **Company-Based Search**: Search jobs by company name with partial match support
- **Automated Job Aggregation**: Scheduled scraping from public career pages
- **No Authentication**: No signup/login required
- **Responsive UI**: Clean and beginner-friendly interface

## Tech Stack

- **Frontend**: React.js
- **Backend**: Node.js + Express.js
- **Database**: MongoDB
- **Scraper**: Python (BeautifulSoup, Requests)
- **Scheduler**: Node.js (node-schedule)

## Project Structure

```
careerhub/
├── backend/                 # Node.js/Express API
│   ├── models/             # MongoDB schemas
│   ├── routes/             # API endpoints
│   ├── config/             # Database configuration
│   ├── server.js           # Main server file
│   └── package.json
├── frontend/                # React application
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── services/       # API service functions
│   │   └── App.js          # Main app component
│   ├── public/
│   └── package.json
├── scraper/                 # Python web scraper
│   ├── scraper.py          # Main scraping logic
│   ├── config.py           # Scraper configuration
│   └── requirements.txt
├── .env.example            # Environment variables template
├── docker-compose.yml      # Docker setup for local development
└── README.md
```

## Getting Started

### Prerequisites

- Node.js (v16 or higher)
- Python (v3.8 or higher)
- MongoDB (local or Atlas)
- npm or yarn

### Quick Start (Automated)

**For Windows:**
```bash
# Double-click run.bat or run in command prompt
run.bat
```

**For Linux/Mac:**
```bash
# Make script executable and run
chmod +x run.sh
./run.sh
```

The automated script will:
- Install all dependencies (backend, frontend, scraper)
- Set up environment variables
- Start MongoDB service (if local)
- Run scraper to populate database
- Start backend and frontend servers
- Open browser windows automatically

### Manual Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd careerhub
   ```

2. **Backend Setup**
   ```bash
   cd backend
   npm install
   cp ../.env.example .env  # Configure your MongoDB URI
   npm run dev
   ```

3. **Frontend Setup**
   ```bash
   cd ../frontend
   npm install
   npm start
   ```

4. **Scraper Setup**
   ```bash
   cd ../scraper
   pip install -r requirements.txt
   python scraper.py
   ```

### Environment Variables

Create a `.env` file in the backend directory:

```env
MONGODB_URI=mongodb://localhost:27017/careerhub
PORT=5000
SCRAPER_INTERVAL_MINUTES=60
COMPANY_URLS=https://careers.tcs.com/,https://careers.infosys.com/
```

## API Endpoints

- `GET /api/jobs` - Get all jobs with optional filters
  - Query params: `year`, `company`, `type`
- `GET /api/jobs/:id` - Get specific job by ID

## Usage

1. Select your academic year
2. Use the search bar to filter by company
3. Browse available opportunities
4. Click "Apply" to visit the company's career page

## Deployment

### Local Development with Docker

```bash
docker-compose up --build
```

### Production Deployment

- **Frontend**: Deploy to Vercel/Netlify
- **Backend**: Deploy to Railway/Heroku
- **Database**: Use MongoDB Atlas
- **Scraper**: Run on a VPS or cloud function

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Testing Documentation

### Critical-Path Testing Approach

This project uses manual critical-path testing suitable for a B.Tech academic project. Testing focuses on key functionality verification rather than comprehensive automated test suites.

### Test Environment Setup

1. **Prerequisites**:
   - Node.js installed
   - Python installed
   - MongoDB running (local or Atlas)
   - Dependencies installed (see Installation section)

2. **Environment Variables**:
   - Copy `.env.example` to `backend/.env`
   - Set `MONGODB_URI` to your MongoDB connection string

### Backend API Testing

**Test Case 1: MongoDB Connection**
- **Steps**:
  1. Start MongoDB service
  2. Run `cd backend && npm run dev`
  3. Check console for "MongoDB connected" message
- **Expected Result**: Server starts without errors, MongoDB connection successful
- **Status**: [Manual verification required]

**Test Case 2: GET /api/jobs Endpoint**
- **Steps**:
  1. Start backend server
  2. Use browser or curl: `curl http://localhost:5000/api/jobs`
- **Expected Result**: Returns JSON array (empty initially)
- **Status**: [Manual verification required]

**Test Case 3: Job Filtering by Year**
- **Steps**:
  1. Ensure jobs exist in database
  2. Test: `curl "http://localhost:5000/api/jobs?year=1st"`
- **Expected Result**: Returns only internship jobs for 1st year
- **Status**: [Manual verification required]

**Test Case 4: Company Search**
- **Steps**:
  1. Ensure jobs exist in database
  2. Test: `curl "http://localhost:5000/api/jobs?company=tcs"`
- **Expected Result**: Returns jobs from TCS (case-insensitive partial match)
- **Status**: [Manual verification required]

### Frontend UI Testing

**Test Case 5: React App Rendering**
- **Steps**:
  1. Run `cd frontend && npm start`
  2. Open browser to http://localhost:3000
- **Expected Result**: App loads without errors, shows year selector and search bar
- **Status**: [Manual verification required]

**Test Case 6: Year Selection**
- **Steps**:
  1. Select "1st Year" from dropdown
  2. Check if job list updates accordingly
- **Expected Result**: Shows internship opportunities only
- **Status**: [Manual verification required]

**Test Case 7: Search Functionality**
- **Steps**:
  1. Type "tata" in search bar
  2. Check filtered results
- **Expected Result**: Shows jobs from Tata companies
- **Status**: [Manual verification required]

### Scraper Testing

**Test Case 8: Scraper Execution**
- **Steps**:
  1. Run `cd scraper && python scraper.py`
- **Expected Result**: Scrapes sample jobs, saves to MongoDB without duplicates
- **Status**: [Manual verification required]

**Test Case 9: Duplicate Prevention**
- **Steps**:
  1. Run scraper multiple times
  2. Check database for duplicate entries
- **Expected Result**: No duplicate jobId entries
- **Status**: [Manual verification required]

### End-to-End Integration Testing

**Test Case 10: Complete Flow**
- **Steps**:
  1. Run scraper to populate database
  2. Start backend server
  3. Start frontend
  4. Select year and search in UI
- **Expected Result**: Jobs display correctly based on filters
- **Status**: [Manual verification required]

### Sample Test Commands

```bash
# Backend testing
curl http://localhost:5000/api/jobs
curl "http://localhost:5000/api/jobs?year=4th"
curl "http://localhost:5000/api/jobs?company=infosys"

# Scraper testing
cd scraper && python scraper.py
```

### Test Results Documentation

After running tests, update the status in this section:
- [ ] All backend tests passed
- [ ] All frontend tests passed
- [ ] All scraper tests passed
- [ ] End-to-end flow working

## License

This project is for educational purposes only.
=======
# CareerHub - Centralized Job & Internship Portal for B.Tech Students

## Overview

CareerHub is a web-based platform designed exclusively for B.Tech students to view internship and job opportunities without requiring login or registration. The system automatically collects opportunities from public company career websites and displays them in a clean, student-focused interface.

## Features

- **Academic Year Selection**: Choose 1st/2nd/3rd year for internships, 4th year for jobs + internships
- **Company-Based Search**: Search jobs by company name with partial match support
- **Automated Job Aggregation**: Scheduled scraping from public career pages
- **No Authentication**: No signup/login required
- **Responsive UI**: Clean and beginner-friendly interface

## Tech Stack

- **Frontend**: React.js
- **Backend**: Node.js + Express.js
- **Database**: MongoDB
- **Scraper**: Python (BeautifulSoup, Requests)
- **Scheduler**: Node.js (node-schedule)

## Project Structure

```
careerhub/
├── backend/                 # Node.js/Express API
│   ├── models/             # MongoDB schemas
│   ├── routes/             # API endpoints
│   ├── config/             # Database configuration
│   ├── server.js           # Main server file
│   └── package.json
├── frontend/                # React application
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── services/       # API service functions
│   │   └── App.js          # Main app component
│   ├── public/
│   └── package.json
├── scraper/                 # Python web scraper
│   ├── scraper.py          # Main scraping logic
│   ├── config.py           # Scraper configuration
│   └── requirements.txt
├── .env.example            # Environment variables template
├── docker-compose.yml      # Docker setup for local development
└── README.md
```

## Getting Started

### Prerequisites

- Node.js (v16 or higher)
- Python (v3.8 or higher)
- MongoDB (local or Atlas)
- npm or yarn

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd careerhub
   ```

2. **Backend Setup**
   ```bash
   cd backend
   npm install
   cp ../.env.example .env  # Configure your MongoDB URI
   npm run dev
   ```

3. **Frontend Setup**
   ```bash
   cd ../frontend
   npm install
   npm start
   ```

4. **Scraper Setup**
   ```bash
   cd ../scraper
   pip install -r requirements.txt
   python scraper.py
   ```

### Environment Variables

Create a `.env` file in the backend directory:

```env
MONGODB_URI=mongodb://localhost:27017/careerhub
PORT=5000
SCRAPER_INTERVAL_MINUTES=60
COMPANY_URLS=https://careers.tcs.com/,https://careers.infosys.com/
```

## API Endpoints

- `GET /api/jobs` - Get all jobs with optional filters
  - Query params: `year`, `company`, `type`
- `GET /api/jobs/:id` - Get specific job by ID

## Usage

1. Select your academic year
2. Use the search bar to filter by company
3. Browse available opportunities
4. Click "Apply" to visit the company's career page

## System Architecture

### High-Level Architecture

```
[Company Career Pages] --> [Python Scraper] --> [MongoDB]
                                      |
                                      v
[React Frontend] <--> [Node.js Backend API] <--> [MongoDB]
```

### Data Flow Diagram (DFD)

1. **Level 0 DFD**:
   - External Entities: Students, Company Career Websites
   - Processes: Web Scraper, Backend API, Frontend UI
   - Data Stores: Job Database

2. **Level 1 DFD**:
   - Process 1: Scrape Jobs
     - Input: Company URLs
     - Output: Job Data
   - Process 2: Store Jobs
     - Input: Scraped Job Data
     - Output: Stored Jobs
   - Process 3: Filter & Search Jobs
     - Input: User Filters (Year, Company)
     - Output: Filtered Job List
   - Process 4: Display Jobs
     - Input: Filtered Jobs
     - Output: Job Listings UI

### Entity-Relationship Diagram (ERD)

**Entities:**
- Job (jobId, companyName, jobTitle, jobType, eligibleYear, location, applyLink, sourceWebsite, postedDate, lastUpdated)

**Relationships:**
- Jobs are scraped from Company Websites
- Jobs are filtered by Academic Year
- Jobs are searched by Company Name

## Deployment

### Local Development with Docker

```bash
docker-compose up --build
```

### Production Deployment

- **Frontend**: Deploy to Vercel/Netlify
- **Backend**: Deploy to Railway/Heroku
- **Database**: Use MongoDB Atlas
- **Scraper**: Run on a VPS or cloud function

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is for educational purposes only.
