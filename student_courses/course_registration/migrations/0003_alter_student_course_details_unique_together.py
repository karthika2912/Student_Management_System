# Generated by Django 4.2 on 2023-04-17 06:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('course_registration', '0002_alter_student_course_details_course_name'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='student_course_details',
            unique_together={('student_roll', 'course_name')},
        ),
    ]