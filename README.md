# QA Test Runner Dashboard

A complete full-stack application for running and monitoring Playwright tests with a modern web interface.

## Architecture Overview

```
Playwright_QA_Dashboard/
├── backend/
│   ├── app.py                 # Flask API server
│   ├── models.py              # SQLAlchemy database models
│   ├── test_runner.py         # Playwright test execution service
│   ├── requirements.txt        # Python dependencies
│   └── tests/
│       └── conftest.py        # Sample Playwright test suite
├── frontend/
│   ├── index.html             # Main dashboard UI
│   ├── css/
│   │   └── style.css          # Complete design system
│   └── js/
│       ├── api.js             # API client
│       └── dashboard.js       # Dashboard logic
└── README.md                  # This file
```

## Features

### Dashboard
- **Real-time metrics** - Total tests, passed, failed, and skipped counts
- **Run type selection** - Functionality, regression, smoke, custom, and more
- **Configurable execution** - Module selection, environment, execution mode, browsers
- **Live monitoring** - Real-time test execution status and progress
- **Test history** - View past runs with detailed reports
- **Report export** - Download reports as HTML or CSV

### Backend API
- **Test execution** - Start and manage test runs
- **Status tracking** - Real-time progress updates
- **Configuration** - Dynamic configuration endpoints
- **Reports** - Generate and export reports
- **Database** - Persistent storage of test runs and results

### Integration
- **Playwright tests** - Integrated with actual Playwright test scripts
- **Flexible test discovery** - Configure which tests to run
- **Browser support** - Chrome, Firefox, Safari, Edge, Mobile variants
- **Environment support** - Staging, Production, QA, Local

## Installation & Setup

### Prerequisites
- Python 3.8+
- Node.js/npm (optional, for frontend development)
- Git

### Backend Setup

1. **Install Python dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Install Playwright browsers:**
   ```bash
   playwright install
   ```

3. **Initialize the database:**
   ```bash
   python
   >>> from app import app, db
   >>> with app.app_context():
   ...     db.create_all()
   >>> exit()
   ```

4. **Start the API server:**
   ```bash
   python app.py
   ```
   The API will be available at `http://localhost:5000`

### Frontend Setup

1. **Serve the frontend:**
   ```bash
   cd frontend
   # Using Python 3
   python -m http.server 8000
   
   # Or using Node.js
   npx http-server -p 8000
   ```

2. **Open in browser:**
   ```
   http://localhost:8000
   ```

## API Endpoints

### Dashboard
- `GET /api/dashboard/stats` - Get overall statistics

### Test Runs
- `GET /api/runs` - List all test runs
- `GET /api/runs/<run_id>` - Get specific run details
- `POST /api/runs` - Start a new test run
- `GET /api/runs/<run_id>/status` - Get real-time status
- `POST /api/runs/<run_id>/stop` - Stop a running test

### Test Cases
- `GET /api/runs/<run_id>/test-cases` - Get test cases for a run
- `POST /api/test-cases/<test_id>/retry` - Retry a failed test

### Reports
- `GET /api/reports/<run_id>/html` - Export as HTML
- `GET /api/reports/<run_id>/csv` - Export as CSV

### Configuration
- `GET /api/config/modules` - Available modules
- `GET /api/config/environments` - Available environments
- `GET /api/config/browsers` - Available browsers
- `GET /api/config/run-types` - Available run types

## Usage Guide

### Starting a Test Run

1. **Select Run Type**
   - Choose from Functionality, Regression, Smoke, or other options
   - Each type configures a different test suite

2. **Configure Options**
   - **Module**: Select which module to test (or all modules)
   - **Environment**: Choose target environment (Staging, Prod, QA, Local)
   - **Execution Mode**: Parallel (faster) or Sequential
   - **Browsers**: Select which browsers to test
   - **Retries**: Configure automatic retry on failure

3. **Click "Run now"**
   - Test execution starts immediately
   - Monitor progress in the Live run status section
   - View real-time test results as they complete

### Monitoring Tests

