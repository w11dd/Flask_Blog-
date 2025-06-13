from flask import Flask
import os
from extensions import db, create_admin
from flasgger import Swagger

app = Flask(__name__, template_folder='templates')
# Konfiguracja aplikacji
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'tajny-klucz'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_ECHO'] = True  # Pokazuje zapytania SQL w konsoli

# Konfiguracja Swaggera (Flasgger)
app.config['SWAGGER'] = {
    'title': 'Blog API',
    'description': 'Dokumentacja API dla bloga w Flasku',
    'version': '1.0',
    'uiversion': 3,  # Używa Swagger UI 3
    'specs_route': '/api/docs/'  # Endpoint dla dokumentacji
}
swagger = Swagger(app)

db.init_app(app)

def initialize_database():
    """
    Inicjalizuje bazę danych:
    - Tworzy wszystkie tabele
    - Dodaje domyślnego administratora
    - Wyświetla informacje o utworzonym administratorze
    """
    with app.app_context():
        db.create_all()
        
        admin = create_admin(app)
        
        if admin:
            print("\n🔍 Informacje o administratorze:")
            print(f"ID: {admin.id}")
            print(f"Nazwa użytkownika: {admin.username}")
            print(f"Email: {admin.email}")
            print(f"Status admina: {admin.is_admin}\n")
        
        db.session.commit()

# Inicjalizacja bazy danych przy starcie aplikacji
initialize_database()

# Rejestracja modułów aplikacji
from routes.auth import auth_bp
from routes.main import main_bp
from routes.posts import posts_bp

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(main_bp)
app.register_blueprint(posts_bp, url_prefix='/posts')

if __name__ == '__main__':
    app.run(debug=True)