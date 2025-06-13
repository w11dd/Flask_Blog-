from flask import Blueprint, render_template, redirect, url_for, flash, session, abort, request
from models import Post, User, Comment
from forms import PostForm, CommentForm
from extensions import db
from datetime import datetime
from functools import wraps
from flasgger import swag_from

posts_bp = Blueprint('posts', __name__)

def login_required(f):
    """Dekorator wymagający zalogowania użytkownika"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Proszę się zalogować.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def author_or_admin_required(f):
    """Dekorator wymagający bycia autorem lub administratorem"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Proszę się zalogować.', 'warning')
            return redirect(url_for('auth.login'))
            
        post = Post.query.get_or_404(kwargs.get('post_id'))
        user = User.query.get(session['user_id'])
        
        if not user or (post.user_id != user.id and not user.is_admin):
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

@posts_bp.route('/')
@swag_from({
    'tags': ['Posts'],
    'description': 'Wyświetla listę wszystkich postów',
    'responses': {
        200: {
            'description': 'Renderuje listę postów',
            'examples': {
                'application/json': [
                    {
                        'id': 1,
                        'title': 'Przykładowy post',
                        'content': 'Treść posta...',
                        'created_at': '2023-01-01T00:00:00Z'
                    }
                ]
            }
        }
    }
})
def index():
    """Wyświetla listę wszystkich postów"""
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template('posts/list_posts.html', posts=posts)

@posts_bp.route('/create', methods=['GET', 'POST'])
@login_required
@swag_from({
    'tags': ['Posts'],
    'description': 'Tworzenie nowego posta',
    'security': [{'session': []}],
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'title': {'type': 'string', 'example': 'Tytuł posta'},
                    'content': {'type': 'string', 'example': 'Treść posta...'}
                },
                'required': ['title', 'content']
            }
        }
    ],
    'responses': {
        200: {'description': 'Renderuje formularz tworzenia posta'},
        302: {'description': 'Przekierowanie po sukcesie'},
        401: {'description': 'Wymagane logowanie'}
    }
})
def create():
    """Tworzenie nowego posta"""
    form = PostForm()
    if form.validate_on_submit():
        user = User.query.get(session.get('user_id'))
        if not user:
            flash('Musisz być zalogowany', 'danger')
            return redirect(url_for('auth.login'))
            
        new_post = Post(
            title=form.title.data,
            content=form.content.data,
            user_id=user.id,
            created_at=datetime.utcnow()
        )
        
        db.session.add(new_post)
        db.session.commit()
        flash('Post utworzony!', 'success')
        return redirect(url_for('posts.index'))
    
    return render_template('posts/create_post.html', form=form)

@posts_bp.route('/<int:post_id>')
@swag_from({
    'tags': ['Posts'],
    'description': 'Wyświetla szczegóły posta z komentarzami',
    'parameters': [
        {
            'name': 'post_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID posta'
        }
    ],
    'responses': {
        200: {
            'description': 'Renderuje szczegóły posta',
            'examples': {
                'application/json': {
                    'id': 1,
                    'title': 'Tytuł posta',
                    'content': 'Treść posta...',
                    'comments': [
                        {
                            'id': 1,
                            'content': 'Przykładowy komentarz',
                            'author': 'Jan Kowalski'
                        }
                    ]
                }
            }
        },
        404: {'description': 'Post nie istnieje'}
    }
})
def view(post_id):
    """Wyświetla szczegóły posta z komentarzami"""
    post = Post.query.get_or_404(post_id)
    form = CommentForm()
    current_user = User.query.get(session['user_id']) if 'user_id' in session else None
    return render_template('posts/view_post.html', 
                         post=post, 
                         form=form,
                         current_user=current_user)

@posts_bp.route('/edit/<int:post_id>', methods=['GET', 'POST'])
@author_or_admin_required
@swag_from({
    'tags': ['Posts'],
    'description': 'Edycja istniejącego posta',
    'security': [{'session': []}],
    'parameters': [
        {
            'name': 'post_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID posta do edycji'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'title': {'type': 'string', 'example': 'Nowy tytuł'},
                    'content': {'type': 'string', 'example': 'Nowa treść...'}
                },
                'required': ['title', 'content']
            }
        }
    ],
    'responses': {
        200: {'description': 'Renderuje formularz edycji'},
        302: {'description': 'Przekierowanie po sukcesie'},
        403: {'description': 'Brak uprawnień'},
        404: {'description': 'Post nie istnieje'}
    }
})
def edit(post_id):
    """Edycja istniejącego posta"""
    post = Post.query.get_or_404(post_id)
    form = PostForm(obj=post)
    
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Post zaktualizowany!', 'success')
        return redirect(url_for('posts.view', post_id=post.id))
    
    return render_template('posts/edit_post.html', form=form, post=post)

