from datetime import timedelta
from types import SimpleNamespace

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from apps.blog.models import Comment, Post, Tag


pytestmark = pytest.mark.django_db


@pytest.fixture
def blog_data(author, other_author, post_factory):
    python_tag = Tag.objects.create(name='python')
    django_tag = Tag.objects.create(name='django')
    old_post = post_factory(
        title='Old post',
        content='A Needle appears in this content.',
        status='published',
        likes=3,
        views=30,
    )
    middle_post = post_factory(
        post_author=other_author,
        title='Middle post',
        content='Middle content',
        status='pending',
        likes=20,
        views=10,
    )
    new_post = post_factory(
        title='Newest post',
        content='Newest content',
        status='draft',
        likes=10,
        views=20,
    )
    old_post.tags.add(python_tag)
    middle_post.tags.add(django_tag)
    new_post.tags.add(python_tag, django_tag)

    now = timezone.now()
    Post.objects.filter(pk=old_post.pk).update(
        created_at=now - timedelta(days=2)
    )
    Post.objects.filter(pk=middle_post.pk).update(
        created_at=now - timedelta(days=1)
    )
    Post.objects.filter(pk=new_post.pk).update(created_at=now)

    return SimpleNamespace(
        old_post=old_post,
        middle_post=middle_post,
        new_post=new_post,
        python_tag=python_tag,
        django_tag=django_tag,
    )


def test_post_list_is_paginated_and_newest_first(api_client, blog_data):
    response = api_client.get(reverse('post-list'), {'page_size': 2})

    assert response.status_code == status.HTTP_200_OK
    assert response.data['count'] == 3
    assert response.data['next'] is not None
    assert [post['title'] for post in response.data['results']] == [
        'Newest post',
        'Middle post',
    ]
    assert set(response.data['results'][0]) == {
        'id',
        'title',
        'author',
        'created_at',
    }


@pytest.mark.parametrize(
    ('filter_name', 'expected_titles'),
    [
        ('status', ['Old post']),
        ('author', ['Middle post']),
        ('tags', ['Newest post', 'Middle post']),
    ],
    ids=['status', 'author', 'tag'],
)
def test_post_list_model_filters(
    api_client,
    blog_data,
    other_author,
    filter_name,
    expected_titles,
):
    values = {
        'status': 'published',
        'author': other_author.pk,
        'tags': blog_data.django_tag.pk,
    }

    response = api_client.get(
        reverse('post-list'), {filter_name: values[filter_name]}
    )

    assert response.status_code == status.HTTP_200_OK
    assert [
        item['title'] for item in response.data['results']
    ] == expected_titles


@pytest.mark.parametrize(
    ('query', 'expected_titles'),
    [
        ({'search': 'Needle'}, ['Old post']),
        (
            {'ordering': '-likes'},
            ['Middle post', 'Newest post', 'Old post'],
        ),
    ],
    ids=['search-content', 'order-by-likes'],
)
def test_post_list_search_and_ordering(
    api_client, blog_data, query, expected_titles
):
    response = api_client.get(reverse('post-list'), query)

    assert response.status_code == status.HTTP_200_OK
    assert [
        item['title'] for item in response.data['results']
    ] == expected_titles


