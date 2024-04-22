# Generated by Django 4.2 on 2024-01-12 12:17

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('products', '0083_code_key'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='key',
            field=models.CharField(default=1, max_length=70),
        ),
        migrations.AddField(
            model_name='orderhistory',
            name='key',
            field=models.CharField(default=1, max_length=70),
        ),
        migrations.AlterField(
            model_name='order',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='orderhistory',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
