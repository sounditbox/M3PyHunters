from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from apps.blog.filters import PostFilter
from apps.blog.models import Post
from apps.blog.permissions import IsAuthorOrReadOnly
from apps.blog.serializers import FullPostSerializer, ShortPostSerializer, \
    CreatePostSerializer, PartialUpdatePostSerializer


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
