# Generated by Django 5.1.4 on 2025-02-15 08:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0002_remove_newsarticle_genre_newsarticle_genres_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='newsarticle',
            old_name='user',
            new_name='user_id',
        ),
    ]
