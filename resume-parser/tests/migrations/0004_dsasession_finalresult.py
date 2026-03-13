# Generated migration for DSA integration

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('tests', '0003_add_proctoring_fields'),
    ]

    operations = [
        migrations.CreateModel(
            name='DSASession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('invite_token', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('sent', 'Sent'), ('active', 'Active'), ('completed', 'Completed'), ('expired', 'Expired')], default='pending', max_length=20)),
                ('sent_at', models.DateTimeField(blank=True, null=True)),
                ('started_at', models.DateTimeField(blank=True, null=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('problems_attempted', models.IntegerField(default=0)),
                ('problems_solved', models.IntegerField(default=0)),
                ('total_dsa_score', models.FloatField(default=0)),
                ('head_turn_violations', models.IntegerField(default=0)),
                ('multiple_face_violations', models.IntegerField(default=0)),
                ('proctoring_terminated', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('test', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='dsa_session', to='tests.test')),
            ],
        ),
        migrations.CreateModel(
            name='FinalResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('aptitude_score', models.FloatField(default=0)),
                ('technical_score', models.FloatField(default=0)),
                ('test_total', models.FloatField(default=0)),
                ('dsa_score', models.FloatField(default=0)),
                ('problems_solved', models.IntegerField(default=0)),
                ('overall_score', models.FloatField(default=0)),
                ('status', models.CharField(default='pending', max_length=20)),
                ('recommendation', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('dsa_session', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='tests.dsasession')),
                ('test', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='final_result', to='tests.test')),
            ],
        ),
    ]
