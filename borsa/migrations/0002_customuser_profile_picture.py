# Generated by Django 5.1.6 on 2025-03-03 13:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('borsa', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='profile_picture',
            field=models.ImageField(blank=True, null=True, upload_to='profile_pics/'),
        ),
    ]
