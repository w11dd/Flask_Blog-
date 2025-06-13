Blog w Flask - Dokumentacja
_____________________________________________________________

Opis projektu

Prosty system blogowy z funkcjonalnościami:
Publikowanie i zarządzanie postami
System komentarzy
Panel administracyjny
Autentykacja użytkowników
_____________________________________________________________

Wymagania systemowe

Python 3.8+
SQLite
Biblioteki wymienione w requirements.txt
_____________________________________________________________

Instalacja
Sklonuj repozytorium:

bash
git clone 
cd blog-flask


Utwórz i aktywuj środowisko wirtualne:

bash
python -m venv venv
# Linux/Mac:
source venv/bin/activate
# Windows:
.\venv\Scripts\activate
Zainstaluj zależności:

bash
pip install -r requirements.txt
_____________________________________________________________

Skonfiguruj aplikację:

Ustaw zmienne środowiskowe (SECRET_KEY, DATABASE_URL itp.)

Uruchomienie
python app.py

Aplikacja będzie dostępna pod adresem: http://localhost:5000
___________________________________________________________

Struktura projektu
text
blog-flask/
│
├── app.py                    # Inicjalizacja aplikacji
├── models.py                 # Modele danych
├── extensions.py             # Rozszerzenia (SQLAlchemy, LoginManager itp.)
│
├── routes/                   # Blueprinty (moduły funkcjonalne)
│   ├── auth.py                 # Autentykacja
│   ├── main.py                 # Główne funkcje
│   └── posts.py                # Zarządzanie postami
│
├── templates/                # Szablony HTML
│   ├── admin/                # Panel admina
│   │   ├── dashboard.html
│   │   ├── users.html
│   │   ├── posts.html
│   │   └── comments.html
│   │
│   ├── posts/                # Szablony postów
│   │   ├── create_posts.html
│   │   ├── edit_posts.html
│   │   ├── list_posts.html
│   │   └── view_posts.html
│   │            
│   ├── login.html            # Szablony autentykacji
│   ├── register.html         # Szablony rejestracji    
│   ├── base.html             # Szablon bazowy
│   ├── navbar.html           # Fragment nawigacji
│   ├── main.html             # Strona główna
│   ├── profile.html          # Strona profilu
│   └── about.html            # Strona "O mnie"
│
└── static/                   # Zasoby statyczne
│   ├── css/                  # Style CSS
│   ├── js/                   # Skrypty JavaScript
│   └── images/               # Obrazy
│
instance/                     # Pliki instancji (konfiguracja, baza danych)
│   └── blog.db                   # Plik bazy danych SQLite
│
├── requirements.txt              # Wymagane zależności
└── README.md                     # Dokumentacja projektu

____________________________________________

Funkcjonalności

Dla użytkowników:
Przeglądanie postów
Dodawanie komentarzy
Rejestracja i logowanie

Dla administratorów:
Zarządzanie postami
Moderacja komentarzy
Zarządzanie użytkownikami
Statystyki bloga

____________________________________________

Autor
[Alexey Solopov]
[solopal_aehit@students.vizja.pl]

EXTRA
4. Dodaj testy jednostkowe i integracyjne
Stwórz plik tests/test_api.py i przetestuj kluczowe endpointy.

5. Wdróż aplikację
Lokalnie: Użyj gunicorn do uruchomienia produkcyjnego:
bash
pip install gunicorn
gunicorn -w 4 app:app
Na serwerze: Skonfiguruj NGINX + Gunicorn lub użyj platformy jak Heroku/Render.

6. Zadbaj o bezpieczeństwo
Dodaj walidację danych wejściowych (np. przy rejestracji).
Wprowadź limity zapytań (np. flask-limiter).

Użyj HTTPS (certyfikat Let’s Encrypt).
7. Zoptymalizuj aplikację
Dodaj cache (np. flask-caching dla często używanych endpointów).
Wykorzystaj asynchroniczność (Celery dla długich zadań).

