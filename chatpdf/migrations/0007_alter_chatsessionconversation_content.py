# Generated by Django 4.2.13 on 2024-07-12 15:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chatpdf', '0006_summary'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chatsessionconversation',
            name='content',
            field=models.JSONField(),
        ),
    ]
