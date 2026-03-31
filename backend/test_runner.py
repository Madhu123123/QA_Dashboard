import asyncio
import json
from datetime import datetime
from uuid import uuid4
import logging
from models import db, TestRun, TestCase

logger = logging.getLogger(__name__)


class PlaywrightTestRunner:
    """
    Service to execute Playwright tests based on configuration
    and track test execution status
    """

    def __init__(self):
        self.running_tests = {}
        self.test_results = {}

    async def run_tests(self, config, app):
        """
        Execute tests based on configuration
        Args:
            config: {
                run_type: str,
                module: str,
                environment: str,
                execution_mode: str,
                browsers: list,
                max_retries: int,
                tags: str
            }
        """
        run_id = str(uuid4())
        
        with app.app_context():
            # Create test run record
            browsers_str = json.dumps(config.get('browsers', []))
            test_run = TestRun(
                run_id=run_id,
                run_type=config.get('run_type', 'custom'),
                module=config.get('module'),
                environment=config.get('environment', 'staging'),
                execution_mode=config.get('execution_mode', 'parallel'),
                browsers=browsers_str,
                status='running'
            )
            
            db.session.add(test_run)
            db.session.commit()
            
            self.running_tests[run_id] = {
                'status': 'running',
                'progress': 0,
                'total': 0,
                'completed': 0,
                'passed': 0,
                'failed': 0
            }

            try:
                # Load and execute playwright tests
                test_cases = self._get_test_cases(config)
                test_run.total_tests = len(test_cases)
                db.session.commit()
                
                self.running_tests[run_id]['total'] = len(test_cases)
                
                # Execute tests
                for idx, test_case in enumerate(test_cases):
                    try:
                        result = await self._execute_test(test_case, config)
                        
                        # Create test case record
                        tc = TestCase(
                            run_id=test_run.id,
                            test_name=test_case['name'],
                            module=test_case['module'],
                            browser=test_case['browser'],
                            environment=config.get('environment', 'staging'),
                            status=result['status'],
                            duration_seconds=result.get('duration', 0),
                            error_message=result.get('error')
                        )
                        db.session.add(tc)
                        
                        # Update metrics
                        if result['status'] == 'passed':
                            test_run.passed_tests += 1
                            self.running_tests[run_id]['passed'] += 1
                        elif result['status'] == 'failed':
                            test_run.failed_tests += 1
                            self.running_tests[run_id]['failed'] += 1
                        
                        self.running_tests[run_id]['completed'] += 1
                        self.running_tests[run_id]['progress'] = int(
                            (self.running_tests[run_id]['completed'] / 
                             self.running_tests[run_id]['total']) * 100
                        )
                        
                        db.session.commit()
                        
                    except Exception as e:
                        logger.error(f"Error executing test {test_case['name']}: {str(e)}")
                        test_run.failed_tests += 1
                        self.running_tests[run_id]['failed'] += 1
                        self.running_tests[run_id]['completed'] += 1
                
                # Mark run as completed
                test_run.status = 'completed'
                test_run.completed_at = datetime.utcnow()
                test_run.duration_seconds = int(
                    (test_run.completed_at - test_run.started_at).total_seconds()
                )
                
                self.running_tests[run_id]['status'] = 'completed'
                
            except Exception as e:
                logger.error(f"Error running tests: {str(e)}")
                test_run.status = 'failed'
                test_run.completed_at = datetime.utcnow()
                self.running_tests[run_id]['status'] = 'failed'
                self.running_tests[run_id]['error'] = str(e)
            
            db.session.commit()
            
            return {
                'run_id': run_id,
                'test_run': test_run.to_dict()
            }

    def _get_test_cases(self, config):
        """
        Get test cases based on configuration
        This would load from actual test files or test definitions
        """
        # Sample test cases - in production, this would load actual Playwright test specs
        all_tests = {
            'login': [
                {'name': 'Login with valid credentials', 'module': 'Auth', 'browser': 'Chrome'},
                {'name': 'Login with invalid password', 'module': 'Auth', 'browser': 'Chrome'},
                {'name': 'Login timeout handling', 'module': 'Auth', 'browser': 'Firefox'}
            ],
            'checkout': [
                {'name': 'Add to cart — guest user', 'module': 'Checkout', 'browser': 'Chrome'},
                {'name': 'Apply coupon code', 'module': 'Checkout', 'browser': 'Firefox'},
                {'name': 'Complete checkout', 'module': 'Checkout', 'browser': 'Safari'}
            ],
            'payments': [
                {'name': 'Payment with saved card', 'module': 'Payments', 'browser': 'Edge'},
                {'name': 'Payment with new card', 'module': 'Payments', 'browser': 'Chrome'}
            ],
            'search': [
                {'name': 'Search with keywords', 'module': 'Search', 'browser': 'Chrome'},
                {'name': 'Search with empty query', 'module': 'Search', 'browser': 'Safari'}
            ],
            'profile': [
                {'name': 'User profile update', 'module': 'Profile', 'browser': 'Chrome'}
            ],
            'dashboard': [
                {'name': 'Dashboard load time', 'module': 'Dashboard', 'browser': 'Firefox'}
            ]
        }

        module = config.get('module', 'all')
        browsers = config.get('browsers', ['Chrome', 'Firefox'])
        
        test_cases = []
        
        if module == 'All modules' or not module:
            tests = [t for tests_list in all_tests.values() for t in tests_list]
        else:
            module_key = module.lower().split()[0]
            tests = all_tests.get(module_key, [])
        
        # Expand test cases for selected browsers
        for test in tests:
            for browser in browsers:
                test_case = test.copy()
                test_case['browser'] = browser
                test_cases.append(test_case)
        
        return test_cases

    async def _execute_test(self, test_case, config):
        """
        Execute individual test case using Playwright
        This is a mock implementation - in production, this would execute actual Playwright tests
        """
        # Simulate test execution
        import random
        
        await asyncio.sleep(random.uniform(1, 3))  # Simulate test duration
        
        # Mock test result - 85% pass rate
        passed = random.random() > 0.15
        
        return {
            'status': 'passed' if passed else 'failed',
            'duration': random.uniform(0.5, 5.0),
            'error': 'Element not found' if not passed else None
        }

    def get_run_status(self, run_id):
        """Get current status of a running test"""
        return self.running_tests.get(run_id, None)

    def stop_run(self, run_id, app):
        """Stop a running test"""
        with app.app_context():
            test_run = TestRun.query.filter_by(run_id=run_id).first()
            if test_run and test_run.status == 'running':
                test_run.status = 'stopped'
                test_run.completed_at = datetime.utcnow()
                db.session.commit()
            
            self.running_tests[run_id]['status'] = 'stopped'
            
            return True


# Global test runner instance
test_runner = PlaywrightTestRunner()
