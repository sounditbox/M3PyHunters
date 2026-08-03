from django_filters import rest_framework as filters

from apps.blog.models import Post


class PostFilter(filters.FilterSet):
    created_after = filters.IsoDateTimeFilter(
        field_name='created_at', lookup_expr='gte'
    )
    created_before = filters.IsoDateTimeFilter(
        field_name='created_at', lookup_expr='lte'
    )

    class Meta:
        model = Post
        fields = ['status', 'author', 'tags']
