# Generated by Django 4.2 on 2023-11-22 19:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0024_alter_product_composition_alter_product_description'),
    ]

    operations = [
        migrations.CreateModel(
            name='Code',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=10)),
                ('value', models.PositiveIntegerField(default=1)),
            ],
        ),
    ]
