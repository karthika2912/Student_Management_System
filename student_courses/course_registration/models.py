from django.db import models

class Department_Details(models.Model):
    department_name=models.CharField(max_length=20)

class Student_Details(models.Model):
    roll=models.CharField(max_length=20)
    name=models.CharField(max_length=100)
    department=models.ForeignKey(Department_Details,on_delete=models.CASCADE)


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
    


    

