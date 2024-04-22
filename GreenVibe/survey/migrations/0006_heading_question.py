# Generated by Django 4.2 on 2024-01-13 12:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0005_rename_question3_pytania3_rename_question4_pytania4'),
    ]

    operations = [
        migrations.CreateModel(
            name='Heading',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('heading', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.CharField(max_length=200)),
                ('heading', models.CharField(max_length=100)),
                ('answer1', models.CharField(max_length=100)),
                ('answer2', models.CharField(max_length=100)),
                ('answer3', models.CharField(max_length=100)),
                ('answer4', models.CharField(max_length=100)),
            ],
        ),
    ]
