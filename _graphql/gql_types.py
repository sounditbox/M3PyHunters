from django.contrib.auth import get_user_model
from graphene_django import DjangoObjectType

from apps.blog.models import Comment, Tag, Post


class UserType(DjangoObjectType):
    class Meta:
        model = get_user_model()
        fields = ('id', 'username', 'email', 'first_name', 'last_name')


class CommentType(DjangoObjectType):
    class Meta:
        model = Comment
        fields = ('id', 'post', 'author', 'content', 'created_at')


class TagType(DjangoObjectType):
    class Meta:
        model = Tag
        fields = ('id', 'name')


class PostType(DjangoObjectType):
    class Meta:
        model = Post
        fields = ('id', 'title', 'content', 'author', 'created_at', 'tags',
                  'comments')
