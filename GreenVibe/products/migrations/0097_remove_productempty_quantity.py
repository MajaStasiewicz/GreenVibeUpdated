# Generated by Django 4.2 on 2024-01-18 18:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0096_useraddress'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='productempty',
            name='quantity',
        ),
    ]
