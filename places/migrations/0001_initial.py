# Generated by Django 4.2.15 on 2024-10-02 13:34

from django.db import migrations, models
import django.db.models.deletion
import django_admin_geomap


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('user_profile', '0003_userprofile_photo_alter_userprofile_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='Amenity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Building',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('address', models.CharField(max_length=255)),
                ('longitude', models.FloatField()),
                ('latitude', models.FloatField()),
                ('is_food_establishment', models.BooleanField(default=False)),
                ('map_icon', models.ImageField(blank=True, null=True, upload_to='images/map/icon/')),
                ('amenities', models.ManyToManyField(related_name='buildings', to='places.amenity')),
            ],
            options={
                'ordering': ['-updated_at'],
                'managed': True,
            },
            bases=(models.Model, django_admin_geomap.GeoItem),
        ),
        migrations.CreateModel(
            name='Accommodation',
            fields=[
                ('building_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='places.building')),
                ('num_bedrooms', models.IntegerField()),
                ('num_bathrooms', models.IntegerField()),
                ('kitchen', models.BooleanField(default=False)),
                ('air_conditioning', models.BooleanField(default=False)),
                ('wifi', models.BooleanField(default=False)),
                ('pets_allowed', models.BooleanField(default=False)),
                ('price_per_night', models.DecimalField(decimal_places=2, max_digits=10)),
                ('property_condition', models.CharField(choices=[('NEW', 'New'), ('GOOD', 'Good'), ('FAIR', 'Fair'), ('OLD', 'Old')], default='GOOD', max_length=10)),
                ('furniture_condition', models.CharField(choices=[('NEW', 'New'), ('GOOD', 'Good'), ('USED', 'Used')], default='GOOD', max_length=10)),
                ('lease_term', models.CharField(choices=[('SHORT_TERM', 'Short-term'), ('LONG_TERM', 'Long-term'), ('MONTH_TO_MONTH', 'Month-to-month')], default='LONG_TERM', max_length=20)),
                ('monthly_rent', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
            options={
                'abstract': False,
            },
            bases=('places.building',),
        ),
        migrations.CreateModel(
            name='FoodEstablishment',
            fields=[
                ('building_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='places.building')),
                ('cuisine_type', models.CharField(max_length=255)),
                ('opening_time', models.TimeField()),
                ('closing_time', models.TimeField()),
                ('preview_photos', models.ImageField(blank=True, null=True, upload_to='preview_photos/')),
            ],
            options={
                'abstract': False,
            },
            bases=('places.building',),
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='subcategories', to='places.category')),
            ],
            options={
                'verbose_name_plural': 'Categories',
            },
        ),
        migrations.CreateModel(
            name='BuildingPhoto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('image', models.ImageField(upload_to='building_photos/')),
                ('building', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='photos', to='places.building')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='building',
            name='categories',
            field=models.ManyToManyField(related_name='buildings', to='places.category'),
        ),
        migrations.AddField(
            model_name='building',
            name='user_profile',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_building', to='user_profile.userprofile'),
        ),
    ]