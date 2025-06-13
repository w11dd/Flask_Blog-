import pytest
from app import app as flask_app
from extensions import db
from models import User, Post, Comment 
from werkzeug.security import generate_password_hash
from flask import url_for

@pytest.fixture
def app():
    """Konfiguracja aplikacji testowej z lepszym czyszczeniem"""
    # Konfiguracja testowa
    flask_app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,
        'SERVER_NAME': 'localhost.localdomain',
        'APPLICATION_ROOT': '/',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False
    })

    # Utworzenie i czyszczenie bazy danych
    with flask_app.app_context():
        db.drop_all()  # Najpierw wyczyść na wypadek poprzednich testów
        db.create_all()
        
        yield flask_app
        
        # Dokładne czyszczenie po testach
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """Klient testowy z czyszczeniem sesji"""
    with app.test_client() as client:
        with app.app_context():
            yield client
        # Wyczyść sesję po teście
        with client.session_transaction() as sess:
            sess.clear()

@pytest.fixture
def test_user(app):
    """Przykładowy użytkownik testowy z lepszą obsługą błędów"""
    with app.app_context():
        # Najpierw usuń istniejącego użytkownika jeśli istnieje
        User.query.filter_by(email='test@example.com').delete()
        db.session.commit()
        
        user = User(
            username='testuser',
            email='test@example.com',
            password_hash=generate_password_hash('TestPassword123'),
            is_admin=False
        )
        db.session.add(user)
        db.session.commit()
        
        yield user
        
        # Bezpieczne usuwanie
        try:
            db.session.delete(user)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            pytest.fail(f"Failed to delete test user: {str(e)}")

@pytest.fixture
def admin_user(app):
    """Przykładowy administrator z spójnymi danymi testowymi"""
    with app.app_context():
        # Najpierw usuń istniejącego admina jeśli istnieje
        User.query.filter_by(email='admin@example.com').delete()
        db.session.commit()
        
        user = User(
            username='admin',
            email='admin@example.com',
            password_hash=generate_password_hash('AdminPassword123'),  
            is_admin=True
        )
        db.session.add(user)
        db.session.commit()
        
        yield user
        
        # Bezpieczne usuwanie
        try:
            db.session.delete(user)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            pytest.fail(f"Failed to delete admin user: {str(e)}")


@pytest.fixture
def auth_client(client, test_user):
    """Authenticated client fixture"""
    with client:
        client.post(url_for('auth.login'),
            data={
                'email': test_user.email,
                'password': 'TestPassword123'
            },
            follow_redirects=True)
        yield client


from flask import url_for
from models import Post, Comment  # Add these if you use them in tests


@pytest.fixture
def admin_auth_client(client, admin_user):
    """Authenticated admin client fixture"""
    with client:
        response = client.post(url_for('auth.login'),
            data={
                'email': admin_user.email,
                'password': 'AdminPassword123'
            },
            follow_redirects=True)
        assert response.status_code == 200  # Verify login succeeded
        yield client