# Generated by Django 4.2.11 on 2024-05-16 00:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('diadiemanuong', '0011_remove_restaurant_is_approved_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='restaurant',
            name='is_approved',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='restaurant',
            name='active',
            field=models.BooleanField(default=False),
        ),
    ]
