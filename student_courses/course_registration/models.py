from django.db import models
from django.contrib.auth.models import User

class Department_Details(models.Model):
    department_name=models.CharField(max_length=20)

class Student_Details(models.Model):
    roll=models.CharField(max_length=20)
    firstname=models.CharField(max_length=100,default="fn")
    lastname=models.CharField(max_length=100,default="ln")
    department=models.ForeignKey(Department_Details,on_delete=models.CASCADE)
    dob=models.CharField(max_length=10,default="29-12-2001")
    gender=models.CharField(max_length=10,default="F")


class Department_wise_Course_Details(models.Model):
    course_title=models.CharField(max_length=50)
    department_name=models.ForeignKey(Department_Details,on_delete=models.CASCADE)
    
    
class Student_Course_Details(models.Model):
    student_roll=models.ForeignKey(Student_Details,on_delete=models.CASCADE,related_name='course_details_roll')
    course_name=models.ForeignKey(Department_wise_Course_Details,on_delete=models.CASCADE,related_name='course_details_name')
    class Meta:
        unique_together = ('student_roll', 'course_name')

class Class_Student(models.Model):
    class_name=models.CharField(max_length=10)
    student_id=models.ForeignKey(Student_Details,on_delete=models.CASCADE)
    class Meta:
        unique_together=('class_name','student_id')

class Class_Details(models.Model):
    class_name=models.CharField(max_length=10)

class Time_Table_Model(models.Model):
    class_id=models.ForeignKey(Class_Details,on_delete=models.CASCADE)
    first_hour_course=models.ForeignKey(Department_wise_Course_Details,on_delete=models.CASCADE,related_name="first_hour_timetables")
    second_hour_course=models.ForeignKey(Department_wise_Course_Details,on_delete=models.CASCADE,related_name="second_hour_timetables")
    third_hour_course=models.ForeignKey(Department_wise_Course_Details,on_delete=models.CASCADE,related_name="third_hour_timetables")

    class Meta:
        unique_together=('class_id',)

class Resumes(models.Model):
    student_id = models.ForeignKey(Student_Details,on_delete=models.CASCADE)
    resume = models.FileField(null = True)
    
class Account(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    auth_token = models.CharField(max_length=100)
    is_verified = models.BooleanField(default = False)
    created_at = models.DateTimeField(auto_now_add = True)
    
    def __str__(self):
        return self.user.username

class Attendance(models.Model):
    student=models.ForeignKey(Student_Details,on_delete=models.CASCADE)
    date=models.CharField(max_length=10)
    first_hour=models.CharField(max_length=1)
    second_hour=models.CharField(max_length=1)
    third_hour=models.CharField(max_length=1)
    fourth_hour=models.CharField(max_length=1)
    fifth_hour=models.CharField(max_length=1)
    present=models.IntegerField()
    absent=models.IntegerField()

class Marks(models.Model):
    sessional=models.IntegerField()
    external=models.IntegerField()
    student=models.ForeignKey(Student_Details,on_delete=models.CASCADE)
    course=models.ForeignKey(Department_wise_Course_Details,on_delete=models.CASCADE)