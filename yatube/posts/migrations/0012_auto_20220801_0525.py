# Generated by Django 2.2.16 on 2022-08-01 00:25

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('posts', '0011_auto_20220801_0301'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='follow',
            options={'verbose_name': 'Подписка', 'verbose_name_plural': 'Подписки'},
        ),
        migrations.AlterUniqueTogether(
            name='follow',
            unique_together={('user', 'author')},
        ),
    ]
