import pytest
from flask import session, url_for
from werkzeug.security import check_password_hash
from models import User
from extensions import db

# Test 1: Test Flask Initialization
def test_flask_init(app):
    """Test checking Flask application initialization"""
    assert app is not None
    assert app.name == 'app'
    assert 'SECRET_KEY' in app.config
    assert app.config['TESTING'] is True

# Test 2: Route Availability
@pytest.mark.parametrize('endpoint,methods', [
    ('auth.login', ['GET', 'POST']),
    ('auth.logout', ['GET']),
    ('auth.register', ['GET', 'POST']),
    ('auth.profile', ['GET']),
    ('auth.admin_users', ['GET']),
])
def test_routes_availability(client, endpoint, methods, app):
    """Test checking route availability"""
    with app.app_context():
        for method in methods:
            try:
                # Use client.open() instead of direct method calls
                response = client.open(url_for(endpoint), method=method)
                assert response.status_code in [200, 302, 401, 403], \
                    f"Unexpected status {response.status_code} for {endpoint} ({method})"
            except Exception as e:
                pytest.fail(f"Error accessing {endpoint} ({method}): {str(e)}")

# Test 3: Authentication Tests
class TestAuthentication:
    """Authentication-related tests"""
    
    def test_register_new_user(self, client, app):
        """Test user registration"""
        with app.app_context():
            # Clean existing user
            User.query.filter_by(email='test@example.com').delete()
            db.session.commit()
            
            response = client.post(url_for('auth.register'),
                data={
                    'username': 'testuser',
                    'email': 'test@example.com',
                    'password': 'TestPassword123',
                    'confirm_password': 'TestPassword123'
                },
                follow_redirects=True)
            
            assert response.status_code == 200
            assert b'Konto zosta' in response.data  # Polish: "Konto zostało utworzone"
            
            user = User.query.filter_by(email='test@example.com').first()
            assert user is not None
            assert user.username == 'testuser'
            assert check_password_hash(user.password_hash, 'TestPassword123')
            
            # Cleanup
            db.session.delete(user)
            db.session.commit()
    
    def test_login_success(self, client, test_user):
        """Test successful login"""
        response = client.post(url_for('auth.login'), 
            data={
                'email': test_user.email,
                'password': 'TestPassword123'
            },
            follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Zalogowano pomy' in response.data  # Polish: "Zalogowano pomyślnie"
        
        with client.session_transaction() as sess:
            assert 'user_id' in sess, "User ID not found in session after login"
            assert sess['user_id'] == test_user.id
    
    def test_login_failure(self, client, test_user):
        """Test failed login"""
        response = client.post(url_for('auth.login'), 
            data={
                'email': test_user.email,
                'password': 'WrongPassword'
            },
            follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Nieprawid' in response.data  # Polish: "Nieprawidłowe dane logowania"
        
        with client.session_transaction() as sess:
            assert 'user_id' not in sess, "User ID found in session after failed login"
    
    def test_logout(self, client, test_user):
        """Test logout"""
        # Login first
        client.post(url_for('auth.login'),
            data={
                'email': test_user.email,
                'password': 'TestPassword123'
            },
            follow_redirects=True)
        
        # Verify login
        with client.session_transaction() as sess:
            assert 'user_id' in sess
        
        # Logout
        response = client.get(url_for('auth.logout'), follow_redirects=True)
        assert response.status_code == 200
        assert b'Wylogowano pomy' in response.data  # Polish: "Wylogowano pomyślnie"
        
        # Verify logout
        with client.session_transaction() as sess:
            assert 'user_id' not in sess

# Test 4: Post Creation
def test_create_post(auth_client, admin_auth_client, app):
    """Test post creation"""
    with app.app_context():
        # Regular user post
        response = auth_client.post('/posts/create',
            data={
                'title': 'Test Post',
                'content': 'Test content'
            },
            follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Test Post' in response.data
        
        # Admin post
        response = admin_auth_client.post('/posts/create',
            data={
                'title': 'Admin Post',
                'content': 'Admin content'
            },
            follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Admin Post' in response.data

# Additional Tests
def test_admin_required_decorator(client, test_user, admin_user, app):
    """Test admin requirement decorator"""
    # Test as regular user
    client.post(url_for('auth.login'),
        data={
            'email': test_user.email,
            'password': 'TestPassword123'
        },
        follow_redirects=True)
    
    response = client.get(url_for('auth.admin_users'), follow_redirects=True)
    assert response.status_code in [403, 302]  # Either forbidden or redirect
    
    # Clear session
    client.get(url_for('auth.logout'))
    
    # Test as admin
    client.post(url_for('auth.login'),
        data={
            'email': admin_user.email,
            'password': 'AdminPassword123'
        },
        follow_redirects=True)
    
    response = client.get(url_for('auth.admin_users'))
    assert response.status_code == 200
    # Check for any indicator of admin page
    assert b'admin' in response.data.lower() or b'zarz' in response.data.lower()

def test_profile_page(auth_client, test_user):
    """Test user profile page"""
    response = auth_client.get(url_for('auth.profile'))
    assert response.status_code == 200
    assert test_user.username.encode() in response.data
    assert test_user.email.encode() in response.data