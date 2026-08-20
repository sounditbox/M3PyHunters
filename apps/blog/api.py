from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view, \
    inline_serializer, OpenApiResponse
from rest_framework import filters
from rest_framework import serializers as drf_serializers
from rest_framework.decorators import action
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly, \
    IsAuthenticated
from rest_framework.response import Response
from rest_framework.routers import DefaultRouter
from rest_framework.viewsets import ModelViewSet

from apps.blog.filters import PostFilter
from apps.blog.models import Post
from apps.blog.permissions import IsAuthorOrReadOnly
from apps.blog.serializers import FullPostSerializer, ShortPostSerializer, \
    CreatePostSerializer, PartialUpdatePostSerializer, CommentSerializer


post_summary_serializer = inline_serializer(
    name='PostSummary',
    fields={
        'authors': inline_serializer(
            name='PostAuthorStatistics',
            fields={
                'author': drf_serializers.IntegerField(allow_null=True),
                'author__count': drf_serializers.IntegerField(),
            },
            many=True,
        ),
        'posts': drf_serializers.IntegerField(),
        'comments': inline_serializer(
            name='PostCommentStatistics',
            fields={
                'comments__author': drf_serializers.IntegerField(
                    allow_null=True
                ),
                'comments__author__count': drf_serializers.IntegerField(),
            },
            many=True,
        ),
        'tags': inline_serializer(
            name='PostTagStatistics',
            fields={
                'tags': drf_serializers.IntegerField(allow_null=True),
                'tags__count': drf_serializers.IntegerField(),
            },
            many=True,
        ),
    },
)


class PostListApiView(ListCreateAPIView):
    queryset = Post.objects.select_related('author').prefetch_related('tags')
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter,
                       filters.OrderingFilter]
    filterset_class = PostFilter
    search_fields = ['title', 'content', '=author__username',
                     '^author__email']
    ordering_fields = ['title', 'created_at', 'updated_at', 'likes', 'views']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreatePostSerializer
        return ShortPostSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class PostDetailApiView(RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.select_related('author').prefetch_related(
        'comments__author', 'tags'
    )
    serializer_class = FullPostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    lookup_url_kwarg = 'post_id'

    def get_serializer_class(self):
        if self.request.method == 'PATCH':
            return PartialUpdatePostSerializer
        return FullPostSerializer


@extend_schema_view(
    list=extend_schema(
        summary='List posts',
        description=(
            'Return a paginated list of posts. Results can be filtered by '
            'status, author, and tags; searched by title, content, author '
            'username, or author email; and ordered by title, timestamps, '
            'likes, or views.'
        ),
        responses={200: ShortPostSerializer(many=True)},
        tags=['Posts'],
    ),
    create=extend_schema(
        summary='Create a post',
        description=(
            'Create a post owned by the authenticated user. The '
            '`user_agreement` field must be true.'
        ),
        request=CreatePostSerializer,
        responses={
            201: CreatePostSerializer,
            400: OpenApiResponse(description='Invalid post data.'),
            401: OpenApiResponse(description='Authentication required.'),
        },
        tags=['Posts'],
    ),
    retrieve=extend_schema(
        summary='Retrieve a post',
        description='Return a single post by its ID.',
        responses={
            200: ShortPostSerializer,
            404: OpenApiResponse(description='Post not found.'),
        },
        tags=['Posts'],
    ),
    update=extend_schema(
        summary='Replace a post',
        description='Replace a post. Authentication is required.',
        request=ShortPostSerializer,
        responses={
            200: ShortPostSerializer,
            400: OpenApiResponse(description='Invalid post data.'),
            401: OpenApiResponse(description='Authentication required.'),
            404: OpenApiResponse(description='Post not found.'),
        },
        tags=['Posts'],
    ),
    partial_update=extend_schema(
        summary='Update a post',
        description=(
            'Update one or more editable fields of a post. Authentication '
            'is required.'
        ),
        request=ShortPostSerializer,
        responses={
            200: ShortPostSerializer,
            400: OpenApiResponse(description='Invalid post data.'),
            401: OpenApiResponse(description='Authentication required.'),
            404: OpenApiResponse(description='Post not found.'),
        },
        tags=['Posts'],
    ),
    destroy=extend_schema(
        summary='Delete a post',
        description='Delete a post. Authentication is required.',
        responses={
            204: OpenApiResponse(description='Post deleted.'),
            401: OpenApiResponse(description='Authentication required.'),
            404: OpenApiResponse(description='Post not found.'),
        },
        tags=['Posts'],
    ),
)
class PostViewSet(ModelViewSet):
    '''
    API endpoint for Post objects

    Basic CRUD operations are available
    Get summary of posts
    Get comments of post
    '''
    queryset = Post.objects.select_related('author').prefetch_related(
        'tags')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter,
                       filters.OrderingFilter]

    filterset_class = PostFilter
    search_fields = ['title', 'content', '=author__username',
                     '^author__email']
    ordering_fields = ['title', 'created_at', 'updated_at', 'likes', 'views']
    ordering = ['-created_at']
    lookup_url_kwarg = 'post_id'

    def get_queryset(self):
        q = self.queryset
        if self.action not in ['list', 'create']:
            q = self.queryset.prefetch_related('comments__author')
        return q

    def get_serializer_class(self):
        if self.action == 'create':
            return CreatePostSerializer
        return ShortPostSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @extend_schema(
        summary='List post comments',
        description='Return all comments for a post, newest first.',
        responses={
            200: CommentSerializer(many=True),
            404: OpenApiResponse(description='Post not found.'),
        },
        tags=['Posts'],
    )
    @action(detail=True, methods=['get'])
    def comments(self, *args, **kwargs):
        return Response(
            CommentSerializer(self.get_object().comments.all(), many=True).data)

    @extend_schema(
        summary='Get post statistics',
        description=(
            'Return the total number of posts and grouped post counts by '
            'author, comment author, and tag.'
        ),
        responses={200: post_summary_serializer},
        tags=['Posts'],
    )
    @action(methods=['get'], detail=False)
    def summary(self, *args, **kwargs):
        return Response(
            {
                'authors': self.get_queryset().values('author').annotate(
                    Count('author')),
                'posts': self.get_queryset().count(),
                'comments': self.get_queryset().values(
                    'comments__author').annotate(Count('comments__author')),
                'tags': self.get_queryset().values('tags').annotate(
                    Count('tags')),
            })


post_router = DefaultRouter()
post_router.register('posts', PostViewSet)
