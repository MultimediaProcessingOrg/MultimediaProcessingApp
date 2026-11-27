from __future__ import annotations

import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

from .choices import (
    HistoryAction,
    JobStage,
    JobStatus,
    JobType,
    SourceFileStatus,
    UserRole,
)

class User(AbstractUser):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.CharField(
        max_length=16,
        choices=UserRole.choices,
        default=UserRole.USER,
        db_index=True,
    )

    class Meta:
        ordering = ("-date_joined",)

    def save(self, *args, **kwargs):
        if self.role == UserRole.ADMIN:
            self.is_staff = True
        super().save(*args, **kwargs)

    @property
    def is_admin_role(self) -> bool:
        return self.role == UserRole.ADMIN or self.is_superuser

    def __str__(self) -> str:
        return f"{self.username} ({self.role})"

class SourceFile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="source_files"
    )
    original_name = models.CharField(max_length=255)
    storage_path = models.CharField(max_length=512)
    size_bytes = models.BigIntegerField(default=0)
    sha256 = models.CharField(max_length=64, blank=True, default="", db_index=True)
    mime_type = models.CharField(max_length=100, blank=True, default="")
    status = models.CharField(
        max_length=16,
        choices=SourceFileStatus.choices,
        default=SourceFileStatus.UPLOADED,
        db_index=True,
    )
    is_deleted = models.BooleanField(default=False, db_index=True)
    uploaded_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        ordering = ("-uploaded_at",)
        indexes = [
            models.Index(fields=("owner", "is_deleted")),
        ]

    def __str__(self) -> str:
        return f"{self.original_name} ({self.id})"

class MediaMetadata(models.Model):
    source_file = models.OneToOneField(
        SourceFile,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="metadata",
    )
    duration_s = models.FloatField(null=True, blank=True)
    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    fps = models.FloatField(null=True, blank=True)
    video_codec = models.CharField(max_length=64, null=True, blank=True)
    audio_codec = models.CharField(max_length=64, null=True, blank=True)
    video_profile = models.CharField(max_length=64, null=True, blank=True)
    audio_profile = models.CharField(max_length=64, null=True, blank=True)
    container = models.CharField(max_length=64, null=True, blank=True)
    audio_channels = models.IntegerField(null=True, blank=True)
    sample_rate_hz = models.IntegerField(null=True, blank=True)
    bitrate_bps = models.BigIntegerField(null=True, blank=True)
    stream_count = models.IntegerField(null=True, blank=True)
    streams_raw = models.JSONField(default=dict, blank=True)
    probed_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name_plural = "Media metadata"

    def __str__(self) -> str:
        return f"Metadata for {self.source_file_id}"

class Job(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="jobs")
    source_file = models.ForeignKey(
        SourceFile, on_delete=models.CASCADE, related_name="jobs"
    )
    type = models.CharField(max_length=20, choices=JobType.choices, db_index=True)
    status = models.CharField(
        max_length=16,
        choices=JobStatus.choices,
        default=JobStatus.PENDING,
        db_index=True,
    )
    progress = models.PositiveSmallIntegerField(default=0)
    stage = models.CharField(
        max_length=16, choices=JobStage.choices, default=JobStage.QUEUED
    )
    params = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(null=True, blank=True)
    celery_task_id = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    internal_job_id = models.CharField(max_length=255, null=True, blank=True)
    cancel_requested = models.BooleanField(default=False)
    attempts = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=("owner", "status")),
            models.Index(fields=("source_file", "status")),
        ]

    def __str__(self) -> str:
        return f"{self.type} {self.id} [{self.status}]"

    @property
    def is_active(self) -> bool:
        from .choices import ACTIVE_JOB_STATUSES

        return self.status in ACTIVE_JOB_STATUSES

    @property
    def is_terminal(self) -> bool:
        from .choices import TERMINAL_JOB_STATUSES

        return self.status in TERMINAL_JOB_STATUSES

class OutputFile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="output_files")
    storage_path = models.CharField(max_length=512)
    file_name = models.CharField(max_length=255)
    format = models.CharField(max_length=20, blank=True, default="")
    size_bytes = models.BigIntegerField(null=True, blank=True)
    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    duration_s = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ("created_at",)

    def __str__(self) -> str:
        return f"{self.file_name} ({self.job_id})"

class OperationHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="operation_history"
    )
    action = models.CharField(max_length=32, choices=HistoryAction.choices, db_index=True)
    job = models.ForeignKey(
        Job, on_delete=models.SET_NULL, null=True, blank=True, related_name="history"
    )
    source_file = models.ForeignKey(
        SourceFile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="history",
    )
    details = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name_plural = "Operation history"
        indexes = [
            models.Index(fields=("user", "created_at")),
        ]

    def __str__(self) -> str:
        return f"{self.action} by {self.user_id} @ {self.created_at}"
