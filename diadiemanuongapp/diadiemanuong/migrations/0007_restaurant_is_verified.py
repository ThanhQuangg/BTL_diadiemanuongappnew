# Generated by Django 4.2.11 on 2024-05-13 15:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('diadiemanuong', '0006_delete_userrole_dish_address'),
    ]

    operations = [
        migrations.AddField(
            model_name='restaurant',
            name='is_verified',
            field=models.BooleanField(default=False),
        ),
    ]