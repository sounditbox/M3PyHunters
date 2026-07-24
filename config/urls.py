from debug_toolbar.toolbar import debug_toolbar_urls
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

import apps
from apps.blog.api import PostListApiView, PostDetailApiView
from config import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('blog/', include('apps.blog.urls', namespace='blog')),
    path('users/', include('apps.users.urls', namespace='users')),
    path('', apps.blog.views.PostListView.as_view()),

    # API
    path('api/posts/', PostListApiView.as_view(), name='post_list_api'),
    path('api/posts/<int:post_id>', PostDetailApiView.as_view(), name='post_detail_api'),
              ] + debug_toolbar_urls()

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
