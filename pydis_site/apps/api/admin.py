import json
from typing import Optional, Tuple

from django import urls
from django.contrib import admin
from django.db.models.query import QuerySet
from django.http import HttpRequest
from django.utils.html import format_html

from .models import (
    BotSetting,
    DeletedMessage,
    DocumentationLink,
    Infraction,
    LogEntry,
    MessageDeletionContext,
    Nomination,
    OffTopicChannelName,
    OffensiveMessage,
    Role,
    User
)


class LogEntryAdmin(admin.ModelAdmin):
    """Allows viewing logs in the Django Admin without allowing edits."""

    actions = None
    list_display = ('timestamp', 'application', 'level', 'message')
    fieldsets = (
        ('Overview', {'fields': ('timestamp', 'application', 'logger_name')}),
        ('Metadata', {'fields': ('level', 'module', 'line')}),
        ('Contents', {'fields': ('message',)})
    )
    list_filter = ('application', 'level', 'timestamp')
    search_fields = ('message',)
    readonly_fields = (
        'application',
        'logger_name',
        'timestamp',
        'level',
        'module',
        'line',
        'message'
    )

    def has_add_permission(self, request: HttpRequest) -> bool:
        """Deny manual LogEntry creation."""
        return False

    def has_delete_permission(self, request: HttpRequest, obj: Optional[LogEntry] = None) -> bool:
        """Deny LogEntry deletion."""
        return False


class DeletedMessageAdmin(admin.ModelAdmin):
    """Admin formatting for the DeletedMessage model."""

    readonly_fields = (
        "id",
        "author",
        "channel_id",
        "content",
        "embed_data",
        "context",
        "view_full_log"
    )

    exclude = ("embeds", "deletion_context")

    search_fields = (
        "id",
        "content",
        "author__name",
        "author__id",
        "deletion_context__actor__name",
        "deletion_context__actor__id"
    )

    @staticmethod
    def embed_data(instance: DeletedMessage) -> Optional[str]:
        """Format embed data in a code block for better readability."""
        if instance.embeds:
            return format_html(
                "<pre style='word-wrap: break-word; white-space: pre-wrap; overflow-x: auto;'>"
                "<code>{0}</code></pre>",
                json.dumps(instance.embeds, indent=4)
            )

    @staticmethod
    def context(instance: DeletedMessage) -> str:
        """Provide full context info with a link through to context admin view."""
        link = urls.reverse(
            "admin:api_messagedeletioncontext_change",
            args=[instance.deletion_context.id]
        )
        details = (
            f"Deleted by {instance.deletion_context.actor} at "
            f"{instance.deletion_context.creation}"
        )
        return format_html("<a href='{0}'>{1}</a>", link, details)

    @staticmethod
    def view_full_log(instance: DeletedMessage) -> str:
        """Provide a link to the message logs for the relevant context."""
        return format_html(
            "<a href='{0}'>Click to view full context log</a>",
            instance.deletion_context.log_url
        )


class MessageDeletionContextAdmin(admin.ModelAdmin):
    """Admin formatting for the MessageDeletionContext model."""

    readonly_fields = ("actor", "creation", "message_log")

    @staticmethod
    def message_log(instance: MessageDeletionContext) -> str:
        """Provide a formatted link to the message logs for the context."""
        return format_html(
            "<a href='{0}'>Click to see deleted message log</a>",
            instance.log_url
        )


class InfractionAdmin(admin.ModelAdmin):
    """Admin formatting for the Infraction model."""

    fields = (
        "user",
        "actor",
        "type",
        "reason",
        "inserted_at",
        "expires_at",
        "active",
        "hidden"
    )
    readonly_fields = (
        "user",
        "actor",
        "type",
        "inserted_at"
    )
    list_display = (
        "type",
        "user",
        "actor",
        "inserted_at",
        "expires_at",
        "reason",
        "active",
    )
    search_fields = (
        "id",
        "user__name",
        "user__id",
        "actor__name",
        "actor__id",
        "reason",
        "type"
    )
    list_filter = (
        "type",
        "hidden",
        "active"
    )


