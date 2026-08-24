import pytest

from _graphql.schema import schema
from apps.blog.models import Post, Tag


pytestmark = pytest.mark.django_db


def test_create_post_resolves_tag_names(author):
    result = schema.execute(
        '''
        mutation CreatePost($tags: [String!]) {
          createPost(title: "GraphQL post", content: "Content", tags: $tags) {
            post { id }
          }
        }
        ''',
        variable_values={'tags': ['python', 'django', 'python']},
    )

    assert result.errors is None
    post = Post.objects.get(title='GraphQL post')
    assert set(post.tags.values_list('name', flat=True)) == {
        'python',
        'django',
    }
    assert Tag.objects.count() == 2


def test_update_post_can_clear_tags(post_factory):
    post = post_factory()
    post.tags.add(Tag.objects.create(name='python'))

    result = schema.execute(
        '''
        mutation UpdatePost($id: Int!) {
          updatePost(id: $id, tags: []) { post { id } }
        }
        ''',
        variable_values={'id': post.pk},
    )

    assert result.errors is None
    assert not post.tags.exists()


@pytest.mark.parametrize(
    'operation',
    [
        '{ getPost(id: 999999) { id } }',
        'mutation { updatePost(id: 999999, title: "New") { post { id } } }',
        'mutation { deletePost(id: 999999) { result } }',
    ],
)
def test_missing_post_returns_domain_error(operation):
    result = schema.execute(operation)

    assert result.errors
    assert result.errors[0].message == 'Post not found'


def test_create_post_arguments_are_required():
    result = schema.execute('mutation { createPost { post { id } } }')

    assert result.errors
    assert all('is required' in error.message for error in result.errors)


def test_invalid_status_is_rejected(post_factory):
    post = post_factory(status='draft')

    result = schema.execute(
        '''
        mutation UpdatePost($id: Int!) {
          updatePost(id: $id, status: "invalid") { post { id } }
        }
        ''',
        variable_values={'id': post.pk},
    )

    assert result.errors
    assert 'status' in result.errors[0].message
    post.refresh_from_db()
    assert post.status == 'draft'
