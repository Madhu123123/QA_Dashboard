"""
QA Test Runner Dashboard - Backend API
A full-stack application for running Playwright tests with real-time monitoring
"""

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from models import db, TestRun, TestCase
from test_runner import test_runner
import logging
import asyncio
from datetime import datetime, timedelta
import json
import os

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///qa_test_runner.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_SORT_KEYS'] = False

# Initialize extensions
db.init_app(app)
CORS(app)

# Create database tables
with app.app_context():
    db.create_all()


# ===============================================
# DASHBOARD ENDPOINTS
# ===============================================

@app.route('/api/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    """Get overall dashboard statistics"""
    try:
        total_runs = TestRun.query.count()
        total_tests = db.session.query(db.func.sum(TestRun.total_tests)).scalar() or 0
        total_passed = db.session.query(db.func.sum(TestRun.passed_tests)).scalar() or 0
        total_failed = db.session.query(db.func.sum(TestRun.failed_tests)).scalar() or 0
        
        # Get last 30 days stats
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_runs = TestRun.query.filter(TestRun.started_at >= thirty_days_ago).all()
        
        return jsonify({
            'total_runs': total_runs,
            'total_tests': int(total_tests),
            'total_passed': int(total_passed),
            'total_failed': int(total_failed),
            'pass_rate': f"{(int(total_passed) / int(total_tests) * 100):.1f}%" if total_tests > 0 else "0%",
            'recent_runs_count': len(recent_runs)
        })
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {str(e)}")
        return jsonify({'error': str(e)}), 500


# ===============================================
# TEST RUN ENDPOINTS
# ===============================================

@app.route('/api/runs', methods=['GET'])
def get_all_runs():
    """Get all test runs with pagination"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        pagination = TestRun.query.order_by(TestRun.started_at.desc()).paginate(
            page=page, per_page=per_page
        )
        
        return jsonify({
            'runs': [run.to_dict() for run in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page
        })
    except Exception as e:
        logger.error(f"Error getting runs: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/runs/<run_id>', methods=['GET'])
def get_run(run_id):
    """Get details of a specific test run"""
    try:
        run = TestRun.query.filter_by(run_id=run_id).first()
        if not run:
            return jsonify({'error': 'Run not found'}), 404
        
        test_cases = TestCase.query.filter_by(run_id=run.id).all()
        
        return jsonify({
            'run': run.to_dict(),
            'test_cases': [tc.to_dict() for tc in test_cases]
        })
    except Exception as e:
        logger.error(f"Error getting run: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/runs', methods=['POST'])
def start_test_run():
    """Start a new test run with configuration"""
    try:
        config = request.get_json()
        
        # Validate required fields
        required_fields = ['run_type', 'environment', 'browsers']
        for field in required_fields:
            if field not in config:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Run tests asynchronously
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(test_runner.run_tests(config, app))
        
        return jsonify(result), 201
    
    except Exception as e:
        logger.error(f"Error starting test run: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/runs/<run_id>/status', methods=['GET'])
def get_run_status(run_id):
    """Get real-time status of a running test"""
    try:
        run = TestRun.query.filter_by(run_id=run_id).first()
        if not run:
            return jsonify({'error': 'Run not found'}), 404
        
        status = test_runner.get_run_status(run_id)
        
        return jsonify({
            'run_id': run_id,
            'status': run.status,
            'progress': {
                'total': run.total_tests,
                'completed': run.passed_tests + run.failed_tests + run.skipped_tests,
                'passed': run.passed_tests,
                'failed': run.failed_tests,
                'skipped': run.skipped_tests,
                'percentage': int(
                    ((run.passed_tests + run.failed_tests + run.skipped_tests) / 
                     run.total_tests * 100) if run.total_tests > 0 else 0
                )
            },
            'running': status or {}
        })
    except Exception as e:
        logger.error(f"Error getting run status: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/runs/<run_id>/stop', methods=['POST'])
def stop_run(run_id):
    """Stop a running test"""
    try:
        result = test_runner.stop_run(run_id, app)
        return jsonify({'success': result, 'message': 'Test run stopped'})
    except Exception as e:
        logger.error(f"Error stopping run: {str(e)}")
        return jsonify({'error': str(e)}), 500


# ===============================================
# TEST CASE ENDPOINTS
# ===============================================

@app.route('/api/runs/<run_id>/test-cases', methods=['GET'])
def get_run_test_cases(run_id):
    """Get all test cases for a specific run"""
    try:
        run = TestRun.query.filter_by(run_id=run_id).first()
        if not run:
            return jsonify({'error': 'Run not found'}), 404
        
        test_cases = TestCase.query.filter_by(run_id=run.id).all()
        
        return jsonify({
            'test_cases': [tc.to_dict() for tc in test_cases]
        })
    except Exception as e:
        logger.error(f"Error getting test cases: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/test-cases/<int:test_id>/retry', methods=['POST'])
def retry_test_case(test_id):
    """Retry a failed test case"""
    try:
        test_case = TestCase.query.get(test_id)
        if not test_case:
            return jsonify({'error': 'Test case not found'}), 404
        
        # Update test case status
        test_case.status = 'retrying'
        test_case.retry_count += 1
        db.session.commit()
        
        # In production, this would trigger actual Playwright test re-execution
        
        return jsonify({
            'success': True,
            'message': 'Test queued for retry',
            'test_case': test_case.to_dict()
        })
    except Exception as e:
        logger.error(f"Error retrying test: {str(e)}")
        return jsonify({'error': str(e)}), 500


# ===============================================
# REPORT ENDPOINTS
# ===============================================

@app.route('/api/reports/<run_id>/html', methods=['GET'])
def export_html_report(run_id):
    """Export test run as HTML report"""
    try:
        run = TestRun.query.filter_by(run_id=run_id).first()
        if not run:
            return jsonify({'error': 'Run not found'}), 404
        
        test_cases = TestCase.query.filter_by(run_id=run.id).all()
        
        # Generate HTML report
        html_content = generate_html_report(run, test_cases)
        
        return html_content, 200, {'Content-Disposition': f'attachment; filename=report_{run_id}.html'}
    except Exception as e:
        logger.error(f"Error generating HTML report: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/reports/<run_id>/csv', methods=['GET'])
def export_csv_report(run_id):
    """Export test run as CSV report"""
    try:
        run = TestRun.query.filter_by(run_id=run_id).first()
        if not run:
            return jsonify({'error': 'Run not found'}), 404
        
        test_cases = TestCase.query.filter_by(run_id=run.id).all()
        
        # Generate CSV
        csv_content = generate_csv_report(run, test_cases)
        
        return csv_content, 200, {
            'Content-Disposition': f'attachment; filename=report_{run_id}.csv',
            'Content-Type': 'text/csv'
        }
    except Exception as e:
        logger.error(f"Error generating CSV report: {str(e)}")
        return jsonify({'error': str(e)}), 500


# ===============================================
# CONFIGURATION ENDPOINTS
# ===============================================

@app.route('/api/config/modules', methods=['GET'])
def get_modules():
    """Get available test modules"""
    modules = [
        'All modules',
        'Login & auth',
        'Checkout',
        'User profile',
        'Search',
        'Payments',
        'Dashboard'
    ]
    return jsonify({'modules': modules})


@app.route('/api/config/environments', methods=['GET'])
def get_environments():
    """Get available environments"""
    environments = ['Staging', 'Production', 'QA', 'Local']
    return jsonify({'environments': environments})


@app.route('/api/config/browsers', methods=['GET'])
def get_browsers():
    """Get available browsers"""
    browsers = [
        {'name': 'Chrome', 'icon': '🌐'},
        {'name': 'Firefox', 'icon': '🦊'},
        {'name': 'Safari', 'icon': '🧭'},
        {'name': 'Edge', 'icon': '🔷'},
        {'name': 'Mobile Chrome', 'icon': '📱'},
        {'name': 'Mobile Safari', 'icon': '📱'}
    ]
    return jsonify({'browsers': browsers})


@app.route('/api/config/run-types', methods=['GET'])
def get_run_types():
    """Get available test run types"""
    run_types = [
        {
            'id': 'functionality',
            'title': 'Functionality scripts',
            'description': 'Run scripts for a specific feature or module only',
            'icon': '⚡'
        },
        {
            'id': 'selective',
            'title': 'Selective regression',
            'description': 'Cherry-pick test cases relevant to recent changes',
            'icon': '◎'
        },
        {
            'id': 'full',
            'title': 'Full regression',
            'description': 'Run the complete regression suite across all modules',
            'icon': '⊞'
        },
        {
            'id': 'rerun',
            'title': 'Re-run failures',
            'description': 'Retry only the test cases that failed in the last run',
            'icon': '↻'
        },
        {
            'id': 'smoke',
            'title': 'Smoke tests',
            'description': 'Quick sanity check — core flows only, fastest run',
            'icon': '⊡'
        },
        {
            'id': 'custom',
            'title': 'Custom selection',
            'description': 'Manually pick any combination of test cases',
            'icon': '✎'
        }
    ]
    return jsonify({'run_types': run_types})


# ===============================================
# HELPER FUNCTIONS
# ===============================================

def generate_html_report(run, test_cases):
    """Generate HTML report for test run"""
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>QA Test Report - {run.run_id}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .header {{ background: #f0f0f0; padding: 20px; border-radius: 5px; }}
            .metrics {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin: 20px 0; }}
            .metric {{ background: white; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
            .metric-value {{ font-size: 24px; font-weight: bold; }}
            .metric-label {{ color: #666; font-size: 12px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th {{ background: #333; color: white; padding: 10px; text-align: left; }}
            td {{ padding: 10px; border-bottom: 1px solid #ddd; }}
            tr:hover {{ background: #f5f5f5; }}
            .passed {{ color: green; }}
            .failed {{ color: red; }}
            .skipped {{ color: orange; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>QA Test Report</h1>
            <p><strong>Run ID:</strong> {run.run_id}</p>
            <p><strong>Run Type:</strong> {run.run_type}</p>
            <p><strong>Environment:</strong> {run.environment}</p>
            <p><strong>Started:</strong> {run.started_at}</p>
            <p><strong>Completed:</strong> {run.completed_at}</p>
        </div>
        
        <div class="metrics">
            <div class="metric">
                <div class="metric-value">{run.total_tests}</div>
                <div class="metric-label">Total Tests</div>
            </div>
            <div class="metric">
                <div class="metric-value passed">{run.passed_tests}</div>
                <div class="metric-label">Passed</div>
            </div>
            <div class="metric">
                <div class="metric-value failed">{run.failed_tests}</div>
                <div class="metric-label">Failed</div>
            </div>
            <div class="metric">
                <div class="metric-value skipped">{run.skipped_tests}</div>
                <div class="metric-label">Skipped</div>
            </div>
        </div>
        
        <table>
            <thead>
                <tr>
                    <th>Test Name</th>
                    <th>Module</th>
                    <th>Browser</th>
                    <th>Status</th>
                    <th>Duration (s)</th>
                </tr>
            </thead>
            <tbody>
    """
    
    for tc in test_cases:
        status_class = tc.status.lower()
        html += f"""
                <tr>
                    <td>{tc.test_name}</td>
                    <td>{tc.module}</td>
                    <td>{tc.browser}</td>
                    <td class="{status_class}">{tc.status}</td>
                    <td>{tc.duration_seconds:.2f if tc.duration_seconds else 'N/A'}</td>
                </tr>
        """
    
    html += """
            </tbody>
        </table>
    </body>
    </html>
    """
    
    return html


def generate_csv_report(run, test_cases):
    """Generate CSV report for test run"""
    csv = "Test Name,Module,Browser,Status,Duration (s),Error\n"
    
    for tc in test_cases:
        error = tc.error_message.replace(',', ';') if tc.error_message else ''
        csv += f"{tc.test_name},{tc.module},{tc.browser},{tc.status},{tc.duration_seconds},{error}\n"
    
    return csv


# ===============================================
# ERROR HANDLERS
# ===============================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500


# ===============================================
# HEALTH CHECK
# ===============================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