class NominationAdmin(admin.ModelAdmin):
    """Admin formatting for the Nomination model."""

    list_display = (
        "user",
        "active",
        "reason",
        "actor",
        "inserted_at",
        "ended_at"
    )
    fields = (
        "user",
        "active",
        "actor",
        "reason",
        "inserted_at",
        "ended_at",
        "end_reason"
    )
    readonly_fields = (
        "user",
        "active",
        "actor",
        "inserted_at",
        "ended_at"
    )
    search_fields = (
        "actor__name",
        "actor__id",
        "user__name",
        "user__id",
        "reason"
    )
    list_filter = ("active",)


class OffTopicChannelNameAdmin(admin.ModelAdmin):
    """Admin formatting for the OffTopicChannelName model."""

    search_fields = ("name",)


class RoleAdmin(admin.ModelAdmin):
    """Admin formatting for the Role model."""

    exclude = ("permissions", "colour")
    readonly_fields = (
        "name",
        "id",
        "colour_with_preview",
        "permissions_with_calc_link",
        "position"
    )
    search_fields = ("name", "id")

    def colour_with_preview(self, instance: Role) -> str:
        """Show colour value in both int and hex, in bolded and coloured style."""
        return format_html(
            "<span style='color: #{0}!important; font-weight: bold;'>{1} / #{0}</span>",
            f"{instance.colour:06x}",
            instance.colour
        )

    def permissions_with_calc_link(self, instance: Role) -> str:
        """Show permissions with link to API permissions calculator page."""
        return format_html(
            "<a href='https://discordapi.com/permissions.html#{0}' target='_blank'>{0}</a>",
            instance.permissions
        )

    colour_with_preview.short_description = "Colour"
    permissions_with_calc_link.short_description = "Permissions"


class TagAdmin(admin.ModelAdmin):
    """Admin formatting for the Tag model."""

    fields = ("title", "embed", "preview")
    readonly_fields = ("preview",)
    search_fields = ("title", "embed")

    @staticmethod
    def preview(instance: Tag) -> Optional[str]:
        """Render tag markdown contents to preview actual appearance."""
        if instance.embed:
            import markdown
            return format_html(
                markdown.markdown(
                    instance.embed["description"],
                    extensions=[
                        "markdown.extensions.nl2br",
                        "markdown.extensions.extra"
                    ]
                )
            )


class StaffRolesFilter(admin.SimpleListFilter):
    """Filter options for Staff Roles."""

    title = "Staff Role"
    parameter_name = "staff_role"

    @staticmethod
    def lookups(*_) -> Tuple[Tuple[str, str], ...]:
        """Available filter options."""
        return (
            ("Owners", "Owners"),
            ("Admins", "Admins"),
            ("Moderators", "Moderators"),
            ("Core Developers", "Core Developers"),
            ("Helpers", "Helpers"),
        )

    def queryset(self, request: HttpRequest, queryset: QuerySet) -> Optional[QuerySet]:
        """Returned data filter based on selected option."""
        value = self.value()
        if value:
            return queryset.filter(roles__name=value)


class UserAdmin(admin.ModelAdmin):
    """Admin formatting for the User model."""

    search_fields = ("name", "id", "roles__name", "roles__id")
    list_filter = ("in_guild", StaffRolesFilter)
    exclude = ("name", "discriminator")
    readonly_fields = (
        "__str__",
        "id",
        "avatar_hash",
        "top_role",
        "roles",
        "in_guild",
    )


admin.site.register(BotSetting)
admin.site.register(DeletedMessage, DeletedMessageAdmin)
admin.site.register(DocumentationLink)
admin.site.register(Infraction, InfractionAdmin)
admin.site.register(LogEntry, LogEntryAdmin)
admin.site.register(MessageDeletionContext, MessageDeletionContextAdmin)
admin.site.register(Nomination, NominationAdmin)
admin.site.register(OffensiveMessage)
admin.site.register(OffTopicChannelName, OffTopicChannelNameAdmin)
admin.site.register(Role, RoleAdmin)
admin.site.register(User, UserAdmin)
