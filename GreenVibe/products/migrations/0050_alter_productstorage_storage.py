# Generated by Django 4.2 on 2023-12-21 09:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0049_rename_usage_productstorage_option'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productstorage',
            name='storage',
            field=models.PositiveIntegerField(default='1000'),
        ),
    ]