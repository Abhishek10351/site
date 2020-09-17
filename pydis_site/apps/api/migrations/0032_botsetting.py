# Generated by Django 2.1.5 on 2019-02-07 19:03

import pydis_site.apps.api.models
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0031_nomination'),
    ]

    operations = [
        migrations.CreateModel(
            name='BotSetting',
            fields=[
                ('name', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('data', django.contrib.postgres.fields.jsonb.JSONField(help_text='The actual settings of this setting.')),
            ],
            bases=(pydis_site.apps.api.models.mixins.ModelReprMixin, models.Model),
        ),
    ]
