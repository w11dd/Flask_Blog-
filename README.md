# Flask_Blog-Blog w Flask - Dokumentacja
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
git clone https://github.com/w11dd/Flask_Blog-.git
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

flask_Blog/
├── instance/ # Pliki instancji (konfiguracja, baza danych)
│ └── blog.db # Baza danych SQLite
│
├── routes/ # Moduły z trasami (endpointy)
│ ├── auth.py # Autentykacja (logowanie/rejestracja)
│ ├── main.py # Główne trasy
│ └── posts.py # Operacje na postach
│
├── static/ # Zasoby statyczne
│ ├── css/ # Style CSS
│ ├── images/ # Obrazy
│ └── js/ # Skrypty JavaScript
│
├── templates/ # Szablony 
│ ├── admin/ # Panel administracyjny
│ │ ├── comments.html # Zarządzanie komentarzami
│ │ ├── dashboard.html # Pulpit nawigacyjny
│ │ ├── posts.html # Zarządzanie postami
│ │ └── users.html # Zarządzanie użytkownikami
│ │
│ ├── posts/ # Szablony postów
│ │ ├── _posts_list.html # Lista postów (częściowy szablon)
│ │ ├── create_post.html # Tworzenie posta
│ │ ├── edit_comment.html # Edycja komentarza
│ │ ├── edit_post.html # Edycja posta
│ │ ├── list_posts.html # Pełna lista postów
│ │ ├── search_results.html # Wyniki wyszukiwania
│ │ └── view_post.html # Podgląd pojedynczego posta
│ │
│ ├── about.html # Strona "O nas"
│ ├── base.html # Szablon bazowy
│ ├── login.html # Logowanie
│ ├── main.html # Strona główna
│ ├── navbar.html # Pasek nawigacyjny (partial)
│ ├── profile.html # Profil użytkownika
│ └── register.html # Rejestracja
│
├── tests/ # Testy jednostkowe
│ ├── init.py
│ ├── conftest.py # Konfiguracja testów
│ ├── test_auth.py # Testy autentykacji
│ ├── test_main.py # Testy głównych funkcji
│ └── test_posts.py # Testy postów
│
├── app.py # Główny plik aplikacji
├── extensions.py # Rozszerzenia Flask (np. DB, LoginManager)
├── forms.py # Formularze WTForms
├── models.py # Modele SQLAlchemy
├── README.md # Dokumentacja projektu
├── requirements.txt # Wymagane zależności
└── swagger.json # Dokumentacja API (OpenAPI/Swagger)
____________________________________________

Funkcjonalności

Dla użytkowników:
Przeglądanie postów
Dodawanie komentarzy
Rejestracja i logowanie
Wyszukiwanie postów

Dla administratorów:
Zarządzanie postami
Moderacja komentarzy
Zarządzanie użytkownikami
Statystyki bloga

____________________________________________

Autor
[Alexey Solopov]
[solopal_aehit@students.vizja.pl]



