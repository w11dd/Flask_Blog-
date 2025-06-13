import pytest
from flask import url_for
from models import Post, User, Comment
from extensions import db

# Test Admin Dashboard
def test_admin_dashboard_access(admin_auth_client, app):
    """Test admin dashboard access with admin user"""
    with app.app_context():
        response = admin_auth_client.get(url_for('main.admin_dashboard'))
        assert response.status_code == 200
        assert 'Panel administracyjny' in response.data.decode('utf-8')
        assert 'Statystyki' in response.data.decode('utf-8')

def test_admin_dashboard_denied(auth_client, app):
    """Test admin dashboard access denied for regular user"""
    with app.app_context():
        response = auth_client.get(url_for('main.admin_dashboard'))
        assert response.status_code == 403

# Test User Management
def test_manage_users_access(admin_auth_client, test_user, app):
    """Test manage users page access with admin user"""
    with app.app_context():
        response = admin_auth_client.get(url_for('main.manage_users'))
        assert response.status_code == 200
        assert 'Zarz±dzanie użytkownikami' in response.data.decode('utf-8')
        assert test_user.username.encode('utf-8') in response.data

def test_toggle_user_status(admin_auth_client, test_user, app):
    """Test toggling user admin status"""
    with app.app_context():
        # Test making user admin
        response = admin_auth_client.post(
            url_for('main.toggle_user_status', user_id=test_user.id),
            data={'toggle_admin': 'on'},
            follow_redirects=True
        )
        assert response.status_code == 200
        assert 'Uprawnienia administratora nadano' in response.data.decode('utf-8')
        
        updated_user = User.query.get(test_user.id)
        assert updated_user.is_admin is True
        
        # Test removing admin privileges
        response = admin_auth_client.post(
            url_for('main.toggle_user_status', user_id=test_user.id),
            data={'toggle_admin': 'on'},
            follow_redirects=True
        )
        assert 'Uprawnienia administratora cofnięto' in response.data.decode('utf-8')
        assert User.query.get(test_user.id).is_admin is False

def test_toggle_own_status(admin_auth_client, admin_user, app):
    """Test preventing admin from toggling their own status"""
    with app.app_context():
        response = admin_auth_client.post(
            url_for('main.toggle_user_status', user_id=admin_user.id),
            data={'toggle_admin': 'on'},
            follow_redirects=True
        )
        assert response.status_code == 200
        assert 'Nie możesz modyfikować własnego konta' in response.data.decode('utf-8')

# Test Post Management
def test_manage_posts(admin_auth_client, test_user, app):
    """Test post management functionality"""
    with app.app_context():
        # Create a test post with user_id
        post = Post(title='Test Post', content='Test Content', user_id=test_user.id)
        db.session.add(post)
        db.session.commit()
        
        # Test access to manage posts
        response = admin_auth_client.get(url_for('main.manage_posts'))
        assert response.status_code == 200
        assert 'Zarz±dzanie postami' in response.data.decode('utf-8')
        assert b'Test Post' in response.data
        
        # Test post deletion
        response = admin_auth_client.post(
            url_for('main.delete_post', post_id=post.id),
            follow_redirects=True
        )
        assert response.status_code == 200
        assert 'Post został usunięty' in response.data.decode('utf-8')
        assert Post.query.get(post.id) is None

# Test Comment Management
def test_manage_comments(admin_auth_client, test_user, app):
    """Test comment management functionality"""
    with app.app_context():
        # Create a test post and comment
        post = Post(title='Test Post', content='Test Content', user_id=test_user.id)
        comment = Comment(content='Test Comment', post_id=post.id, user_id=test_user.id)
        db.session.add_all([post, comment])
        db.session.commit()
        
        # Test access to manage comments
        response = admin_auth_client.get(url_for('main.manage_comments'))
        assert response.status_code == 200
        assert 'Zarz±dzanie komentarzami' in response.data.decode('utf-8')
        assert b'Test Comment' in response.data
        
        # Test comment deletion
        response = admin_auth_client.post(
            url_for('main.delete_comment', comment_id=comment.id),
            follow_redirects=True
        )
        assert response.status_code == 200
        assert 'Komentarz został usunięty' in response.data.decode('utf-8')
        assert Comment.query.get(comment.id) is None

# Test Public Routes
def test_home_page(client, test_user, app):
    """Test home page with posts"""
    with app.app_context():
        # Create a test post with user_id
        post = Post(title='Public Post', content='Public Content', user_id=test_user.id)
        db.session.add(post)
        db.session.commit()
        
        response = client.get(url_for('main.home'))
        assert response.status_code == 200
        assert b'Public Post' in response.data
        assert b'Public Content' in response.data

def test_about_page(client, app):
    """Test about page"""
    with app.app_context():
        response = client.get(url_for('main.about'))
        assert response.status_code == 200
        assert 'O mnie' in response.data.decode('utf-8')

# Test Admin Required Decorator
def test_admin_required_decorator(auth_client, admin_auth_client, app):
    """Test that admin routes are protected"""
    admin_routes = [
        'main.admin_dashboard',
        'main.manage_users',
        'main.manage_posts',
        'main.manage_comments'
    ]
    
    with app.app_context():
        # Test as regular user
        for route in admin_routes:
            response = auth_client.get(url_for(route))
            assert response.status_code == 403
        
        # Test as admin user
        for route in admin_routes:
            response = admin_auth_client.get(url_for(route))
            assert response.status_code == 200

# Test Error Cases
def test_delete_nonexistent_post(admin_auth_client, app):
    """Test deleting a post that doesn't exist"""
    with app.app_context():
        response = admin_auth_client.post(
            url_for('main.delete_post', post_id=9999),
            follow_redirects=True
        )
        assert response.status_code == 404

def test_delete_nonexistent_comment(admin_auth_client, app):
    """Test deleting a comment that doesn't exist"""
    with app.app_context():
        response = admin_auth_client.post(
            url_for('main.delete_comment', comment_id=9999),
            follow_redirects=True
        )
        assert response.status_code == 404

def test_toggle_nonexistent_user(admin_auth_client, app):
    """Test toggling status for a user that doesn't exist"""
    with app.app_context():
        response = admin_auth_client.post(
            url_for('main.toggle_user_status', user_id=9999),
            follow_redirects=True
        )
        assert response.status_code == 404