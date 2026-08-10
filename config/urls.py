from debug_toolbar.toolbar import debug_toolbar_urls
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

import apps
from apps.blog.api import PostListApiView, PostDetailApiView, post_router
from config import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('blog/', include('apps.blog.urls', namespace='blog')),
    path('users/', include('apps.users.urls', namespace='users')),
    path('', apps.blog.views.PostListView.as_view()),

    # API
    path('api/auth-token/', obtain_auth_token, name='api_auth_token'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # path('api/posts/', PostListApiView.as_view(), name='post_list_api'),
    # path('api/posts/<int:post_id>', PostDetailApiView.as_view(), name='post_detail_api'),
    #
    path('api/', include(post_router.urls))
] + debug_toolbar_urls()

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
