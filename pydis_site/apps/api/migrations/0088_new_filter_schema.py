"""Modified migration file to migrate existing filters to the new system."""
from datetime import timedelta

import django.contrib.postgres.fields
from django.apps.registry import Apps
from django.core.validators import MinValueValidator
from django.db import migrations, models
import django.db.models.deletion
from django.db.backends.base.schema import BaseDatabaseSchemaEditor

import pydis_site.apps.api.models

OLD_LIST_NAMES = (('GUILD_INVITE', True), ('GUILD_INVITE', False), ('FILE_FORMAT', True), ('DOMAIN_NAME', False), ('FILTER_TOKEN', False), ('REDIRECT', False))
change_map = {
    "FILTER_TOKEN": "token",
    "DOMAIN_NAME": "domain",
    "GUILD_INVITE": "invite",
    "FILE_FORMAT": "extension",
    "REDIRECT": "redirect"
}


def forward(apps: Apps, schema_editor: BaseDatabaseSchemaEditor) -> None:
    filter_: pydis_site.apps.api.models.Filter = apps.get_model("api", "Filter")
    filter_list: pydis_site.apps.api.models.FilterList = apps.get_model("api", "FilterList")
    filter_list_old = apps.get_model("api", "FilterListOld")

    for name, type_ in OLD_LIST_NAMES:
        objects = filter_list_old.objects.filter(type=name, allowed=type_)
        if name == "DOMAIN_NAME":
            dm_content = "Your message has been removed because it contained a blocked domain: `{domain}`."
        elif name == "GUILD_INVITE":
            dm_content = "Per Rule 6, your invite link has been removed. " \
                         "Our server rules can be found here: https://pythondiscord.com/pages/rules"
        else:
            dm_content = ""

        list_ = filter_list.objects.create(
            name=change_map[name],
            list_type=int(type_),
            guild_pings=(["Moderators"] if name != "FILE_FORMAT" else []),
            filter_dm=True,
            dm_pings=[],
            remove_context=(True if name != "FILTER_TOKEN" else False),
            bypass_roles=["Helpers"],
            enabled=True,
            dm_content=dm_content,
            dm_embed="" if name != "FILE_FORMAT" else "*Defined at runtime.*",
            infraction_type="NONE",
            infraction_reason="",
            infraction_duration=timedelta(seconds=0),
            infraction_channel=0,
            disabled_channels=[],
            disabled_categories=(["CODE JAM"] if name in ("FILE_FORMAT", "GUILD_INVITE") else []),
            enabled_channels=[],
            enabled_categories=[],
            send_alert=(name in ('GUILD_INVITE', 'DOMAIN_NAME', 'FILTER_TOKEN'))
        )

        for object_ in objects:
            new_object = filter_.objects.create(
                content=object_.content,
                created_at=object_.created_at,
                updated_at=object_.updated_at,
                filter_list=list_,
                description=object_.comment,
                additional_settings={},
                guild_pings=None,
                filter_dm=None,
                dm_pings=None,
                remove_context=None,
                bypass_roles=None,
                enabled=None,
                dm_content=None,
                dm_embed=None,
                infraction_type=None,
                infraction_reason=None,
                infraction_duration=None,
                infraction_channel=None,
                disabled_channels=None,
                disabled_categories=None,
                enabled_channels=None,
                enabled_categories=None,
                send_alert=None,
            )
            new_object.save()


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0087_alter_mute_to_timeout'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='FilterList',
            new_name='FilterListOld'
        ),
        migrations.CreateModel(
            name='Filter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('content', models.TextField(help_text='The definition of this filter.')),
                ('description', models.TextField(help_text='Why this filter has been added.', null=True)),
                ('additional_settings', models.JSONField(help_text='Additional settings which are specific to this filter.', default=dict)),
                ('guild_pings', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=100), help_text='Who to ping when this filter triggers.', size=None, null=True)),
                ('filter_dm', models.BooleanField(help_text='Whether DMs should be filtered.', null=True)),
                ('dm_pings', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=100), help_text='Who to ping when this filter triggers on a DM.', size=None, null=True)),
                ('remove_context', models.BooleanField(help_text='Whether this filter should remove the context (such as a message) triggering it.', null=True)),
                ('bypass_roles', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=100), help_text='Roles and users who can bypass this filter.', size=None, null=True)),
                ('enabled', models.BooleanField(help_text='Whether this filter is currently enabled.', null=True)),
                ('dm_content', models.CharField(help_text='The DM to send to a user triggering this filter.', max_length=1000, null=True, blank=True)),
                ('dm_embed', models.CharField(help_text='The content of the DM embed', max_length=2000, null=True, blank=True)),
                ('infraction_type', models.CharField(choices=[('NONE', 'None'), ('NOTE', 'Note'), ('WARNING', 'Warning'), ('WATCH', 'Watch'), ('TIMEOUT', 'Timeout'), ('KICK', 'Kick'), ('BAN', 'Ban'), ('SUPERSTAR', 'Superstar'), ('VOICE_BAN', 'Voice Ban'), ('VOICE_MUTE', 'Voice Mute')], help_text='The infraction to apply to this user.', max_length=10, null=True)),
                ('infraction_reason', models.CharField(help_text='The reason to give for the infraction.', max_length=1000, null=True, blank=True)),
                ('infraction_duration', models.DurationField(help_text='The duration of the infraction. 0 for permanent.', null=True)),
                ('infraction_channel', models.BigIntegerField(validators=(MinValueValidator(limit_value=0, message="Channel IDs cannot be negative."),), help_text="Channel in which to send the infraction.", null=True)),
                ('disabled_channels', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=100), help_text="Channels in which to not run the filter even if it's enabled in the category.", null=True, size=None)),
                ('disabled_categories', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=100), help_text="Categories in which to not run the filter.", null=True, size=None)),
                ('enabled_channels', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=100), help_text="Channels in which to run the filter even if it's disabled in the category.", null=True, size=None)),
                ('enabled_categories', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=100), help_text="The only categories in which to run the filter.", null=True, size=None)),
                ('send_alert', models.BooleanField(help_text='Whether an alert should be sent.', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='FilterList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(help_text='The unique name of this list.', max_length=50)),
                ('list_type', models.IntegerField(choices=[(1, 'Allow'), (0, 'Deny')], help_text='Whether this list is an allowlist or denylist')),
                ('guild_pings', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=100), help_text='Who to ping when this filter triggers.', size=None)),
                ('filter_dm', models.BooleanField(help_text='Whether DMs should be filtered.')),
                ('dm_pings', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=100), help_text='Who to ping when this filter triggers on a DM.', size=None)),
                ('remove_context', models.BooleanField(help_text='Whether this filter should remove the context (such as a message) triggering it.')),
                ('bypass_roles', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=100), help_text='Roles and users who can bypass this filter.', size=None)),
                ('enabled', models.BooleanField(help_text='Whether this filter is currently enabled.')),
                ('dm_content', models.CharField(help_text='The DM to send to a user triggering this filter.', max_length=1000, blank=True)),
                ('dm_embed', models.CharField(help_text='The content of the DM embed', max_length=2000, blank=True)),
                ('infraction_type', models.CharField(choices=[('NONE', 'None'), ('NOTE', 'Note'), ('WARNING', 'Warning'), ('WATCH', 'Watch'), ('TIMEOUT', 'Timeout'), ('KICK', 'Kick'), ('BAN', 'Ban'), ('SUPERSTAR', 'Superstar'), ('VOICE_BAN', 'Voice Ban'), ('VOICE_MUTE', 'Voice Mute')], help_text='The infraction to apply to this user.', max_length=10)),
                ('infraction_reason', models.CharField(help_text='The reason to give for the infraction.', max_length=1000, blank=True)),
                ('infraction_duration', models.DurationField(help_text='The duration of the infraction. 0 for permanent.')),
                ('infraction_channel', models.BigIntegerField(validators=(MinValueValidator(limit_value=0, message="Channel IDs cannot be negative."),), help_text="Channel in which to send the infraction.")),
                ('disabled_channels', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=100), help_text="Channels in which to not run the filter even if it's enabled in the category.", size=None)),
                ('disabled_categories', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=100), help_text="Categories in which to not run the filter.", size=None)),
                ('enabled_channels', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=100), help_text="Channels in which to run the filter even if it's disabled in the category.", size=None)),
                ('enabled_categories', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=100), help_text="The only categories in which to run the filter.", size=None)),
                ('send_alert', models.BooleanField(help_text='Whether an alert should be sent.')),
            ],
        ),
        migrations.AddField(
            model_name='filter',
            name='filter_list',
            field=models.ForeignKey(help_text='The filter list containing this filter.', on_delete=django.db.models.deletion.CASCADE, related_name='filters', to='api.FilterList'),
        ),
        migrations.AddConstraint(
            model_name='filterlist',
            constraint=models.UniqueConstraint(fields=('name', 'list_type'), name='unique_name_type'),
        ),
        migrations.RunPython(
            code=forward,  # Core of the migration
            reverse_code=None,
            elidable=True,
        ),
        migrations.DeleteModel(
            name='FilterListOld'
        )
    ]
