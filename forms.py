from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo

class LoginForm(FlaskForm):
    """
    Formularz logowania użytkownika.
    Zawiera pola:
    - email (wymagany, walidacja formatu)
    - hasło (wymagane)
    - opcję zapamiętania sesji
    """
    email = StringField('Email', 
                      validators=[DataRequired(message='Pole wymagane'), 
                                 Email(message='Nieprawidłowy format email')],
                      render_kw={"placeholder": "Twój email"})
    password = PasswordField('Hasło', 
                           validators=[DataRequired(message='Pole wymagane')],
                           render_kw={"placeholder": "Twoje hasło"})
    remember = BooleanField('Zapamiętaj mnie')
    submit = SubmitField('Zaloguj się', render_kw={"class": "btn btn-primary"})


class RegistrationForm(FlaskForm):
    """
    Formularz rejestracji nowego użytkownika.
    Wymagania:
    - nazwa użytkownika (3-50 znaków)
    - email (wymagany, walidacja formatu)
    - hasło (min. 6 znaków)
    - potwierdzenie hasła (musi być identyczne)
    """
    username = StringField('Nazwa użytkownika',
                         validators=[DataRequired(message='Pole wymagane'),
                                    Length(min=3, max=50, message='Wymagane 3-50 znaków')],
                         render_kw={"placeholder": "Wybierz nazwę"})
    email = StringField('Email',
                      validators=[DataRequired(message='Pole wymagane'),
                                 Email(message='Nieprawidłowy format email')],
                      render_kw={"placeholder": "Twój email"})
    password = PasswordField('Hasło',
                           validators=[DataRequired(message='Pole wymagane'),
                                      Length(min=6, message='Minimum 6 znaków')],
                           render_kw={"placeholder": "Wprowadź hasło"})
    confirm_password = PasswordField('Potwierdź hasło',
                                   validators=[DataRequired(message='Pole wymagane'),
                                              EqualTo('password', message='Hasła muszą być identyczne')],
                                   render_kw={"placeholder": "Powtórz hasło"})
    submit = SubmitField('Zarejestruj się', render_kw={"class": "btn btn-success"})


class PostForm(FlaskForm):
    """
    Formularz tworzenia/edycji posta.
    Zawiera:
    - tytuł (max 120 znaków)
    - treść (wymagana)
    - opcjonalne tagi
    - przyciski publikacji i zapisu szkicu
    """
    title = StringField('Tytuł',
                      validators=[DataRequired(message='Pole wymagane'),
                                 Length(max=120, message='Maksymalnie 120 znaków')],
                      render_kw={"placeholder": "Tytuł posta"})
    content = TextAreaField('Treść',
                          validators=[DataRequired(message='Pole wymagane')],
                          render_kw={"placeholder": "Treść posta", "rows": 10})
    tags = StringField('Tagi (oddziel przecinkami)',
                      render_kw={"placeholder": "np. python, flask, web"})
    submit = SubmitField('Opublikuj', render_kw={"class": "btn btn-primary"})
    save_draft = SubmitField('Zapisz szkic', render_kw={"class": "btn btn-secondary"})


class CommentForm(FlaskForm):
    """
    Formularz dodawania komentarza.
    Wymagania:
    - treść (2-500 znaków)
    - wbudowana ochrona CSRF
    """
    content = TextAreaField('Komentarz',
                          validators=[DataRequired(message='Pole wymagane'),
                                    Length(min=2, max=500, message='Wymagane 2-500 znaków')],
                          render_kw={"placeholder": "Twój komentarz...", "rows": 4})
    submit = SubmitField('Dodaj komentarz', render_kw={"class": "btn btn-sm btn-outline-primary"})

    class Meta:
        csrf = True


class PasswordResetRequestForm(FlaskForm):
    """
    Formularz żądania resetu hasła.
    Wymaga podania prawidłowego adresu email.
    """
    email = StringField('Email',
                      validators=[DataRequired(message='Pole wymagane'),
                                 Email(message='Nieprawidłowy format email')],
                      render_kw={"placeholder": "Twój email"})
    submit = SubmitField('Wyślij link resetujący', render_kw={"class": "btn btn-warning"})


class PasswordResetForm(FlaskForm):
    """
    Formularz resetowania hasła.
    Wymagania:
    - nowe hasło (min. 6 znaków)
    - potwierdzenie nowego hasła
    """
    password = PasswordField('Nowe hasło',
                           validators=[DataRequired(message='Pole wymagane'),
                                      Length(min=6, message='Minimum 6 znaków')],
                           render_kw={"placeholder": "Nowe hasło"})
    confirm_password = PasswordField('Potwierdź nowe hasło',
                                   validators=[DataRequired(message='Pole wymagane'),
                                              EqualTo('password', message='Hasła muszą być identyczne')],
                                   render_kw={"placeholder": "Powtórz hasło"})
    submit = SubmitField('Zresetuj hasło', render_kw={"class": "btn btn-success"})