
import django.contrib.auth.models
import django.contrib.auth.validators
import django.db.models.deletion
import django.utils.timezone
import uuid
from django.conf import settings
from django.db import migrations, models

class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='SourceFile',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('original_name', models.CharField(max_length=255)),
                ('storage_path', models.CharField(max_length=512)),
                ('size_bytes', models.BigIntegerField(default=0)),
                ('sha256', models.CharField(blank=True, db_index=True, default='', max_length=64)),
                ('mime_type', models.CharField(blank=True, default='', max_length=100)),
                ('status', models.CharField(choices=[('UPLOADED', 'Wgrany'), ('INSPECTING', 'W trakcie inspekcji'), ('READY', 'Gotowy'), ('REJECTED', 'Odrzucony')], db_index=True, default='UPLOADED', max_length=16)),
                ('is_deleted', models.BooleanField(db_index=True, default=False)),
                ('uploaded_at', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
            ],
            options={
                'ordering': ('-uploaded_at',),
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('role', models.CharField(choices=[('ADMIN', 'Administrator'), ('USER', 'Użytkownik')], db_index=True, default='USER', max_length=16)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'ordering': ('-date_joined',),
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='MediaMetadata',
            fields=[
                ('source_file', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='metadata', serialize=False, to='core.sourcefile')),
                ('duration_s', models.FloatField(blank=True, null=True)),
                ('width', models.IntegerField(blank=True, null=True)),
                ('height', models.IntegerField(blank=True, null=True)),
                ('fps', models.FloatField(blank=True, null=True)),
                ('video_codec', models.CharField(blank=True, max_length=64, null=True)),
                ('audio_codec', models.CharField(blank=True, max_length=64, null=True)),
                ('video_profile', models.CharField(blank=True, max_length=64, null=True)),
                ('audio_profile', models.CharField(blank=True, max_length=64, null=True)),
                ('container', models.CharField(blank=True, max_length=64, null=True)),
                ('audio_channels', models.IntegerField(blank=True, null=True)),
                ('sample_rate_hz', models.IntegerField(blank=True, null=True)),
                ('bitrate_bps', models.BigIntegerField(blank=True, null=True)),
                ('stream_count', models.IntegerField(blank=True, null=True)),
                ('streams_raw', models.JSONField(blank=True, default=dict)),
                ('probed_at', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'verbose_name_plural': 'Media metadata',
            },
        ),
        migrations.AddField(
            model_name='sourcefile',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='source_files', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('type', models.CharField(choices=[('TRANSCODE', 'Transkodowanie'), ('THUMBNAIL', 'Miniatura'), ('GIF', 'GIF'), ('PREVIEW', 'Podgląd'), ('AUDIO_PROCESS', 'Przetwarzanie audio'), ('INSPECT', 'Inspekcja')], db_index=True, max_length=20)),
                ('status', models.CharField(choices=[('PENDING', 'Oczekuje'), ('STARTED', 'Rozpoczęty'), ('PROGRESS', 'W toku'), ('SUCCESS', 'Sukces'), ('FAILURE', 'Błąd'), ('REVOKED', 'Anulowany')], db_index=True, default='PENDING', max_length=16)),
                ('progress', models.PositiveSmallIntegerField(default=0)),
                ('stage', models.CharField(choices=[('QUEUED', 'W kolejce'), ('VALIDATING', 'Walidacja'), ('PROBING', 'Sondowanie'), ('ENCODING', 'Kodowanie'), ('FINALIZING', 'Finalizacja'), ('DONE', 'Zakończone')], default='QUEUED', max_length=16)),
                ('params', models.JSONField(blank=True, default=dict)),
                ('error_message', models.TextField(blank=True, null=True)),
                ('celery_task_id', models.CharField(blank=True, db_index=True, max_length=255, null=True)),
                ('internal_job_id', models.CharField(blank=True, max_length=255, null=True)),
                ('cancel_requested', models.BooleanField(default=False)),
                ('attempts', models.PositiveSmallIntegerField(default=0)),
                ('created_at', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('started_at', models.DateTimeField(blank=True, null=True)),
                ('finished_at', models.DateTimeField(blank=True, null=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='jobs', to=settings.AUTH_USER_MODEL)),
                ('source_file', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='jobs', to='core.sourcefile')),
            ],
            options={
                'ordering': ('-created_at',),
            },
        ),
        migrations.CreateModel(
            name='OperationHistory',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('action', models.CharField(choices=[('FILE_UPLOADED', 'Plik wgrany'), ('FILE_REJECTED', 'Plik odrzucony'), ('FILE_DELETED', 'Plik usunięty'), ('JOB_CREATED', 'Zadanie utworzone'), ('JOB_SUCCESS', 'Zadanie zakończone sukcesem'), ('JOB_FAILURE', 'Zadanie zakończone błędem'), ('JOB_CANCELLED', 'Zadanie anulowane'), ('JOB_RETRIED', 'Zadanie ponowione')], db_index=True, max_length=32)),
                ('details', models.JSONField(blank=True, default=dict)),
                ('created_at', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('job', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='history', to='core.job')),
                ('source_file', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='history', to='core.sourcefile')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='operation_history', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Operation history',
                'ordering': ('-created_at',),
            },
        ),
        migrations.CreateModel(
            name='OutputFile',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('storage_path', models.CharField(max_length=512)),
                ('file_name', models.CharField(max_length=255)),
                ('format', models.CharField(blank=True, default='', max_length=20)),
                ('size_bytes', models.BigIntegerField(blank=True, null=True)),
                ('width', models.IntegerField(blank=True, null=True)),
                ('height', models.IntegerField(blank=True, null=True)),
                ('duration_s', models.FloatField(blank=True, null=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='output_files', to='core.job')),
            ],
            options={
                'ordering': ('created_at',),
            },
        ),
        migrations.AddIndex(
            model_name='sourcefile',
            index=models.Index(fields=['owner', 'is_deleted'], name='core_source_owner_i_ac1c75_idx'),
        ),
        migrations.AddIndex(
            model_name='job',
            index=models.Index(fields=['owner', 'status'], name='core_job_owner_i_75dce8_idx'),
        ),
        migrations.AddIndex(
            model_name='job',
            index=models.Index(fields=['source_file', 'status'], name='core_job_source__0a8300_idx'),
        ),
        migrations.AddIndex(
            model_name='operationhistory',
            index=models.Index(fields=['user', 'created_at'], name='core_operat_user_id_8562e1_idx'),
        ),
    ]
