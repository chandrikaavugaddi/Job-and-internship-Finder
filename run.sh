#!/bin/bash

echo "========================================"
echo "   CareerHub - Automated Setup Script"
echo "========================================"

echo ""
echo "Setting up CareerHub project..."

echo ""
echo "Step 1: Installing backend dependencies..."
cd backend
npm install
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install backend dependencies"
    exit 1
fi

echo ""
echo "Step 2: Installing frontend dependencies..."
cd ../frontend
npm install
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install frontend dependencies"
    exit 1
fi

echo ""
echo "Step 3: Installing scraper dependencies..."
cd ../scraper
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install scraper dependencies"
    exit 1
fi

echo ""
echo "Step 4: Setting up environment variables..."
cd ../backend
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env file from .env.example"
    echo "Please edit backend/.env to set your MongoDB connection string"
    echo "Press Enter after editing .env..."
    read -p ""
fi

echo ""
echo "Step 5: Running scraper to populate database..."
cd ../scraper
python scraper.py &
echo "Scraper started in background..."

echo ""
echo "Step 6: Starting backend server..."
cd ../backend
npm run dev &
echo "Backend server started..."

echo ""
echo "Step 7: Starting frontend..."
cd ../frontend
npm start &
echo "Frontend started..."

echo ""
echo "========================================"
echo "   CareerHub is starting up!"
echo "========================================"
echo ""
echo "- Backend API: http://localhost:5000"
echo "- Frontend UI: http://localhost:3000"
echo "- MongoDB: localhost:27017 (if using local)"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for all background processes
wait
