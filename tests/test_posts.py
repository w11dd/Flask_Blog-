import pytest
from flask import session, url_for, get_flashed_messages
from datetime import datetime
from models import Post, Comment
from extensions import db

def test_index_route(client):
    """Test the posts index route"""
    response = client.get(url_for('posts.index'))
    assert response.status_code == 200
    assert b'Posts' in response.data

def test_create_post_unauthorized(client):
    """Test create post route without authentication"""
    response = client.get(url_for('posts.create'))
    assert response.status_code == 302  # Should redirect to login
    assert url_for('auth.login') in response.location

def test_create_post_authorized(auth_client):
    """Test create post route with authentication"""
    response = auth_client.get(url_for('posts.create'))
    assert response.status_code == 200
    assert b'Create Post' in response.data

    # Test form submission
    response = auth_client.post(url_for('posts.create'),
        data={'title': 'Test Post', 'content': 'Test content'},
        follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Test Post' in response.data
    assert b'Post utworzony!' in response.data

def test_view_post(client, test_user):
    """Test viewing a single post"""
    # Create a test post
    post = Post(
        title='Test Post',
        content='Test content',
        user_id=test_user.id,
        created_at=datetime.utcnow()
    )
    db.session.add(post)
    db.session.commit()

    response = client.get(url_for('posts.view', post_id=post.id))
    assert response.status_code == 200
    assert b'Test Post' in response.data
    assert b'Test content' in response.data

def test_edit_post_unauthorized(client, test_user):
    """Test editing a post without proper authorization"""
    # Create a test post
    post = Post(
        title='Test Post',
        content='Test content',
        user_id=test_user.id,
        created_at=datetime.utcnow()
    )
    db.session.add(post)
    db.session.commit()

    # Unauthenticated user
    response = client.get(url_for('posts.edit', post_id=post.id))
    assert response.status_code == 302  # Should redirect to login

def test_edit_post_author(auth_client, test_user):
    """Test editing a post as the author"""
    # Create a test post
    post = Post(
        title='Test Post',
        content='Test content',
        user_id=test_user.id,
        created_at=datetime.utcnow()
    )
    db.session.add(post)
    db.session.commit()

    # Authorized user (author)
    response = auth_client.get(url_for('posts.edit', post_id=post.id))
    assert response.status_code == 200
    assert b'Edit Post' in response.data

    # Test form submission
    response = auth_client.post(url_for('posts.edit', post_id=post.id),
        data={'title': 'Updated Post', 'content': 'Updated content'},
        follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Updated Post' in response.data
    assert b'Post zaktualizowany!' in response.data

def test_edit_post_admin(admin_auth_client, test_user):
    """Test editing a post as admin (not the author)"""
    # Create a test post
    post = Post(
        title='Test Post',
        content='Test content',
        user_id=test_user.id,
        created_at=datetime.utcnow()
    )
    db.session.add(post)
    db.session.commit()

    # Admin user (not author)
    response = admin_auth_client.get(url_for('posts.edit', post_id=post.id))
    assert response.status_code == 200
    assert b'Edit Post' in response.data

def test_delete_post_unauthorized(client, test_user):
    """Test deleting a post without proper authorization"""
    # Create a test post
    post = Post(
        title='Test Post',
        content='Test content',
        user_id=test_user.id,
        created_at=datetime.utcnow()
    )
    db.session.add(post)
    db.session.commit()

    # Unauthenticated user
    response = client.post(url_for('posts.delete', post_id=post.id))
    assert response.status_code == 302  # Should redirect to login

def test_delete_post_author(auth_client, test_user):
    """Test deleting a post as the author"""
    # Create a test post
    post = Post(
        title='Test Post',
        content='Test content',
        user_id=test_user.id,
        created_at=datetime.utcnow()
    )
    db.session.add(post)
    db.session.commit()

    # Authorized user (author)
    response = auth_client.post(url_for('posts.delete', post_id=post.id),
        follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Post usuni' in response.data
    assert Post.query.get(post.id) is None

def test_delete_post_admin(admin_auth_client, test_user):
    """Test deleting a post as admin (not the author)"""
    # Create a test post
    post = Post(
        title='Test Post',
        content='Test content',
        user_id=test_user.id,
        created_at=datetime.utcnow()
    )
    db.session.add(post)
    db.session.commit()

    # Admin user (not author)
    response = admin_auth_client.post(url_for('posts.delete', post_id=post.id),
        follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Post usuni' in response.data
    assert Post.query.get(post.id) is None

def test_add_comment_unauthorized(client, test_user):
    """Test adding a comment without authentication"""
    # Create a test post
    post = Post(
        title='Test Post',
        content='Test content',
        user_id=test_user.id,
        created_at=datetime.utcnow()
    )
    db.session.add(post)
    db.session.commit()

    response = client.post(url_for('posts.add_comment', post_id=post.id),
        data={'content': 'Test comment'},
        follow_redirects=True)
    
    assert response.status_code == 200
    assert url_for('auth.login') in response.request.url  # Should redirect to login

def test_add_comment_authorized(auth_client, test_user):
    """Test adding a comment with authentication"""
    # Create a test post
    post = Post(
        title='Test Post',
        content='Test content',
        user_id=test_user.id,
        created_at=datetime.utcnow()
    )
    db.session.add(post)
    db.session.commit()

    response = auth_client.post(url_for('posts.add_comment', post_id=post.id),
        data={'content': 'Test comment'},
        follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Test comment' in response.data
    assert b'Komentarz zosta' in response.data  # Flash message

def test_edit_comment_unauthorized(client, test_user):
    """Test editing a comment without proper authorization"""
    # Create a test post and comment
    post = Post(
        title='Test Post',
        content='Test content',
        user_id=test_user.id,
        created_at=datetime.utcnow()
    )
    db.session.add(post)
    db.session.commit()
    
    comment = Comment(
        content='Test comment',
        user_id=test_user.id,
        post_id=post.id
    )
    db.session.add(comment)
    db.session.commit()

    # Unauthenticated user
    response = client.get(url_for('posts.edit_comment', comment_id=comment.id))
    assert response.status_code == 302  # Should redirect to login

def test_edit_comment_author(auth_client, test_user):
    """Test editing a comment as the author"""
    # Create a test post and comment
    post = Post(
        title='Test Post',
        content='Test content',
        user_id=test_user.id,
        created_at=datetime.utcnow()
    )
    db.session.add(post)
    db.session.commit()
    
    comment = Comment(
        content='Test comment',
        user_id=test_user.id,
        post_id=post.id
    )
    db.session.add(comment)
    db.session.commit()

    # Authorized user (author)
    response = auth_client.get(url_for('posts.edit_comment', comment_id=comment.id))
    assert response.status_code == 200
    assert b'Edit Comment' in response.data

    # Test form submission
    response = auth_client.post(url_for('posts.edit_comment', comment_id=comment.id),
        data={'content': 'Updated comment'},
        follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Updated comment' in response.data
    assert b'Komentarz zosta' in response.data  # Flash message

def test_delete_comment_unauthorized(client, test_user):
    """Test deleting a comment without proper authorization"""
    # Create a test post and comment
    post = Post(
        title='Test Post',
        content='Test content',
        user_id=test_user.id,
        created_at=datetime.utcnow()
    )
    db.session.add(post)
    db.session.commit()
    
    comment = Comment(
        content='Test comment',
        user_id=test_user.id,
        post_id=post.id
    )
    db.session.add(comment)
    db.session.commit()

    # Unauthenticated user
    response = client.post(url_for('posts.delete_comment', comment_id=comment.id))
    assert response.status_code == 302  # Should redirect to login

def test_delete_comment_author(auth_client, test_user):
    """Test deleting a comment as the author"""
    # Create a test post and comment
    post = Post(
        title='Test Post',
        content='Test content',
        user_id=test_user.id,
        created_at=datetime.utcnow()
    )
    db.session.add(post)
    db.session.commit()
    
    comment = Comment(
        content='Test comment',
        user_id=test_user.id,
        post_id=post.id
    )
    db.session.add(comment)
    db.session.commit()

    # Authorized user (author)
    response = auth_client.post(url_for('posts.delete_comment', comment_id=comment.id),
        follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Komentarz zosta' in response.data  # Flash message
    assert Comment.query.get(comment.id) is None

def test_delete_comment_admin(admin_auth_client, test_user):
    """Test deleting a comment as admin (not the author)"""
    # Create a test post and comment
    post = Post(
        title='Test Post',
        content='Test content',
        user_id=test_user.id,
        created_at=datetime.utcnow()
    )
    db.session.add(post)
    db.session.commit()
    
    comment = Comment(
        content='Test comment',
        user_id=test_user.id,
        post_id=post.id
    )
    db.session.add(comment)
    db.session.commit()

    # Admin user (not author)
    response = admin_auth_client.post(url_for('posts.delete_comment', comment_id=comment.id),
        follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Komentarz zosta' in response.data  # Flash message
    assert Comment.query.get(comment.id) is None