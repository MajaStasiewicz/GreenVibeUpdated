# Generated by Django 4.2 on 2024-01-12 14:00

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('products', '0086_rename_key_order_key_session_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderhistory',
            name='key_session',
        ),
        migrations.AlterField(
            model_name='orderhistory',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='OrderUserSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product', models.CharField(max_length=100)),
                ('key_session', models.CharField(max_length=70)),
                ('option', models.CharField(max_length=50)),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('price', models.DecimalField(decimal_places=2, default=0, max_digits=20, validators=[django.core.validators.MinValueValidator(0)])),
                ('priceOrder', models.FloatField(default=0)),
                ('delivery_status', models.CharField(choices=[('Realizacja', 'Realizacja'), ('Przesłano', 'Przesłano'), ('Doręczono', 'Doręczono')], default='Realizacja', max_length=20)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.order')),
            ],
        ),
    ]