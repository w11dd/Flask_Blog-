from flask import Blueprint, render_template, redirect, url_for, flash, session, abort
from werkzeug.security import generate_password_hash, check_password_hash
from forms import LoginForm, RegistrationForm
from models import User
from extensions import db
from functools import wraps
from flasgger import swag_from

auth_bp = Blueprint('auth', __name__)

def admin_required(f):
    """Dekorator wymagający uprawnień administratora"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Proszę się zalogować.', 'warning')
            return redirect(url_for('auth.login'))
        
        user = User.query.get(session['user_id'])
        if not user or not user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/login', methods=['GET', 'POST'])
@swag_from({
    'tags': ['Authentication'],
    'description': 'Logowanie użytkownika',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'email': {'type': 'string', 'example': 'user@example.com'},
                    'password': {'type': 'string', 'example': 'haslo123'}
                },
                'required': ['email', 'password']
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Logowanie udane - przekierowanie',
            'examples': {
                'application/json': {'message': 'Zalogowano pomyślnie!'}
            }
        },
        401: {
            'description': 'Błąd logowania',
            'examples': {
                'application/json': {'error': 'Nieprawidłowy email lub hasło'}
            }
        }
    }
})
def login():
    """Obsługa logowania użytkowników"""
    if 'user_id' in session:
        return redirect(url_for('main.home'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user and check_password_hash(user.password_hash, form.password.data):
            session['user_id'] = user.id
            session['username'] = user.username
            session['is_admin'] = user.is_admin
            
            flash('Zalogowano pomyślnie!', 'success')
            
            if user.is_admin:
                return redirect(url_for('main.admin_dashboard'))
            return redirect(url_for('main.home'))
        
        flash('Nieprawidłowy email lub hasło', 'danger')
    return render_template('login.html', form=form)

@auth_bp.route('/logout')
@swag_from({
    'tags': ['Authentication'],
    'description': 'Wylogowanie użytkownika',
    'responses': {
        200: {
            'description': 'Wylogowano pomyślnie - przekierowanie',
            'examples': {
                'application/json': {'message': 'Wylogowano pomyślnie'}
            }
        }
    }
})
def logout():
    """Wylogowanie użytkownika i wyczyszczenie sesji"""
    session.clear()
    flash('Wylogowano pomyślnie.', 'success')
    return redirect(url_for('main.home'))

@auth_bp.route('/profile')
@swag_from({
    'tags': ['User'],
    'description': 'Wyświetlenie profilu użytkownika',
    'security': [{'session': []}],
    'responses': {
        200: {
            'description': 'Dane profilu użytkownika',
            'examples': {
                'application/json': {
                    'username': 'jan_kowalski',
                    'email': 'jan@example.com',
                    'is_admin': False
                }
            }
        },
        401: {
            'description': 'Użytkownik niezalogowany',
            'examples': {
                'application/json': {'error': 'Proszę się zalogować'}
            }
        }
    }
})
def profile():
    """Wyświetlenie profilu użytkownika"""
    if 'user_id' not in session:
        flash('Proszę się zalogować.', 'warning')
        return redirect(url_for('auth.login'))
    
    user = User.query.get(session['user_id'])
    if not user:
        session.clear()
        flash('Użytkownik nie istnieje.', 'danger')
        return redirect(url_for('auth.login'))
    
    return render_template('profile.html',
                         username=user.username,
                         email=user.email,
                         is_admin=user.is_admin)

@auth_bp.route('/admin/users')
@admin_required
@swag_from({
    'tags': ['Admin'],
    'description': 'Lista wszystkich użytkowników (tylko dla admina)',
    'security': [{'session': []}],
    'responses': {
        200: {
            'description': 'Lista użytkowników',
            'examples': {
                'application/json': [
                    {'id': 1, 'username': 'admin', 'email': 'admin@example.com', 'is_admin': True},
                    {'id': 2, 'username': 'user1', 'email': 'user1@example.com', 'is_admin': False}
                ]
            }
        },
        403: {
            'description': 'Brak uprawnień administratora'
        }
    }
})
def admin_users():
    """Wyświetlenie listy wszystkich użytkowników (tylko dla administratora)"""
    users = User.query.order_by(User.id).all()
    return render_template('admin/users.html', users=users)

@auth_bp.route('/register', methods=['GET', 'POST'])
@swag_from({
    'tags': ['Authentication'],
    'description': 'Rejestracja nowego użytkownika',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'username': {'type': 'string', 'example': 'jan_kowalski'},
                    'email': {'type': 'string', 'example': 'jan@example.com'},
                    'password': {'type': 'string', 'example': 'haslo123'},
                    'confirm_password': {'type': 'string', 'example': 'haslo123'}
                },
                'required': ['username', 'email', 'password', 'confirm_password']
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Rejestracja udana - przekierowanie',
            'examples': {
                'application/json': {'message': 'Konto zostało utworzone!'}
            }
        },
        400: {
            'description': 'Błąd rejestracji',
            'examples': {
                'application/json': {'error': 'Email lub nazwa użytkownika jest już zajęta'}
            }
        }
    }
})
def register():
    """Rejestracja nowego użytkownika"""
    if 'user_id' in session:
        return redirect(url_for('main.home'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash('Email jest już zajęty.', 'danger')
            return redirect(url_for('auth.register'))
        
        if User.query.filter_by(username=form.username.data).first():
            flash('Nazwa użytkownika jest już zajęta.', 'danger')
            return redirect(url_for('auth.register'))
        
        user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=generate_password_hash(form.password.data),
            is_admin=False
        )
        
        db.session.add(user)
        db.session.commit()
        flash('Konto zostało utworzone! Możesz się zalogować.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html', form=form)