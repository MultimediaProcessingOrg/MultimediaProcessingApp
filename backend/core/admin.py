from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import (
    Job,
    MediaMetadata,
    OperationHistory,
    OutputFile,
    SourceFile,
    User,
)

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("username", "email", "role", "is_staff", "is_superuser", "is_active")
    list_filter = ("role", "is_staff", "is_superuser", "is_active")
    fieldsets = BaseUserAdmin.fieldsets + (("Rola domenowa", {"fields": ("role",)}),)
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ("Rola domenowa", {"fields": ("role",)}),
    )

@admin.register(SourceFile)
class SourceFileAdmin(admin.ModelAdmin):
    list_display = ("id", "original_name", "owner", "status", "size_bytes", "mime_type", "uploaded_at")
    list_filter = ("status", "is_deleted", "mime_type")
    search_fields = ("original_name", "sha256", "owner__username")
    readonly_fields = ("id", "sha256", "uploaded_at")

@admin.register(MediaMetadata)
class MediaMetadataAdmin(admin.ModelAdmin):
    list_display = ("source_file", "duration_s", "width", "height", "fps", "video_codec", "audio_codec")
    search_fields = ("source_file__original_name",)

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("id", "type", "status", "progress", "stage", "owner", "attempts", "created_at")
    list_filter = ("type", "status", "stage")
    search_fields = ("id", "owner__username", "source_file__original_name", "celery_task_id")
    readonly_fields = ("id", "created_at", "started_at", "finished_at")

@admin.register(OutputFile)
class OutputFileAdmin(admin.ModelAdmin):
    list_display = ("id", "file_name", "format", "job", "size_bytes", "created_at")
    search_fields = ("file_name", "job__id")

@admin.register(OperationHistory)
class OperationHistoryAdmin(admin.ModelAdmin):
    list_display = ("id", "action", "user", "job", "source_file", "created_at")
    list_filter = ("action",)
    search_fields = ("user__username", "job__id")
    readonly_fields = ("id", "created_at")
