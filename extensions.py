from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import humanize  # For humanize filter

# Inicjalizacja rozszerzeń
db = SQLAlchemy()

def register_template_filters(app):
    """
    Rejestruje niestandardowe filtry szablonów w aplikacji Flask
    
    Dodane filtry:
    - datetimeformat: formatuje datę do czytelnej postaci
    - humanize: konwertuje datę na przyjazną formę (np. '5 minut temu')
    """
    
    @app.template_filter('datetimeformat')
    def datetimeformat(value, format='%Y-%m-%d %H:%M'):
        """Formatuje obiekt datetime do stringa"""
        if value is None:
            return ""
        return value.strftime(format)
    
    @app.template_filter('humanize')
    def humanize_time(dt):
        """Konwertuje datę na przyjazną formę (np. '5 minut temu')"""
        return humanize.naturaltime(dt)

def create_admin(app):
    """
    Inicjalizuje głównego administratora i przykładowe dane w bazie danych.
    
    Funkcja wykonuje następujące operacje:
    1. Tworzy tabele w bazie danych jeśli nie istnieją
    2. Rejestruje filtry szablonów
    3. Sprawdza czy istnieje główny administrator (ID=1)
    4. Jeśli nie istnieje - tworzy nowego administratora
    5. Jeśli istnieje - aktualizuje jego dane
    6. Dodaje przykładowe posty jeśli baza jest pusta
    
    Zwraca:
        User: Obiekt użytkownika administratora
    
    Wyjątki:
        Exception: W przypadku błędu podczas operacji na bazie danych
    """
    from models import User, Post
    
    try:
        # Utworzenie tabel w bazie danych i rejestracja filtrów
        with app.app_context():
            db.create_all()
            register_template_filters(app)

        # Sprawdzenie czy istnieje główny administrator
        admin = User.query.get(1)
        
        if not admin:
            # Tworzenie nowego administratora
            admin = User(
                id=1,
                username='Admin',
                email='admin@example.com',
                is_admin=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("✅ Główny administrator został utworzony (ID=1)")
        else:
            # Aktualizacja danych istniejącego administratora
            needs_update = False
            if not admin.is_admin:
                admin.is_admin = True
                needs_update = True
            if admin.username != 'Admin':
                admin.username = 'Admin'
                needs_update = True
            if admin.email != 'admin@example.com':
                admin.email = 'admin@example.com'
                needs_update = True
                
            if needs_update:
                db.session.commit()
                print("✅ Dane administratora zostały zaktualizowane")
        
        # Dodanie przykładowych postów jeśli baza jest pusta
        if Post.query.count() == 0:
            sample_posts = [
                Post(
                    title='Pierwszy post na blogu',
                    content='Flask to lekki framework Pythona idealny do małych projektów...',
                    user_id=1,
                    created_at=datetime.utcnow()
                ),
                Post(
                    title='Flask jest świetny!',
                    content='Chcesz rozpocząć z Flaskiem? Zainstaluj go przez pip install flask...',
                    user_id=1,
                    created_at=datetime.utcnow()
                ),
                Post(
                    title='Python dla początkujących',
                    content='Flask REST API? Tak! Użyj Flask-RESTful do szybkiego budowania endpointów...',
                    user_id=1,
                    created_at=datetime.utcnow()
                )
            ]
            
            db.session.add_all(sample_posts)
            db.session.commit()
            print("✅ Dodano przykładowe posty")
        
        return admin
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Wystąpił błąd podczas inicjalizacji administratora: {str(e)}")
        raise