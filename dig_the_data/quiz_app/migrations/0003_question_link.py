# Generated by Django 5.1.6 on 2025-02-06 15:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz_app', '0002_remove_question_is_common_remove_question_link_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='link',
            field=models.URLField(blank=True, null=True),
        ),
    ]
