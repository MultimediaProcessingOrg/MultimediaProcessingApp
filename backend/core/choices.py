from django.db import models

class UserRole(models.TextChoices):
    ADMIN = "ADMIN", "Administrator"
    USER = "USER", "Użytkownik"

class SourceFileStatus(models.TextChoices):
    UPLOADED = "UPLOADED", "Wgrany"
    INSPECTING = "INSPECTING", "W trakcie inspekcji"
    READY = "READY", "Gotowy"
    REJECTED = "REJECTED", "Odrzucony"

class JobType(models.TextChoices):
    TRANSCODE = "TRANSCODE", "Transkodowanie"
    THUMBNAIL = "THUMBNAIL", "Miniatura"
    GIF = "GIF", "GIF"
    PREVIEW = "PREVIEW", "Podgląd"
    AUDIO_PROCESS = "AUDIO_PROCESS", "Przetwarzanie audio"
    INSPECT = "INSPECT", "Inspekcja"

class JobStatus(models.TextChoices):
    PENDING = "PENDING", "Oczekuje"
    STARTED = "STARTED", "Rozpoczęty"
    PROGRESS = "PROGRESS", "W toku"
    SUCCESS = "SUCCESS", "Sukces"
    FAILURE = "FAILURE", "Błąd"
    REVOKED = "REVOKED", "Anulowany"

class JobStage(models.TextChoices):
    QUEUED = "QUEUED", "W kolejce"
    VALIDATING = "VALIDATING", "Walidacja"
    PROBING = "PROBING", "Sondowanie"
    ENCODING = "ENCODING", "Kodowanie"
    FINALIZING = "FINALIZING", "Finalizacja"
    DONE = "DONE", "Zakończone"

class HistoryAction(models.TextChoices):
    FILE_UPLOADED = "FILE_UPLOADED", "Plik wgrany"
    FILE_REJECTED = "FILE_REJECTED", "Plik odrzucony"
    FILE_DELETED = "FILE_DELETED", "Plik usunięty"
    JOB_CREATED = "JOB_CREATED", "Zadanie utworzone"
    JOB_SUCCESS = "JOB_SUCCESS", "Zadanie zakończone sukcesem"
    JOB_FAILURE = "JOB_FAILURE", "Zadanie zakończone błędem"
    JOB_CANCELLED = "JOB_CANCELLED", "Zadanie anulowane"
    JOB_RETRIED = "JOB_RETRIED", "Zadanie ponowione"

ACTIVE_JOB_STATUSES = (
    JobStatus.PENDING,
    JobStatus.STARTED,
    JobStatus.PROGRESS,
)

TERMINAL_JOB_STATUSES = (
    JobStatus.SUCCESS,
    JobStatus.FAILURE,
    JobStatus.REVOKED,
)

RETRYABLE_JOB_STATUSES = (
    JobStatus.FAILURE,
    JobStatus.REVOKED,
)
