# Quick Start Guide

## Get Up and Running in 5 Minutes

### Step 1: Clone and Navigate
```bash
cd Playwright_QA_Dashboard
```

### Step 2: Start the Backend

**Terminal 1 - Backend API:**
```bash
cd backend

# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install

# Start the server
python app.py
```

The API will be available at: **http://localhost:5000**

### Step 3: Start the Frontend

**Terminal 2 - Frontend Server:**
```bash
cd frontend

# Using Python 3
python -m http.server 8000

# Or using Node.js (if installed)
npx http-server -p 8000
```

The dashboard will be available at: **http://localhost:8000**

### Step 4: Open Dashboard

Open your browser and navigate to:
```
http://localhost:8000
```

You should see the QA Test Runner Dashboard!

## Running Your First Test

1. **Select a run type** - Click on "Functionality scripts"
2. **Choose options**:
   - Module: "All modules"
   - Environment: "Staging"
   - Browsers: Keep Chrome and Firefox selected
3. **Click "Run now"**
4. **Monitor** the tests in the Live run status section
5. **View results** in the Reports section

## Project Structure

```
Playwright_QA_Dashboard/
├── backend/                    # Flask API
│   ├── app.py                 # Main Flask application
│   ├── models.py              # Database models
│   ├── test_runner.py         # Test execution logic
│   ├── requirements.txt        # Dependencies
│   └── tests/
│       └── conftest.py        # Sample Playwright tests
├── frontend/                  # Web UI
│   ├── index.html             # Main page
│   ├── css/style.css          # Styling
│   └── js/
│       ├── api.js             # API client
│       └── dashboard.js       # UI logic
├── README.md                  # Full documentation
├── QUICKSTART.md              # This file
└── .gitignore                 # Git ignore rules
```

## Common Commands

### Backend Commands

```bash
# Install dependencies
pip install -r backend/requirements.txt

# Install Playwright browsers
playwright install

# Start API server
python backend/app.py

# Run pytest tests
pytest backend/tests/

# Reset database
rm backend/qa_test_runner.db
```

### Frontend Commands

```bash
# Start development server (Python)
cd frontend && python -m http.server 8000

# Start development server (Node.js)
cd frontend && npx http-server -p 8000
```

## API Health Check

To verify the API is working:
```bash
curl http://localhost:5000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2024-03-31T10:00:00.000000"
}
```

## Troubleshooting

### "Cannot connect to API" Error
- Check if backend is running: `python backend/app.py`
- Verify port 5000 is available
- Check browser console (F12) for CORS errors

### "Module not found" Error
```bash
pip install -r backend/requirements.txt
```

### Browser not launching
```bash
playwright install
```

### Port Already in Use
- Backend: Edit `app.py` and change port to 5001
- Frontend: Use `python -m http.server 8001`

## Next Steps

1. **Create custom tests** - Add test cases to `backend/tests/conftest.py`
2. **Configure environments** - Update test URLs and credentials
3. **Schedule runs** - Set up automated test runs
4. **Add integrations** - Connect with CI/CD pipelines

## Documentation

- See [README.md](./README.md) for complete documentation
- Check [backend/app.py](./backend/app.py) for API documentation
- Review [backend/tests/conftest.py](./backend/tests/conftest.py) for test examples

## Support

For issues:
1. Check the Troubleshooting section above
2. Review the full README.md
3. Check console logs for error messages
4. Verify all dependencies are installed

---

**Happy Testing!** 🚀
