from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('blog', '0007_post_cover'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='post',
            index=models.Index(fields=['status'], name='blog_post_status_idx'),
        ),
        migrations.AddIndex(
            model_name='post',
            index=models.Index(fields=['title'], name='blog_post_title_idx'),
        ),
        migrations.AddIndex(
            model_name='post',
            index=models.Index(
                fields=['created_at'], name='blog_post_created_idx'
            ),
        ),
        migrations.AddIndex(
            model_name='post',
            index=models.Index(
                fields=['updated_at'], name='blog_post_updated_idx'
            ),
        ),
        migrations.AddIndex(
            model_name='post',
            index=models.Index(fields=['likes'], name='blog_post_likes_idx'),
        ),
        migrations.AddIndex(
            model_name='post',
            index=models.Index(fields=['views'], name='blog_post_views_idx'),
        ),
    ]
