from extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


class User(db.Model, UserMixin):
    """Model użytkownika systemu.
    
    Attributes:
        id (int): Unikalny identyfikator użytkownika
        username (str): Nazwa użytkownika (unikalna)
        email (str): Adres email (unikalny)
        password_hash (str): Zahashowane hasło
        created_at (datetime): Data rejestracji
        is_admin (bool): Czy użytkownik ma uprawnienia administratora
    """
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False)

    # Relacje z postami i komentarzami
    posts = db.relationship('Post', backref='post_author', lazy=True)
    comments = db.relationship('Comment', backref='comment_author', lazy=True)
    
    def set_password(self, password):
        """Generuje i ustawia zahashowane hasło dla użytkownika.
        
        Args:
            password (str): Hasło w postaci tekstowej
        """
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Sprawdza czy podane hasło zgadza się z zahashowanym.
        
        Args:
            password (str): Hasło w postaci tekstowej do weryfikacji
            
        Returns:
            bool: True jeśli hasła się zgadzają, False w przeciwnym wypadku
        """
        return check_password_hash(self.password_hash, password)
    
    @classmethod
    def get_admin(cls):
        """Pobiera użytkownika z uprawnieniami administratora.
        
        Returns:
            User: Instancja użytkownika administratora
        """
        return cls.query.get(1)


class Post(db.Model):
    """Model wpisu/blog posta.
    
    Attributes:
        id (int): Unikalny identyfikator posta
        title (str): Tytuł posta
        content (str): Treść posta
        created_at (datetime): Data utworzenia
        updated_at (datetime): Data ostatniej aktualizacji
        user_id (int): ID użytkownika-autora
    """
    __tablename__ = 'posts'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relacja z komentarzami (usuwane kaskadowo)
    comments = db.relationship('Comment', backref='comment_post', lazy=True, cascade='all, delete-orphan')


class Comment(db.Model):
    """Model komentarza do posta.
    
    Attributes:
        id (int): Unikalny identyfikator komentarza
        content (str): Treść komentarza
        created_at (datetime): Data utworzenia
        updated_at (datetime): Data ostatniej aktualizacji
        user_id (int): ID użytkownika-autora komentarza
        post_id (int): ID posta do którego dodano komentarz
    """
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)