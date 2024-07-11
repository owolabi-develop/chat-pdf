# Generated by Django 4.2.13 on 2024-07-10 01:47

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('chatpdf', '0003_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chatsession',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
