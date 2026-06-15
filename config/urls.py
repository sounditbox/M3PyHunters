from debug_toolbar.toolbar import debug_toolbar_urls
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('blog/', include('apps.blog.urls', namespace='blog')),
    path('users/', include('apps.users.urls', namespace='users')),
              ] + debug_toolbar_urls()
