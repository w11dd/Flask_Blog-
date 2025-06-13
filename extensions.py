from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

def create_admin(app):
    """
    Inicjalizuje głównego administratora i przykładowe dane w bazie danych.
    
    Funkcja wykonuje następujące operacje:
    1. Tworzy tabele w bazie danych jeśli nie istnieją
    2. Sprawdza czy istnieje główny administrator (ID=1)
    3. Jeśli nie istnieje - tworzy nowego administratora
    4. Jeśli istnieje - aktualizuje jego dane
    5. Dodaje przykładowe posty jeśli baza jest pusta
    
    Zwraca:
        User: Obiekt użytkownika administratora
    
    Wyjątki:
        Exception: W przypadku błędu podczas operacji na bazie danych
    """
    from models import User, Post
    
    try:
        # Utworzenie tabel w bazie danych
        with app.app_context():
            db.create_all()

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