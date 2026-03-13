# Generated migration for tab switch detection

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tests', '0004_dsasession_finalresult'),
    ]

    operations = [
        migrations.AddField(
            model_name='test',
            name='tab_switch_violations',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='dsasession',
            name='tab_switch_violations',
            field=models.IntegerField(default=0),
        ),
    ]
