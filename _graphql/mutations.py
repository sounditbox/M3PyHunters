import graphene
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction
from graphql import GraphQLError

from _graphql.gql_types import PostType
from apps.blog.models import Post, Tag


def _validate(instance):
    try:
        instance.full_clean()
    except ValidationError as exc:
        if hasattr(exc, 'message_dict'):
            details = '; '.join(
                f'{field}: {", ".join(messages)}'
                for field, messages in exc.message_dict.items()
            )
        else:
            details = '; '.join(exc.messages)
        raise GraphQLError(details) from None


def _resolve_tags(tag_names):
    names = list(dict.fromkeys(name.strip() for name in tag_names))
    if any(not name for name in names):
        raise GraphQLError('Tag names must not be empty')

    tags = []
    for name in names:
        tag = Tag.objects.filter(name=name).first()
        if tag is None:
            tag = Tag(name=name)
            _validate(tag)
            tag.save()
        tags.append(tag)
    return tags


class CreatePost(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        content = graphene.String(required=True)
        tags = graphene.List(graphene.NonNull(graphene.String))

    @classmethod
    @transaction.atomic
    def mutate(cls, root, info, title, content, tags=None):
        user = get_user_model().objects.first()
        if not user.is_authenticated:
            raise GraphQLError("Unauthorized")
        post = Post(title=title, content=content, author=user)
        _validate(post)
        post.save()
        if tags is not None:
            post.tags.set(_resolve_tags(tags))
        return cls(post=post)

    post = graphene.Field(PostType)


class UpdatePost(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        title = graphene.String()
        content = graphene.String()
        tags = graphene.List(graphene.NonNull(graphene.String))
        status = graphene.String()

    @classmethod
    @transaction.atomic
    def mutate(cls, root, info, id, title=None, content=None, tags=None,
               status=None):
        try:
            post = Post.objects.get(id=id)
        except Post.DoesNotExist:
            raise GraphQLError('Post not found') from None
        if title is not None:
            post.title = title
        if content is not None:
            post.content = content
        if status is not None:
            post.status = status
        resolved_tags = _resolve_tags(tags) if tags is not None else None
        _validate(post)
        post.save()
        if resolved_tags is not None:
            post.tags.set(resolved_tags)
        return cls(post=post)

    post = graphene.Field(PostType)


class DeletePost(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    @classmethod
    @transaction.atomic
    def mutate(cls, root, info, id):
        try:
            post = Post.objects.get(id=id)
        except Post.DoesNotExist:
            raise GraphQLError('Post not found') from None
        post.delete()
        return cls(result="Post deleted successfully")

    result = graphene.String()


class BlogMutation:
    create_post = CreatePost.Field()
    update_post = UpdatePost.Field()
    delete_post = DeletePost.Field()
