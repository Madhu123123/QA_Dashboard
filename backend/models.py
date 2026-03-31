from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()


class TestRun(db.Model):
    """Model for a test run execution"""
    __tablename__ = 'test_runs'

    id = db.Column(db.Integer, primary_key=True)
    run_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    run_type = db.Column(db.String(50), nullable=False)  # functionality, regression, smoke, etc.
    status = db.Column(db.String(20), default='queued')  # queued, running, completed, failed
    module = db.Column(db.String(100), nullable=True)
    environment = db.Column(db.String(50), nullable=False)  # staging, production, qa, local
    execution_mode = db.Column(db.String(20), default='parallel')  # parallel, sequential
    browsers = db.Column(db.String(500), nullable=False)  # JSON array of browsers
    total_tests = db.Column(db.Integer, default=0)
    passed_tests = db.Column(db.Integer, default=0)
    failed_tests = db.Column(db.Integer, default=0)
    skipped_tests = db.Column(db.Integer, default=0)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    duration_seconds = db.Column(db.Integer, nullable=True)
    
    # Relationships
    test_cases = db.relationship('TestCase', backref='run', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'run_id': self.run_id,
            'run_type': self.run_type,
            'status': self.status,
            'module': self.module,
            'environment': self.environment,
            'execution_mode': self.execution_mode,
            'browsers': json.loads(self.browsers) if self.browsers else [],
            'total_tests': self.total_tests,
            'passed_tests': self.passed_tests,
            'failed_tests': self.failed_tests,
            'skipped_tests': self.skipped_tests,
            'started_at': self.started_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'duration_seconds': self.duration_seconds,
            'pass_rate': f"{(self.passed_tests / self.total_tests * 100):.1f}%" if self.total_tests > 0 else "0%"
        }


class TestCase(db.Model):
    """Model for individual test cases within a run"""
    __tablename__ = 'test_cases'

    id = db.Column(db.Integer, primary_key=True)
    run_id = db.Column(db.Integer, db.ForeignKey('test_runs.id'), nullable=False)
    test_name = db.Column(db.String(255), nullable=False)
    module = db.Column(db.String(100), nullable=False)
    browser = db.Column(db.String(50), nullable=False)
    environment = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20))  # running, passed, failed, skipped
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    duration_seconds = db.Column(db.Float, nullable=True)
    error_message = db.Column(db.Text, nullable=True)
    screenshot_path = db.Column(db.String(255), nullable=True)
    retry_count = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {
            'id': self.id,
            'run_id': self.run_id,
            'test_name': self.test_name,
            'module': self.module,
            'browser': self.browser,
            'environment': self.environment,
            'status': self.status,
            'started_at': self.started_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'duration_seconds': self.duration_seconds,
            'error_message': self.error_message,
            'screenshot_path': self.screenshot_path,
            'retry_count': self.retry_count
        }
