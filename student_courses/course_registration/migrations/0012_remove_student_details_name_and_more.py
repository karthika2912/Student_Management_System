# Generated by Django 4.2 on 2023-06-08 04:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course_registration', '0011_student_details_dob_student_details_gender'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='student_details',
            name='name',
        ),
        migrations.AddField(
            model_name='student_details',
            name='firstname',
            field=models.CharField(default='fn', max_length=100),
        ),
        migrations.AddField(
            model_name='student_details',
            name='lastname',
            field=models.CharField(default='ln', max_length=100),
        ),
    ]
