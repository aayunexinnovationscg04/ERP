"""Rename Driver -> Pilot, DriverAttendance -> PilotAttendance, and the FK
fields that reference them, in place (RenameModel/RenameField preserve the
underlying table/column + all existing rows; this must never be regenerated
via makemigrations autodetection, which would DROP + recreate and lose data).

The two AlterFields only update `related_name` (a Python/ORM-level attribute,
not a DB column) so Django's migration state matches models.py; they run no
actual schema change.
"""

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fleet', '0004_driver_monthly_salary_driverattendance'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameModel(old_name='Driver', new_name='Pilot'),
        migrations.RenameModel(old_name='DriverAttendance', new_name='PilotAttendance'),
        migrations.RenameField(model_name='pilotattendance', old_name='driver', new_name='pilot'),
        migrations.RenameField(model_name='vehicle', old_name='active_driver', new_name='active_pilot'),
        migrations.RenameField(model_name='trip', old_name='driver', new_name='pilot'),
        migrations.AlterField(
            model_name='pilot',
            name='company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pilots', to='core.company'),
        ),
        migrations.AlterField(
            model_name='pilot',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='pilot_profiles', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterModelOptions(
            name='pilotattendance',
            options={'ordering': ['-date'], 'verbose_name_plural': 'pilot attendance'},
        ),
        migrations.RemoveConstraint(
            model_name='pilotattendance',
            name='uniq_attendance_per_day',
        ),
        migrations.AddConstraint(
            model_name='pilotattendance',
            constraint=models.UniqueConstraint(fields=('pilot', 'date'), name='uniq_attendance_per_day'),
        ),
    ]
