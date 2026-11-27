from rest_framework import serializers

from .models import MediaMetadata, OutputFile, SourceFile, User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name", "role")
        read_only_fields = ("id",)

class MediaMetadataSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediaMetadata
        fields = (
            "id",
            "source_file",
            "duration_s",
            "width",
            "height",
            "fps",
            "video_codec",
            "audio_codec",
            "video_bitrate",
            "audio_bitrate",
            "sample_rate",
            "channels",
            "format_name",
            "size_bytes",
            "analyzed_at",
        )
        read_only_fields = fields

class SourceFileSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    metadata = MediaMetadataSerializer(read_only=True)

    class Meta:
        model = SourceFile
        fields = (
            "id",
            "owner",
            "file_name",
            "original_name",
            "file_path",
            "size_bytes",
            "sha256",
            "mime_type",
            "status",
            "created_at",
            "updated_at",
            "metadata",
        )
        read_only_fields = (
            "id",
            "owner",
            "file_name",
            "file_path",
            "size_bytes",
            "sha256",
            "mime_type",
            "status",
            "created_at",
            "updated_at",
        )

class OutputFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = OutputFile
        fields = (
            "id",
            "job",
            "file_name",
            "file_path",
            "size_bytes",
            "mime_type",
            "created_at",
        )
        read_only_fields = fields
