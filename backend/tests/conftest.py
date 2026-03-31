"""
Sample Playwright tests for QA Dashboard
These tests can be run with: pytest tests/
"""

import pytest
from playwright.sync_api import sync_playwright, expect
import os


class TestAuthentication:
    """Test cases for authentication/login functionality"""

    @pytest.fixture(scope="function")
    def browser_context(self):
        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context()
            yield context
            context.close()
            browser.close()

    def test_login_with_valid_credentials(self, browser_context):
        """Test login with valid credentials"""
        page = browser_context.new_page()
        
        # Navigate to login page
        page.goto("https://example.com/login")
        
        # Fill username and password
        page.fill("input[name='username']", "testuser@example.com")
        page.fill("input[name='password']", "password123")
        
        # Click login button
        page.click("button:has-text('Login')")
        
        # Verify redirect to dashboard
        expect(page).to_have_url("**/dashboard")
        page.close()

    def test_login_with_invalid_password(self, browser_context):
        """Test login with invalid password"""
        page = browser_context.new_page()
        
        page.goto("https://example.com/login")
        page.fill("input[name='username']", "testuser@example.com")
        page.fill("input[name='password']", "wrongpassword")
        page.click("button:has-text('Login')")
        
        # Verify error message appears
        error_msg = page.locator(".error-message")
        expect(error_msg).to_be_visible()
        page.close()

    def test_password_reset_flow(self, browser_context):
        """Test password reset functionality"""
        page = browser_context.new_page()
        
        page.goto("https://example.com/login")
        page.click("a:has-text('Forgot password')")
        
        expect(page).to_have_url("**/reset-password")
        page.close()


class TestCheckout:
    """Test cases for checkout functionality"""

    @pytest.fixture(scope="function")
    def browser_context(self):
        with sync_playwright() as p:
            browser = p.firefox.launch()
            context = browser.new_context()
            yield context
            context.close()
            browser.close()

    def test_add_to_cart_as_guest(self, browser_context):
        """Test adding item to cart as guest user"""
        page = browser_context.new_page()
        
        page.goto("https://example.com/products")
        page.click("button:has-text('Add to Cart')")
        
        # Verify item was added
        cart_count = page.locator(".cart-count")
        expect(cart_count).to_have_text("1")
        page.close()

    def test_apply_coupon_code(self, browser_context):
        """Test applying coupon code"""
        page = browser_context.new_page()
        
        page.goto("https://example.com/checkout")
        page.fill("input[name='coupon']", "SAVE10")
        page.click("button:has-text('Apply')")
        
        # Verify discount applied
        discount = page.locator(".discount-amount")
        expect(discount).to_be_visible()
        page.close()

    def test_complete_checkout(self, browser_context):
        """Test completing checkout process"""
        page = browser_context.new_page()
        
        page.goto("https://example.com/checkout")
        
        # Fill checkout form
        page.fill("input[name='email']", "user@example.com")
        page.fill("input[name='card']", "4111111111111111")
        page.fill("input[name='expiry']", "12/25")
        page.fill("input[name='cvc']", "123")
        
        # Complete checkout
        page.click("button:has-text('Complete Purchase')")
        
        # Verify order confirmation
        expect(page).to_have_url("**/order-confirmation")
        page.close()


class TestSearch:
    """Test cases for search functionality"""

    @pytest.fixture(scope="function")
    def browser_context(self):
        with sync_playwright() as p:
            browser = p.webkit.launch()
            context = browser.new_context()
            yield context
            context.close()
            browser.close()

    def test_search_with_keywords(self, browser_context):
        """Test searching with valid keywords"""
        page = browser_context.new_page()
        
        page.goto("https://example.com")
        page.fill("input[name='search']", "laptop")
        page.press("input[name='search']", "Enter")
        
        # Verify search results
        results = page.locator(".search-result")
        expect(results.first).to_be_visible()
        page.close()

    def test_search_with_empty_query(self, browser_context):
        """Test search with empty query"""
        page = browser_context.new_page()
        
        page.goto("https://example.com")
        search_input = page.locator("input[name='search']")
        
        # Try to submit empty search
        page.press("input[name='search']", "Enter")
        
        # Verify error or empty state
        empty_state = page.locator(".empty-results")
        expect(empty_state).to_be_visible()
        page.close()


class TestUserProfile:
    """Test cases for user profile functionality"""

    @pytest.fixture(scope="function")
    def browser_context(self):
        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context()
            yield context
            context.close()
            browser.close()

    def test_user_profile_update(self, browser_context):
        """Test updating user profile"""
        page = browser_context.new_page()
        
        page.goto("https://example.com/profile")
        
        # Update profile information
        page.fill("input[name='firstname']", "John")
        page.fill("input[name='lastname']", "Doe")
        page.click("button:has-text('Save')")
        
        # Verify success message
        success_msg = page.locator(".success-message")
        expect(success_msg).to_be_visible()
        page.close()


class TestPayments:
    """Test cases for payment functionality"""

    @pytest.fixture(scope="function")
    def browser_context(self):
        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context()
            yield context
            context.close()
            browser.close()

    def test_payment_with_saved_card(self, browser_context):
        """Test payment using saved card"""
        page = browser_context.new_page()
        
        page.goto("https://example.com/checkout/payment")
        page.click("input[value='saved-card']")
        page.click("button:has-text('Pay Now')")
        
        # Verify payment success
        expect(page).to_have_url("**/payment-success")
        page.close()

    def test_payment_with_new_card(self, browser_context):
        """Test payment with new card"""
        page = browser_context.new_page()
        
        page.goto("https://example.com/checkout/payment")
        page.click("input[value='new-card']")
        
        # Fill card details
        page.fill("input[name='card-number']", "4111111111111111")
        page.fill("input[name='expiry']", "12/25")
        page.fill("input[name='cvv']", "123")
        
        page.click("button:has-text('Pay Now')")
        expect(page).to_have_url("**/payment-success")
        page.close()


class TestDashboard:
    """Test cases for dashboard functionality"""

    @pytest.fixture(scope="function")
    def browser_context(self):
        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context()
            yield context
            context.close()
            browser.close()

    def test_dashboard_load_time(self, browser_context):
        """Test dashboard loads within acceptable time"""
        page = browser_context.new_page()
        
        import time
        start_time = time.time()
        page.goto("https://example.com/dashboard")
        
        # Wait for main content to load
        page.wait_for_selector(".dashboard-content", timeout=5000)
        
        load_time = time.time() - start_time
        
        # Assert load time is acceptable (less than 3 seconds)
        assert load_time < 3.0, f"Dashboard load time exceeded: {load_time}s"
        page.close()


# Pytest configuration
@pytest.fixture(scope="session")
def setup_test_environment():
    """Setup test environment"""
    # Set test environment variables
    os.environ['TEST_ENV'] = 'staging'
    os.environ['BASE_URL'] = 'https://example.com'
    yield
    # Cleanup after tests


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
