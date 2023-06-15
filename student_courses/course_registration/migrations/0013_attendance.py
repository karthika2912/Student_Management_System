# Generated by Django 4.2 on 2023-06-09 03:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('course_registration', '0012_remove_student_details_name_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Attendance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.CharField(max_length=10)),
                ('first_hour', models.CharField(max_length=1)),
                ('second_hour', models.CharField(max_length=1)),
                ('third_hour', models.CharField(max_length=1)),
                ('fourth_hour', models.CharField(max_length=1)),
                ('fifth_hour', models.CharField(max_length=1)),
                ('present', models.IntegerField()),
                ('absent', models.IntegerField()),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='course_registration.student_details')),
            ],
        ),
    ]