- **Live Status Table**: See individual test cases as they execute
- **Progress Bars**: Visual indicator of test completion
- **Status Pills**: Color-coded status (Running, Passed, Failed, Skipped)
- **Duration**: Actual test execution time

### Viewing Reports

- **View**: Click "View" to see detailed test results
- **Export**: Download reports as HTML or CSV
- **Email**: Send reports via email (feature in development)

## Playwright Integration

### Example Test Structure

```python
# tests/conftest.py

class TestAuthentication:
    @pytest.fixture(scope="function")
    def browser_context(self):
        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context()
            yield context
            context.close()
            browser.close()

    def test_login_with_valid_credentials(self, browser_context):
        page = browser_context.new_page()
        page.goto("https://example.com/login")
        page.fill("input[name='username']", "testuser@example.com")
        page.fill("input[name='password']", "password123")
        page.click("button:has-text('Login')")
        expect(page).to_have_url("**/dashboard")
        page.close()
```

### Running Tests Locally

```bash
# Run all tests
pytest tests/

# Run specific test class
pytest tests/conftest.py::TestAuthentication

# Run specific test
pytest tests/conftest.py::TestAuthentication::test_login_with_valid_credentials

# With verbose output
pytest tests/ -v
```

## Database Models

### TestRun
Stores information about each test execution:
- `run_id`: Unique identifier
- `run_type`: Type of test (functionality, regression, etc.)
- `status`: Current status (running, completed, failed)
- `total_tests`: Total number of tests
- `passed_tests`: Number of passed tests
- `failed_tests`: Number of failed tests
- `started_at`, `completed_at`: Timestamps
- `duration_seconds`: Total execution time

### TestCase
Stores individual test case results:
- `test_name`: Name of the test
- `module`: Module being tested
- `browser`: Browser that tested it
- `environment`: Target environment
- `status`: Test status (passed, failed, skipped)
- `duration_seconds`: Test execution time
- `error_message`: Failure details
- `retry_count`: Number of retries

## Configuration

### Environment Variables
Create a `.env` file in the backend directory:

```bash
FLASK_ENV=development
DATABASE_URL=sqlite:///qa_test_runner.db
DEBUG=True
```

### API Base URL
The frontend defaults to `http://localhost:5000`. To change:

Edit `frontend/js/api.js`:
```javascript
const api = new APIClient('http://your-api-url:port');
```

## Contributing

### Adding New Tests

1. Create test file in `backend/tests/conftest.py`
2. Follow Playwright test patterns
3. Use pytest fixtures for setup/teardown
4. Tests are discovered automatically by the test runner

### Extending the API

1. Add new endpoints in `backend/app.py`
2. Use database models from `backend/models.py`
3. Return JSON responses
4. Implement proper error handling

### Customizing the UI

1. Edit `frontend/css/style.css` for styling
2. Edit `frontend/js/dashboard.js` for functionality
3. Use the API client in `frontend/js/api.js`

## Troubleshooting

### API Connection Failed
- Ensure backend is running: `python app.py`
- Check if port 5000 is available
- Check browser console for CORS errors
- Enable CORS in Flask if needed

### Database Errors
- Delete `backend/qa_test_runner.db` to reset
- Re-initialize with `python` and the db.create_all() command

### Playwright Tests Fail
- Ensure Playwright browsers are installed: `playwright install`
- Check that test URLs are correct
- Verify test credentials are valid
- See Playwright documentation for element selectors

### Port Already in Use
- Backend: Change port in `app.py`: `app.run(port=5001)`
- Frontend: `python -m http.server 8001`

## Production Deployment

### Backend
1. Set `DEBUG=False` in Flask config
2. Use production WSGI server (Gunicorn):
   ```bash
   pip install gunicorn
   gunicorn app:app -w 4 -b 0.0.0.0:5000
   ```
3. Set up database (PostgreSQL recommended)
4. Configure environment variables

### Frontend
1. Build optimized files
2. Deploy to CDN or web server
3. Update API base URL for production

## License

MIT

## Support

For issues or questions, see the documentation or check the backend logs.
