from django.contrib import admin
from unfold.admin import TabularInline, StackedInline, ModelAdmin

from apps.blog.models import Post, Comment, Tag


class CommentInline(TabularInline):
    model = Comment
    extra = 0
    readonly_fields = ('created_at', 'updated_at')
    classes = ('collapse',)


class TagInline(StackedInline):
    model = Post.tags.through
    extra = 0
    classes = ('collapse',)


@admin.register(Post)
class PostAdmin(ModelAdmin):
    list_display = ('id', 'title', 'status', 'created_at', 'updated_at',
                    'popularity', 'comments_count')
    list_display_links = ('id',)
    list_filter = ('status', 'created_at', 'updated_at')
    list_per_page = 10
    list_max_show_all = 1000
    list_editable = ('status',)
    search_fields = ('title', 'content')
    actions = ['publish', 'make_draft', 'make_pending']
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'popularity')
    inlines = (CommentInline, TagInline)

    fieldsets = (
        ('Main Information', {'fields': ('title', 'status')}),
        ('Content', {'fields': ('content',), 'classes': ('collapse',)}),
        ('Statistics', {'fields': ('likes', 'views', 'popularity')}),
        ('Important Dates', {'fields': ('created_at', 'updated_at')})
    )

    @admin.display(
        description='Popularity',
        empty_value=0,
        ordering='likes'
    )
    def popularity(self, obj):
        if obj.views == 0:
            return 0
        return round(obj.likes / obj.views, 2)

    @admin.display(description='Comments count')
    def comments_count(self, obj):
        return obj.comments.count()

    @admin.action
    def publish(self, request, queryset):
        queryset.update(status='published')

    @admin.action
    def make_draft(self, request, queryset):
        queryset.update(status='draft')

    @admin.action
    def make_pending(self, request, queryset):
        queryset.update(status='pending')


@admin.register(Comment)
class CommentAdmin(ModelAdmin):
    list_display = ('id', 'content', 'created_at', 'updated_at', 'post')
    list_display_links = ('id',)
    list_filter = ('created_at', 'updated_at')
    list_per_page = 10
    list_editable = ('post',)
    search_fields = ('content',)
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)


admin.site.register(Tag)
