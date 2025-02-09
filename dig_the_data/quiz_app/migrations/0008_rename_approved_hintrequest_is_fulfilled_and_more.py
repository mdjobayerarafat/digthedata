# Generated by Django 5.1.6 on 2025-02-07 16:37

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz_app', '0007_answer_is_correct'),
    ]

    operations = [
        migrations.RenameField(
            model_name='hintrequest',
            old_name='approved',
            new_name='is_fulfilled',
        ),
        migrations.AlterField(
            model_name='hintrequest',
            name='requested_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.CreateModel(
            name='Hint',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hint_text', models.TextField()),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quiz_app.question')),
            ],
        ),
        migrations.AddField(
            model_name='hintrequest',
            name='hint',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='quiz_app.hint'),
        ),
    ]
