# Generated by Django 4.2 on 2023-12-21 11:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0050_alter_productstorage_storage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productstorage',
            name='storage',
            field=models.CharField(default='1000', max_length=50),
        ),
    ]
