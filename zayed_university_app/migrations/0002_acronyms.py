# Generated by Django 3.2 on 2023-02-26 14:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('zayed_university_app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Acronyms',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('short_form', models.CharField(max_length=50)),
                ('long_form', models.CharField(blank=True, max_length=30)),
            ],
        ),
    ]