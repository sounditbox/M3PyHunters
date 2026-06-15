from typing import Any

from django.http import HttpRequest
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View

from apps.blog.models import Post, Comment, Tag


# def get_post(request: HttpRequest, post_id: int) -> HttpResponse:
#     if post_id not in pseudo_db['posts']:
#         return render(request, '404.html', {'instance': f'Post {post_id}'})
#     post = pseudo_db['posts'][post_id]
#
#     context = {
#         'post': post,
#         'title': f'Post {post["title"]}'
#     }
#     return render(request, 'post_detail.html', context)

# def post_list(request: HttpRequest) -> HttpResponse:
#     if request.method == 'POST':
#         title = request.POST.get('title')
#         content = request.POST.get('content')
#         new_post = {'id': len(pseudo_db['posts']) + 1, 'title': title,
#                     'content': content}
#         pseudo_db['posts'][new_post['id']] = new_post
#     posts = [p for p in pseudo_db['posts'].values()]
#     context: dict[str, Any] = {
#         'title': 'All posts',
#         'posts': posts,
#     }
#     return render(request, 'post_list.html', context)

# def get_post_comments(request, post_id):
#     if request.method == 'POST':
#         content = request.POST.get('content')
#         new_comment = {'post_id': post_id, 'content': content}
#         pseudo_db['comments'][len(pseudo_db['comments']) + 1] = new_comment
#         return redirect('blog:comments', post_id=post_id)
#
#     if post_id not in pseudo_db['posts']:
#         return render(request, '404.html', {'instance': f'Post {post_id}'})
#     comments = [c for c in pseudo_db['comments'].values() if
#                 c['post_id'] == post_id]
#     context = {
#         'comments': comments,
#         'post_id': post_id,
#         'title': f'Comments for post {post_id}'
#     }
#
#     return render(request, 'comment_list.html', context)

class PostDetailView(View):
    def get(self, request, post_id):
        if not Post.objects.filter(id=post_id).exists():
            return render(
                request,
                '404.html',
                {'instance': f'Post {post_id}'},
                status=404,
            )
        post = Post.objects.get(id=post_id)
        return render(request, 'post_detail.html', {'post': post})


class PostListView(View):
    def get(self, request: HttpRequest):
        posts = Post.objects.prefetch_related('tags').all()
        context: dict[str, Any] = {
            'title': 'All posts',
            'posts': posts,
        }
        return render(self.request, 'post_list.html', context)


class PostCreateView(View):
    def get(self, request):
        return render(self.request, 'create_post.html')

    def post(self, request):
        title = self.request.POST.get('title')
        content = self.request.POST.get('content')
        tags = self.request.POST.get('tags').split(',')
        new_post = Post()
        new_post.title = title
        new_post.content = content
        new_post.save()

        for tag in tags:
            new_post.tags.add(
                Tag.objects.get_or_create(name=tag.strip().title())[0]
            )
        return redirect('blog:post_detail', post_id=new_post.id)


class PostDeleteView(View):
    def post(self, request, post_id):
        if Post.objects.filter(id=post_id).exists():
            Post.objects.get(id=post_id).delete()
        return redirect('blog:post_list')


class PostUpdateView(View):
    def get(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        return render(self.request, 'update_post.html', {'post': post})

    def post(self, request, post_id):
        Post.objects.filter(id=post_id).update(
            title=self.request.POST.get('title'),
            content=self.request.POST.get('content')
        )
        return redirect('blog:post_detail', post_id=post_id)

    # def post(self, request, post_id):
    #     post = get_object_or_404(Post, id=post_id)
    #     post.title = self.request.POST.get('title')
    #     post.content = self.request.POST.get('content')
    #     post.save(update_fields=['title', 'content'])
    #     return redirect('blog:post_detail', post_id=post.id)


class CommentListView(View):
    def get(self, request, post_id):
        if not Post.objects.filter(id=post_id).exists():
            return render(
                request,
                '404.html',
                {'instance': f'Post {post_id}'},
                status=404,
            )
        post = Post.objects.get(id=post_id)  # .select_related('comments')
        return render(request, 'comment_list.html', {'post': post})

    def post(self, request, post_id):
        content = request.POST.get('content')
        post = Post.objects.get(id=post_id)
        Comment.objects.create(content=content, post=post)
        return redirect('blog:comments', post_id=post_id)
