# Generated by Django 4.0.6 on 2022-07-27 20:32

import django.utils.timezone
from django.db import migrations, models
from django.apps.registry import Apps


def set_last_applied_to_inserted_at(apps: Apps, schema_editor):
    Infractions = apps.get_model("api", "infraction")
    Infractions.objects.all().update(last_applied=models.F("inserted_at"))


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0083_remove_embed_validation'),
    ]

    operations = [
        migrations.AddField(
            model_name='infraction',
            name='last_applied',
            field=models.DateTimeField(default=django.utils.timezone.now, help_text='The date and time of when this infraction was last applied.'),
        ),
        migrations.RunPython(set_last_applied_to_inserted_at, elidable=True)
    ]
