# Generated migration for proctoring fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tests', '0002_test_ranking_result_test_sent_at_alter_test_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='test',
            name='head_turn_violations',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='test',
            name='multiple_face_violations',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='test',
            name='proctoring_terminated',
            field=models.BooleanField(default=False),
        ),
    ]
