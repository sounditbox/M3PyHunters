import graphene
from graphql import GraphQLError

from apps.blog.models import Post
from .gql_types import PostType, UserType


class BlogQuery(graphene.ObjectType):

    @staticmethod
    def resolve_all_posts(root, info, limit, status=None):
        qs = Post.objects.all()
        if status:
            qs = qs.filter(status=status)
        return qs[:limit]
    all_posts = graphene.List(PostType,
                              limit=graphene.Int(default_value=10),
                              status=graphene.String()
                              )

    @staticmethod
    def resolve_get_post(root, info, id):
        try:
            return Post.objects.get(id=id)
        except Post.DoesNotExist:
            raise GraphQLError('Post not found') from None
    get_post = graphene.Field(PostType, id=graphene.Int(required=True))


class UserQuery(graphene.ObjectType):
    @staticmethod
    def resolve_me(root, info):
        return info.context.user
    me = graphene.Field(UserType)
