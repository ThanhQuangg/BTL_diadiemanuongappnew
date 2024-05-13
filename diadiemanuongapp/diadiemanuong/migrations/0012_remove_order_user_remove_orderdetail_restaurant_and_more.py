# Generated by Django 4.2.11 on 2024-05-10 10:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('diadiemanuong', '0011_remove_orderdetail_product_id_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='user',
        ),
        migrations.RemoveField(
            model_name='orderdetail',
            name='restaurant',
        ),
        migrations.AddField(
            model_name='orderdetail',
            name='restaurant_image',
            field=models.ImageField(null=True, upload_to='restaurants_image/%Y/%m'),
        ),
        migrations.AddField(
            model_name='orderdetail',
            name='restaurant_name',
            field=models.CharField(max_length=255, null=True),
        ),
    ]