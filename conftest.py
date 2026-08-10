from itertools import count

import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.settings import api_settings as jwt_api_settings


@pytest.fixture(autouse=True)
def test_security_settings(settings, monkeypatch):
    settings.PASSWORD_HASHERS = [
        'django.contrib.auth.hashers.MD5PasswordHasher'
    ]
    settings.SECRET_KEY = 'test-secret-key-that-is-longer-than-32-bytes'
    monkeypatch.setattr(jwt_api_settings, 'SIGNING_KEY', settings.SECRET_KEY)


@pytest.fixture
def user_factory(db, django_user_model):
    sequence = count(1)

    def create_user(*, username=None, password='strong-password', **kwargs):
        username = username or f'user-{next(sequence)}'
        return django_user_model.objects.create_user(
            username=username,
            password=password,
            **kwargs,
        )

    return create_user


@pytest.fixture
def author(user_factory):
    return user_factory(username='author', email='author@example.com')


@pytest.fixture
def other_author(user_factory):
    return user_factory(username='other', email='other@example.com')


@pytest.fixture
def post_factory(db, author):
    from apps.blog.models import Post

    sequence = count(1)

    def create_post(*, post_author=None, **kwargs):
        number = next(sequence)
        defaults = {
            'title': f'Post {number}',
            'content': f'Content {number}',
            'author': post_author or author,
        }
        defaults.update(kwargs)
        return Post.objects.create(**defaults)

    return create_post


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def authenticated_api_client(api_client, author):
    api_client.force_authenticate(author)
    return api_client
