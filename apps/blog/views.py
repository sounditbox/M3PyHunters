from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView, CreateView, UpdateView, \
    DeleteView

from apps.blog.forms import PostCreateForm
from apps.blog.models import Post, Comment


class PostDetailView(DetailView):
    model = Post
    context_object_name = 'post'
    pk_url_kwarg = 'post_id'


class PostListView(ListView):
    model = Post
    context_object_name = 'posts'
    extra_context = {'title': 'All Posts'}
    ordering = ['created_at']


class PostCreateView(CreateView):
    model = Post
    form_class = PostCreateForm
    success_url = reverse_lazy('blog:post_list')
    template_name = 'create_post.html'


class PostDeleteView(DeleteView):
    model = Post
    success_url = reverse_lazy('blog:post_list')
    template_name = 'delete_post.html'
    pk_url_kwarg = 'post_id'


class PostUpdateView(UpdateView):
    model = Post
    form_class = PostCreateForm
    success_url = reverse_lazy('blog:post_list')
    template_name = 'create_post.html'
    pk_url_kwarg = 'post_id'


class CommentListView(ListView):
    model = Comment
    context_object_name = 'comments'

    def get_queryset(self):
        return Comment.objects.filter(post_id=self.kwargs['post_id'])

    def get_context_data(self, **context):
        context['post_id'] = self.kwargs['post_id']
        return super().get_context_data(**context)

    def post(self, request, post_id):
        content = request.POST.get('content')
        post = Post.objects.get(id=post_id)
        Comment.objects.create(content=content, post=post)
        return redirect('blog:comments', post_id=post_id)