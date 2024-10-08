# Generated by Django 5.1.1 on 2024-10-07 09:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vtuApp', '0007_remove_comment_parent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='image',
            field=models.URLField(),
        ),
        migrations.AlterField(
            model_name='profile',
            name='profileimg',
            field=models.URLField(default='profile_images/blank-profile-picture.png'),
        ),
    ]
