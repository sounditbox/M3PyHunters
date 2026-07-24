from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.blog.models import Post, Comment
from apps.blog.validators import agreed_to_terms


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('id', 'username', 'email')


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField()

    class Meta:
        model = Comment
        exclude = ('post',)


class FullPostSerializer(serializers.ModelSerializer):
    author = AuthorSerializer()
    comments = CommentSerializer(many=True)

    class Meta:
        model = Post
        fields = '__all__'


class ShortPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ('id', 'title', 'author', 'created_at')


class CreatePostSerializer(serializers.ModelSerializer):
    user_agreement = serializers.BooleanField(validators=[agreed_to_terms])

    class Meta:
        model = Post
        fields = ('title', 'content', 'author', 'user_agreement')

    def validate_title(self, value):
        if 'test' in value or 'Test' in value:
            raise serializers.ValidationError("Title is not allowed")
        return value

    def create(self, validated_data):
        validated_data.pop('user_agreement')
        post = super().create(validated_data)
        post.save()
        return post


class PartialUpdatePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ('title', 'content')
        extra_kwargs = {'title': {'required': False},
                        'content': {'required': False}}