@posts_bp.route('/delete/<int:post_id>', methods=['POST'])
@author_or_admin_required
@swag_from({
    'tags': ['Posts'],
    'description': 'Usuwanie posta',
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
        302: {'description': 'Przekierowanie po sukcesie'},
        403: {'description': 'Brak uprawnień'},
        404: {'description': 'Post nie istnieje'}
    }
})
def delete(post_id):
    """Usuwanie posta"""
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash('Post usunięty!', 'success')
    return redirect(url_for('posts.index'))

@posts_bp.route('/post/<int:post_id>/comment', methods=['POST'])
@login_required
@swag_from({
    'tags': ['Comments'],
    'description': 'Dodawanie komentarza do posta',
    'security': [{'session': []}],
    'parameters': [
        {
            'name': 'post_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID posta'
        },
        {
            'name': 'content',
            'in': 'formData',
            'type': 'string',
            'required': True,
            'description': 'Treść komentarza'
        }
    ],
    'responses': {
        302: {'description': 'Przekierowanie z powrotem do posta'},
        400: {'description': 'Nieprawidłowe dane formularza'},
        401: {'description': 'Wymagane logowanie'}
    }
})
def add_comment(post_id):
    """Dodawanie komentarza do posta"""
    form = CommentForm()
    if form.validate_on_submit():
        user = User.query.get(session['user_id'])
        comment = Comment(
            content=form.content.data,
            user_id=user.id,
            post_id=post_id
        )
        db.session.add(comment)
        db.session.commit()
        flash('Komentarz został dodany!', 'success')
    else:
        for error in form.content.errors:
            flash(error, 'danger')
    return redirect(url_for('posts.view', post_id=post_id))

@posts_bp.route('/comment/<int:comment_id>/edit', methods=['GET', 'POST'])
@login_required
@swag_from({
    'tags': ['Comments'],
    'description': 'Edycja istniejącego komentarza',
    'security': [{'session': []}],
    'parameters': [
        {
            'name': 'comment_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID komentarza do edycji'
        },
        {
            'name': 'content',
            'in': 'formData',
            'type': 'string',
            'required': True,
            'description': 'Nowa treść komentarza'
        }
    ],
    'responses': {
        200: {'description': 'Renderuje formularz edycji'},
        302: {'description': 'Przekierowanie po sukcesie'},
        403: {'description': 'Brak uprawnień'},
        404: {'description': 'Komentarz nie istnieje'}
    }
})
def edit_comment(comment_id):
    """Edycja istniejącego komentarza"""
    comment = Comment.query.get_or_404(comment_id)
    user = User.query.get(session['user_id'])
    
    if comment.user_id != user.id and not user.is_admin:
        abort(403)
    
    form = CommentForm(obj=comment)
    
    if form.validate_on_submit():
        comment.content = form.content.data
        comment.updated_at = datetime.utcnow()
        db.session.commit()
        flash('Komentarz został zaktualizowany.', 'success')
        return redirect(url_for('posts.view', post_id=comment.post_id))
    
    return render_template('posts/edit_comment.html', form=form, comment=comment)

@posts_bp.route('/comment/<int:comment_id>/delete', methods=['POST'])
@login_required
@swag_from({
    'tags': ['Comments'],
    'description': 'Usuwanie komentarza',
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
        302: {'description': 'Przekierowanie po sukcesie'},
        403: {'description': 'Brak uprawnień'},
        404: {'description': 'Komentarz nie istnieje'}
    }
})
def delete_comment(comment_id):
    """Usuwanie komentarza"""
    comment = Comment.query.get_or_404(comment_id)
    user = User.query.get(session['user_id'])
    
    if comment.user_id != user.id and not user.is_admin:
        abort(403)
    
    post_id = comment.post_id
    db.session.delete(comment)
    db.session.commit()
    flash('Komentarz został usunięty.', 'success')
    return redirect(url_for('posts.view', post_id=post_id))