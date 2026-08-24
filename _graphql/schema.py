import graphene
from graphene import ObjectType

from .mutations import BlogMutation
from .queries import BlogQuery, UserQuery


class Query(BlogQuery, UserQuery):
    pass


class Mutation(BlogMutation, ObjectType):  # , UserMutation):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
