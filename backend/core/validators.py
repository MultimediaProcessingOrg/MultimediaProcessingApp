from __future__ import annotations

from rest_framework import serializers

from .choices import JobType

TARGET_CONTAINERS = ("mp4", "mkv", "webm", "mov", "avi")
VIDEO_CODECS = ("h264", "h265", "vp9")
AUDIO_CODECS_TRANSCODE = ("aac", "opus", "mp2", "copy")
AUDIO_CODECS_AUDIO = ("aac", "mp3", "opus", "flac")
AUDIO_OUTPUT_FORMATS = ("mp3", "aac", "wav", "flac", "ogg", "opus")
RESOLUTIONS = ("240p", "360p", "480p", "720p", "1080p", "original")
PREVIEW_RESOLUTIONS = ("360p", "480p")
FPS_VALUES = (24, 25, 30, 60, "original")
PRESETS = (
    "ultrafast",
    "superfast",
    "veryfast",
    "faster",
    "fast",
    "medium",
    "slow",
    "slower",
    "veryslow",
)
SAMPLE_RATES = (22050, 44100, 48000)
CHANNELS = (1, 2)
IMAGE_FORMATS = ("jpg", "png", "webp")

def _int_range(name, min_value, max_value, required=False, default=None):
    return serializers.IntegerField(
        min_value=min_value,
        max_value=max_value,
        required=required,
        default=default,
    )

def _float_range(name, min_value, max_value, required=False, default=None):
    return serializers.FloatField(
        min_value=min_value,
        max_value=max_value,
        required=required,
        default=default,
    )

def _choice(name, choices, required=False, default=None):
    return serializers.ChoiceField(
        choices=choices, required=required, default=default
    )

class _BaseParamsSerializer(serializers.Serializer):

    def to_internal_value(self, data):
        if not isinstance(data, dict):
            raise serializers.ValidationError("params musi być obiektem JSON.")
        unknown = set(data.keys()) - set(self.fields.keys())
        if unknown:
            raise serializers.ValidationError(
                {key: ["Nieznany parametr."] for key in sorted(unknown)}
            )
        return super().to_internal_value(data)

class TranscodeParamsSerializer(_BaseParamsSerializer):
    target_container = _choice("target_container", TARGET_CONTAINERS, default="mp4")
    video_codec = _choice("video_codec", VIDEO_CODECS, default="h264")
    audio_codec = _choice("audio_codec", AUDIO_CODECS_TRANSCODE, default="aac")
    resolution = _choice("resolution", RESOLUTIONS, default="original")
    fps = serializers.ChoiceField(choices=FPS_VALUES, required=False, default="original")
    video_bitrate_kbps = _int_range("video_bitrate_kbps", 100, 100000, required=False, default=None)
    crf = _int_range("crf", 18, 40, required=False, default=23)
    preset = _choice("preset", PRESETS, default="medium")
    audio_bitrate_kbps = _int_range("audio_bitrate_kbps", 32, 512, required=False, default=None)
    sample_rate_hz = _choice("sample_rate_hz", SAMPLE_RATES, required=False, default=None)
    channels = _choice("channels", CHANNELS, required=False, default=None)
    start_time_s = _float_range("start_time_s", 0, 86400, required=False, default=None)
    duration_s = _float_range("duration_s", 0.1, 86400, required=False, default=None)

class ThumbnailParamsSerializer(_BaseParamsSerializer):
    time_s = _float_range("time_s", 0, 86400, required=False, default=1.0)
    width = _int_range("width", 64, 1920, required=False, default=640)
    height = _int_range("height", 64, 1920, required=False, default=None)
    format = _choice("format", IMAGE_FORMATS, default="jpg")

class GifParamsSerializer(_BaseParamsSerializer):
    start_time_s = _float_range("start_time_s", 0, 86400, required=False, default=0.0)
    duration_s = _float_range("duration_s", 0.1, 30, required=False, default=10.0)
    fps = _int_range("fps", 5, 25, required=False, default=15)
    width = _int_range("width", 128, 640, required=False, default=480)

class PreviewParamsSerializer(_BaseParamsSerializer):
    preview_length_s = _float_range("preview_length_s", 1, 60, required=False, default=30.0)
    resolution = _choice("resolution", PREVIEW_RESOLUTIONS, default="360p")
    audio = serializers.BooleanField(required=False, default=True)

class AudioProcessParamsSerializer(_BaseParamsSerializer):
    audio_codec = _choice("audio_codec", AUDIO_CODECS_AUDIO, default="aac")
    output_format = _choice("output_format", AUDIO_OUTPUT_FORMATS, required=False, default=None)
    audio_bitrate_kbps = _int_range("audio_bitrate_kbps", 32, 512, required=False, default=192)
    sample_rate_hz = _choice("sample_rate_hz", SAMPLE_RATES, required=False, default=48000)
    channels = _choice("channels", CHANNELS, required=False, default=None)
    loudnorm = serializers.BooleanField(required=False, default=False)
    volume = _float_range("volume", -60, 60, required=False, default=None)
    denoise = serializers.BooleanField(required=False, default=False)
    start_time_s = _float_range("start_time_s", 0, 86400, required=False, default=None)
    duration_s = _float_range("duration_s", 0.1, 86400, required=False, default=None)

class InspectParamsSerializer(_BaseParamsSerializer):

PARAMS_SERIALIZERS = {
    JobType.TRANSCODE: TranscodeParamsSerializer,
    JobType.THUMBNAIL: ThumbnailParamsSerializer,
    JobType.GIF: GifParamsSerializer,
    JobType.PREVIEW: PreviewParamsSerializer,
    JobType.AUDIO_PROCESS: AudioProcessParamsSerializer,
    JobType.INSPECT: InspectParamsSerializer,
}

def validate_job_params(job_type: str, params) -> dict:
    serializer_cls = PARAMS_SERIALIZERS.get(job_type)
    if serializer_cls is None:
        raise serializers.ValidationError({"type": ["Nieznany typ zadania."]})
    if params is None:
        params = {}
    serializer = serializer_cls(data=params)
    serializer.is_valid(raise_exception=True)
    return dict(serializer.validated_data)