def test_anonymous_user_cannot_create_post(api_client):
    response = api_client.post(
        reverse('post-list'),
        {
            'title': 'A valid title',
            'content': 'Post content',
            'user_agreement': True,
        },
        format='json',
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert not Post.objects.filter(title='A valid title').exists()


def test_authenticated_user_can_create_post(
    api_client, other_author
):
    api_client.force_authenticate(other_author)

    response = api_client.post(
        reverse('post-list'),
        {
            'title': 'A valid title',
            'content': 'Post content',
            'user_agreement': True,
        },
        format='json',
    )

    assert response.status_code == status.HTTP_201_CREATED
    created_post = Post.objects.get(title='A valid title')
    assert created_post.author == other_author
    assert response.data['author']['username'] == 'other'
    assert 'user_agreement' not in response.data


@pytest.mark.parametrize(
    ('payload', 'error_field'),
    [
        (
            {
                'title': 'A valid title',
                'content': 'Content',
                'user_agreement': False,
            },
            'user_agreement',
        ),
        (
            {
                'title': 'A test title',
                'content': 'Content',
                'user_agreement': True,
            },
            'title',
        ),
    ],
    ids=['terms-not-accepted', 'forbidden-title'],
)
def test_create_post_validation(
    authenticated_api_client, payload, error_field
):
    response = authenticated_api_client.post(
        reverse('post-list'), payload, format='json'
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert error_field in response.data


@pytest.mark.parametrize(
    ('post_id', 'expected_status'),
    [(None, status.HTTP_200_OK), (999_999, status.HTTP_404_NOT_FOUND)],
    ids=['existing-post', 'missing-post'],
)
def test_retrieve_post(api_client, blog_data, post_id, expected_status):
    post_id = post_id or blog_data.old_post.pk

    response = api_client.get(
        reverse('post-detail', kwargs={'post_id': post_id})
    )

    assert response.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        assert response.data['id'] == blog_data.old_post.pk
        assert response.data['title'] == 'Old post'


def test_comments_action_returns_newest_comments(
    api_client, blog_data, author, other_author
):
    old_comment = Comment.objects.create(
        post=blog_data.old_post,
        author=author,
        content='First comment',
    )
    new_comment = Comment.objects.create(
        post=blog_data.old_post,
        author=other_author,
        content='Second comment',
    )

    response = api_client.get(
        reverse(
            'post-comments', kwargs={'post_id': blog_data.old_post.pk}
        )
    )

    assert response.status_code == status.HTTP_200_OK
    assert [comment['id'] for comment in response.data] == [
        new_comment.pk,
        old_comment.pk,
    ]
    assert response.data[0]['author'] == 'other'
    assert 'post' not in response.data[0]


def test_summary_reports_totals_and_grouped_statistics(
    api_client, blog_data, other_author
):
    Comment.objects.create(
        post=blog_data.old_post,
        author=other_author,
        content='A comment',
    )

    response = api_client.get(reverse('post-summary'))

    assert response.status_code == status.HTTP_200_OK
    assert response.data['posts'] == 3
    assert len(response.data['authors']) == 2
    assert response.data['comments']
    assert response.data['tags']


def test_authenticated_author_can_patch_and_delete_post(
    authenticated_api_client, blog_data
):
    detail_url = reverse(
        'post-detail', kwargs={'post_id': blog_data.old_post.pk}
    )

    patch_response = authenticated_api_client.patch(
        detail_url, {'title': 'Updated title'}, format='json'
    )
    delete_response = authenticated_api_client.delete(detail_url)

    assert patch_response.status_code == status.HTTP_200_OK
    assert patch_response.data['title'] == 'Updated title'
    assert delete_response.status_code == status.HTTP_204_NO_CONTENT
    assert not Post.objects.filter(pk=blog_data.old_post.pk).exists()


@pytest.mark.parametrize('method', ['patch', 'delete'])
def test_anonymous_user_cannot_modify_post(
    api_client, blog_data, method
):
    detail_url = reverse(
        'post-detail', kwargs={'post_id': blog_data.old_post.pk}
    )
    request = getattr(api_client, method)

    response = request(
        detail_url,
        {'title': 'Updated title'} if method == 'patch' else None,
        format='json',
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    blog_data.old_post.refresh_from_db()
    assert blog_data.old_post.title == 'Old post'


def test_obtain_auth_token_returns_persisted_token(api_client, user_factory):
    user = user_factory(username='api-user')

    response = api_client.post(
        reverse('api_auth_token'),
        {'username': 'api-user', 'password': 'strong-password'},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data['token'] == user.auth_token.key


def test_jwt_obtain_and_refresh_flow(api_client, user_factory):
    user_factory(username='api-user')

    obtain_response = api_client.post(
        reverse('token_obtain_pair'),
        {'username': 'api-user', 'password': 'strong-password'},
    )

    assert obtain_response.status_code == status.HTTP_200_OK
    assert {'access', 'refresh'} <= obtain_response.data.keys()

    refresh_response = api_client.post(
        reverse('token_refresh'),
        {'refresh': obtain_response.data['refresh']},
    )
    assert refresh_response.status_code == status.HTTP_200_OK
    assert 'access' in refresh_response.data


def test_post_detail_increments_view_count(client, post_factory):
    post = post_factory(title='Web post', views=0)

    response = client.get(
        reverse('blog:post_detail', kwargs={'post_id': post.pk})
    )

    assert response.status_code == 200
    post.refresh_from_db()
    assert post.views == 1


def test_post_create_requires_login(client):
    response = client.get(reverse('blog:post_create'))

    assert response.url == (
        f"{reverse('users:login')}?next={reverse('blog:post_create')}"
    )


def test_logged_in_user_can_create_post(client, author):
    client.force_login(author)

    response = client.post(
        reverse('blog:post_create'),
        {
            'title': 'Created through form',
            'content': 'Form content',
            'user_agreement': 'on',
        },
    )

    assert response.status_code == 302
    assert response.url == reverse('blog:post_list')
    created_post = Post.objects.get(title='Created through form')
    assert created_post.author == author


@pytest.mark.parametrize(
    ('authenticated', 'expected_comment_count'),
    [(False, 0), (True, 1)],
    ids=['anonymous', 'authenticated'],
)
def test_comment_creation_authentication(
    client,
    author,
    post_factory,
    authenticated,
    expected_comment_count,
):
    post = post_factory()
    url = reverse('blog:comments', kwargs={'post_id': post.pk})
    if authenticated:
        client.force_login(author)

    response = client.post(url, {'content': 'A web comment'})

    assert response.status_code == 302
    assert Comment.objects.filter(post=post).count() == expected_comment_count
    if authenticated:
        comment = Comment.objects.get(post=post)
        assert comment.author == author
        assert response.url == url
    else:
        assert response.url == reverse('users:login')
