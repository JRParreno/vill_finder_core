# Generated by Django 4.2.15 on 2024-12-12 15:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('places', '0022_review_sentiment_label_review_sentiment_score'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='review',
            name='stars',
        ),
    ]