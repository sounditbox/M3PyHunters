from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
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


class PostViewSet(ModelViewSet):
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

    @action(detail=True, methods=['get'])
    def comments(self, *args, **kwargs):
        return Response(
            CommentSerializer(self.get_object().comments.all(), many=True).data)

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
