# Generated by Django 4.2 on 2023-12-02 15:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0038_remove_useritem_added_order_date_useritem_date_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='useritem',
            name='date',
        ),
    ]