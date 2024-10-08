# Generated by Django 4.2.15 on 2024-10-05 03:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('places', '0009_alter_rental_num_bathrooms_alter_rental_num_bedrooms_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='building',
            name='latitude',
            field=models.DecimalField(decimal_places=6, max_digits=9),
        ),
        migrations.AlterField(
            model_name='building',
            name='longitude',
            field=models.DecimalField(decimal_places=6, max_digits=9),
        ),
        migrations.AlterField(
            model_name='building',
            name='name',
            field=models.CharField(max_length=255, unique=True),
        ),
    ]
