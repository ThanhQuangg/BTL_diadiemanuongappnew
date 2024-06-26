# Generated by Django 4.2.11 on 2024-05-17 09:02

import cloudinary.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('diadiemanuong', '0012_restaurant_is_approved_alter_restaurant_active'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='dish',
            options={},
        ),
        migrations.AddField(
            model_name='restaurant',
            name='avatar',
            field=cloudinary.models.CloudinaryField(max_length=255, null=True, verbose_name='avatar'),
        ),
        migrations.AlterField(
            model_name='restaurant',
            name='tags',
            field=models.ManyToManyField(null=True, to='diadiemanuong.tag'),
        ),
        migrations.AlterUniqueTogether(
            name='dish',
            unique_together={('name', 'restaurant')},
        ),
        migrations.CreateModel(
            name='Follow',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('active', models.BooleanField(default=True)),
                ('follower', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('restaurant', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='diadiemanuong.restaurant')),
            ],
            options={
                'ordering': ['id'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Bill',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bill_code', models.CharField(blank=True, max_length=200, null=True)),
                ('total_amount', models.FloatField(blank=True, default=0, null=True)),
                ('bill_transactionNo', models.CharField(blank=True, max_length=200, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('order', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='bill', to='diadiemanuong.order')),
            ],
        ),
    ]
