# Generated by Django 4.2.15 on 2024-09-17 12:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('establishment', '0004_alter_businesssubcategory_categories'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='businesscategory',
            options={'managed': True, 'ordering': ['name'], 'verbose_name': 'Business Category', 'verbose_name_plural': 'Business Categories'},
        ),
        migrations.AlterModelOptions(
            name='businesssubcategory',
            options={'managed': True, 'ordering': ['name'], 'verbose_name': 'Business Sub Category', 'verbose_name_plural': 'Business Sub Categories'},
        ),
        migrations.AddField(
            model_name='businesscategory',
            name='map_icon',
            field=models.ImageField(blank=True, null=True, upload_to='images/map/icon/'),
        ),
    ]