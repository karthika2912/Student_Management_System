# Generated by Django 4.2 on 2023-04-18 18:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('course_registration', '0005_class_details_timetable'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='TimeTable',
            new_name='Time_Table_Model',
        ),
    ]