# Generated by Django 4.2.15 on 2024-09-15 19:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('establishment', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='businesscategory',
            options={'managed': True, 'ordering': ['-updated_at'], 'verbose_name': 'Business Category', 'verbose_name_plural': 'Business Categories'},
        ),
        migrations.AlterModelOptions(
            name='businesssubcategory',
            options={'managed': True, 'ordering': ['-updated_at'], 'verbose_name': 'Business Sub Category', 'verbose_name_plural': 'Business Sub Categories'},
        ),
        migrations.AlterField(
            model_name='businesssubcategory',
            name='categories',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sub_categories', to='establishment.businesscategory'),
        ),
    ]