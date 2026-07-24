from rest_framework.response import Response
from rest_framework.views import APIView

from apps.blog.models import Post
from apps.blog.serializers import FullPostSerializer, ShortPostSerializer, \
    CreatePostSerializer, PartialUpdatePostSerializer


class PostListApiView(APIView):

    def get(self, request):
        posts = [ShortPostSerializer(p).data for p in Post.objects.all()]
        return Response({"posts": posts})

    def post(self, request):
        instance = CreatePostSerializer(data=request.data)
        instance.is_valid(raise_exception=True)
        instance.save()
        return Response(status=201, data={"created": True})


class PostDetailApiView(APIView):
    def get(self, request, post_id):
        post = Post.objects.get(id=post_id)
        return Response({"post": FullPostSerializer(post).data})

    def patch(self, request, post_id):
        post = Post.objects.get(id=post_id)
        instance = PartialUpdatePostSerializer(post, data=request.data)
        instance.is_valid(raise_exception=True)
        instance.save()
        return Response(status=200, data={"updated": True})

    def put(self, request, post_id):
        post = Post.objects.get(id=post_id)
        instance = FullPostSerializer(post, data=request.data)
        instance.is_valid(raise_exception=True)
        instance.save()
        return Response(status=200, data={"updated": True})

    def delete(self, request, post_id):
        post = Post.objects.get(id=post_id)
        post.delete()
        return Response(status=200, data={"deleted": True})