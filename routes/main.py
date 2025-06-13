from flask import Blueprint, render_template, redirect, url_for, flash, session, abort, request
from models import Post, User, Comment
from extensions import db
from functools import wraps
from flasgger import swag_from

main_bp = Blueprint('main', __name__)

def admin_required(f):
    """Dekorator wymagający uprawnień administratora"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Proszę się zalogować.', 'warning')
            return redirect(url_for('auth.login'))
        
        user = User.query.get(session['user_id'])
        if not user or not user.is_admin:
            print(f"ACCESS DENIED: User {user.username if user else 'None'} tried to access admin panel")
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

@main_bp.route('/admin')
@admin_required
@swag_from({
    'tags': ['Admin'],
    'description': 'Panel administracyjny ze statystykami bloga',
    'security': [{'session': []}],
    'responses': {
        200: {'description': 'Renderuje panel admina'},
        403: {'description': 'Brak uprawnień administratora'}
    }
})
def admin_dashboard():
    """Wyświetla panel administracyjny ze statystykami"""
    stats = {
        'users_count': User.query.count(),
        'posts_count': Post.query.count(),
        'comments_count': Comment.query.count(),
        'latest_users': User.query.order_by(User.id.desc()).limit(5).all(),
        'latest_posts': Post.query.order_by(Post.created_at.desc()).limit(5).all()
    }
    return render_template('admin/dashboard.html', stats=stats)

@main_bp.route('/admin/users')
@admin_required
@swag_from({
    'tags': ['Admin'],
    'description': 'Lista wszystkich użytkowników',
    'security': [{'session': []}],
    'responses': {
        200: {
            'description': 'Renderuje listę użytkowników',
            'examples': {
                'application/json': [
                    {'id': 1, 'username': 'admin', 'email': 'admin@example.com', 'is_admin': True},
                    {'id': 2, 'username': 'user1', 'email': 'user1@example.com', 'is_admin': False}
                ]
            }
        },
        403: {'description': 'Brak uprawnień'}
    }
})
def manage_users():
    """Wyświetla listę wszystkich użytkowników do zarządzania"""
    users = User.query.order_by(User.id).all()
    return render_template('admin/users.html', users=users)

@main_bp.route('/admin/users/<int:user_id>/toggle', methods=['POST'])
@admin_required
@swag_from({
    'tags': ['Admin'],
    'description': 'Zmienia status użytkownika (aktywny/admin)',
    'security': [{'session': []}],
    'parameters': [
        {
            'name': 'user_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID użytkownika'
        },
        {
            'name': 'toggle_admin',
            'in': 'formData',
            'type': 'string',
            'required': False,
            'description': 'Jeśli obecny - zmienia uprawnienia admina'
        }
    ],
    'responses': {
        302: {'description': 'Przekierowuje do listy użytkowników'},
        403: {'description': 'Brak uprawnień lub próba modyfikacji własnego konta'},
        404: {'description': 'Użytkownik nie istnieje'}
    }
})
def toggle_user_status(user_id):
    """Zmienia status użytkownika (aktywny/admin)"""
    if session['user_id'] == user_id:
        flash('Nie możesz modyfikować własnego konta', 'danger')
        return redirect(url_for('main.manage_users'))
    
    user = User.query.get_or_404(user_id)
    
    if 'toggle_admin' in request.form:
        user.is_admin = not user.is_admin
        action = "nadano" if user.is_admin else "cofnięto"
        msg = f"Uprawnienia administratora {action} dla {user.username}"
    else:
        user.is_active = not user.is_active
        action = "aktywowano" if user.is_active else "dezaktywowano"
        msg = f"Konto {user.username} {action}"
    
    db.session.commit()
    flash(msg, 'success')
    return redirect(url_for('main.manage_users'))

@main_bp.route('/admin/posts')
@admin_required
@swag_from({
    'tags': ['Admin'],
    'description': 'Lista wszystkich postów',
    'security': [{'session': []}],
    'responses': {
        200: {
            'description': 'Renderuje listę postów',
            'examples': {
                'application/json': [
                    {'id': 1, 'title': 'Tytuł posta', 'content': 'Treść...', 'author_id': 1}
                ]
            }
        },
        403: {'description': 'Brak uprawnień'}
    }
})
def manage_posts():
    """Wyświetla listę wszystkich postów do zarządzania"""
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template('admin/posts.html', posts=posts)

@main_bp.route('/admin/posts/<int:post_id>/delete', methods=['POST'])
@admin_required
@swag_from({
    'tags': ['Admin'],
    'description': 'Usuwa wybrany post',
    'security': [{'session': []}],
    'parameters': [
        {
            'name': 'post_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID posta do usunięcia'
        }
    ],
    'responses': {
        302: {'description': 'Przekierowuje do listy postów'},
        403: {'description': 'Brak uprawnień'},
        404: {'description': 'Post nie istnieje'}
    }
})
def delete_post(post_id):
    """Usuwa wybrany post"""
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash('Post został usunięty', 'success')
    return redirect(url_for('main.manage_posts'))

@main_bp.route('/admin/comments')
@admin_required
@swag_from({
    'tags': ['Admin'],
    'description': 'Lista wszystkich komentarzy',
    'security': [{'session': []}],
    'responses': {
        200: {
            'description': 'Renderuje listę komentarzy',
            'examples': {
                'application/json': [
                    {'id': 1, 'content': 'Treść komentarza', 'post_id': 1, 'author_id': 1}
                ]
            }
        },
        403: {'description': 'Brak uprawnień'}
    }
})
def manage_comments():
    """Wyświetla listę wszystkich komentarzy do zarządzania"""
    comments = Comment.query.order_by(Comment.created_at.desc()).all()
    return render_template('admin/comments.html', comments=comments)

@main_bp.route('/admin/comments/<int:comment_id>/delete', methods=['POST'])
@admin_required
@swag_from({
    'tags': ['Admin'],
    'description': 'Usuwa wybrany komentarz',
    'security': [{'session': []}],
    'parameters': [
        {
            'name': 'comment_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID komentarza do usunięcia'
        }
    ],
    'responses': {
        302: {'description': 'Przekierowuje do listy komentarzy'},
        403: {'description': 'Brak uprawnień'},
        404: {'description': 'Komentarz nie istnieje'}
    }
})
def delete_comment(comment_id):
    """Usuwa wybrany komentarz"""
    comment = Comment.query.get_or_404(comment_id)
    db.session.delete(comment)
    db.session.commit()
    flash('Komentarz został usunięty', 'success')
    return redirect(url_for('main.manage_comments'))

@main_bp.route('/')
@swag_from({
    'tags': ['Public'],
    'description': 'Strona główna z listą postów',
    'responses': {
        200: {
            'description': 'Renderuje stronę główną',
            'examples': {
                'application/json': [
                    {'id': 1, 'title': 'Tytuł posta', 'content': 'Treść...'}
                ]
            }
        }
    }
})
def home():
    """Wyświetla stronę główną z listą postów"""
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template('main.html', posts=posts)

@main_bp.route('/about')
@swag_from({
    'tags': ['Public'],
    'description': 'Strona "O mnie"',
    'responses': {
        200: {'description': 'Renderuje stronę "O mnie"'}
    }
})
def about():
    """Wyświetla stronę 'O mnie'"""
    return render_template('about.html')