# Generated by Django 4.2.11 on 2024-05-14 10:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('diadiemanuong', '0009_userrole_restaurant_user_alter_restaurant_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='restaurant',
            name='is_approved',
            field=models.BooleanField(default=False),
        ),
    ]
