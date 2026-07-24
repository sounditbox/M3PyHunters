from django.urls import path

from .views import *

app_name = 'apps.blog'
urlpatterns = [
    path('feedback', FeedbackView.as_view(), name='feedback'),
    # path('posts/create/', post_create, name='post_create'),
    path('posts/create/', PostCreateView.as_view(), name='post_create'), # CBV аналог
    path('posts/', PostListView.as_view(), name='post_list'),
    path('posts/<int:post_id>/', PostDetailView.as_view(), name='post_detail'),
    path('posts/<int:post_id>/update', PostUpdateView.as_view(), name='post_update'),
    path('posts/<int:post_id>/delete/', PostDeleteView.as_view(), name='post_delete'),
    path('posts/<int:post_id>/comments/', CommentListView.as_view(),
         name='comments'),


]

