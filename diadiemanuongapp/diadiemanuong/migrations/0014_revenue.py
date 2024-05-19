# Generated by Django 4.2.11 on 2024-05-19 03:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('diadiemanuong', '0013_alter_dish_options_restaurant_avatar_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Revenue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('restaurant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='diadiemanuong.restaurant')),
            ],
        ),
    ]