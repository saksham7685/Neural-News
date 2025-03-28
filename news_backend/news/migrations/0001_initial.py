# Generated by Django 5.1.4 on 2025-02-08 15:20

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='NewsArticle',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('title', models.CharField(max_length=500)),
                ('content', models.TextField()),
                ('source', models.CharField(max_length=255)),
                ('url', models.URLField(unique=True)),
                ('published_at', models.DateTimeField()),
                ('genre', models.CharField(blank=True, max_length=50)),
                ('credibility_score', models.FloatField(default=0.0)),
                ('bias_score', models.FloatField(default=0.0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
