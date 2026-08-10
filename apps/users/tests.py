import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse


pytestmark = pytest.mark.django_db


def test_registration_creates_user_and_redirects_to_login(client):
    response = client.post(
        reverse('users:register'),
        {
            'username': 'new-user',
            'email': 'new@example.com',
            'password1': 'a-strong-new-password',
            'password2': 'a-strong-new-password',
        },
    )

    assert response.status_code == 302
    assert response.url == reverse('users:login')
    assert get_user_model().objects.filter(
        username='new-user', email='new@example.com'
    ).exists()


def test_profile_page_displays_requested_user(client, author):
    response = client.get(reverse('users:profile', kwargs={'pk': author.pk}))

    assert response.status_code == 200
    assert response.context['user'] == author


def test_user_can_edit_own_profile(client, author):
    client.force_login(author)

    response = client.post(
        reverse('users:edit', kwargs={'pk': author.pk}),
        {'first_name': 'After', 'last_name': 'Edit'},
    )

    assert response.status_code == 302
    assert response.url == reverse('users:profile', kwargs={'pk': author.pk})
    author.refresh_from_db()
    assert author.first_name == 'After'
    assert author.last_name == 'Edit'


@pytest.mark.parametrize('authenticated', [False, True])
def test_user_cannot_edit_another_profile(
    client, author, other_author, authenticated
):
    if authenticated:
        client.force_login(other_author)

    response = client.get(reverse('users:edit', kwargs={'pk': author.pk}))

    assert response.status_code == 403
