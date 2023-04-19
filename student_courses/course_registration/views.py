from django.shortcuts import render,redirect
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import StudentSerializer,Department_DetailsSerializer,Student_Course_DetailsSerializer
from .models import Student_Details,Department_Details,Department_wise_Course_Details,Student_Course_Details,Class_Student,Class_Details,Time_Table_Model
from django.http import HttpRequest

from django.shortcuts import get_object_or_404


import requests

class_section=""
@api_view(['GET'])
def apiOverview(request):
    api_urls={
        'List':'/student-list/',
        'Detail View':'/student-detail/<str:pk>',
        'Create':'/create/',
        'Update':'/update/<str:pk>',
        'Delete':'/delete/<str:pk>/',
    }
    return Response(api_urls)

@api_view(['GET'])
def studentList(request):
    tasks=Student_Details.objects.all()
    serializer=StudentSerializer(tasks,many=True)
    return Response(serializer.data)

def home(request):
    response=requests.get('http://127.0.0.1:8001/api/student-list').json()
    print(response)
    for res in response:
        k=res['department']
        if(k==1):
            res['department']="CSE"
        elif(k==2):
            res['department']="IT"  
        else:
            res['department']='ECE'
    return render(request,'home.html',{'response':response})

@api_view(['GET'])
def studentDetail(request,pk):
    tasks=Student_Details.objects.get(id=pk)
    serializer=StudentSerializer(tasks,many=False)
    return Response(serializer.data)

@api_view(['POST'])
def Create(request):
    if request.method=='POST':
        roll=request.POST.get("roll")
        name=request.POST.get("name")
        department=request.POST.get("department")

        data={
            'roll':roll,
            'name':name,
            'department':department
        }

        serializer=StudentSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
    
        return redirect('/api/home')
@api_view(['POST'])
def Update(request,pk):
    task=Student_Details.objects.get(id=pk)
    serializer=StudentSerializer(instance=task,data=request.data)
    if serializer.is_valid():
        serializer.save()
    
    return redirect('/api/home')

@api_view(['DELETE'])
def Delete(request,pk):
    task=Student_Details.objects.get(id=pk)
    task.delete()
    return redirect('/api/home')

def add_student(request):
    return render(request,"add_student.html")

def update_student(request,roll):
    std=Student_Details.objects.get(pk=roll)
    print(std.roll)
    print(std.name)
    return render(request,"update.html",{"std":std})

def home_course(request):
    response=requests.get('http://127.0.0.1:8001/api/student-list').json()
    return render(request,'home_course.html',{'response':response})

def add_course(request,roll):
    res=Student_Details.objects.get(pk=roll)
    d1=res.department
    d2=Department_Details.objects.get(pk=d1.id)
    dept_name=d2.department_name
    dep=Department_wise_Course_Details.objects.filter(department_name_id=d1)
    course_list=[]
    for d in dep:
        course_list.append(d.course_title)
    return render(request,"add_course.html",{"res":res,"c1":course_list[0],"c2":course_list[1],"dept_name":dept_name})

@api_view(['POST'])
def courseCreate(request):
    print("Entered courseCreate")
    if request.method=='POST':
        roll=request.POST.get("roll")
        print(roll)
        name=request.POST.get("name")
        department=request.POST.get("department")
        course=request.POST.get("course")
        res=Student_Details.objects.filter(roll=roll)
        student_roll_id=1
        for r in res:
            student_roll_id=r.id
            break

        
        course_details=Department_wise_Course_Details.objects.all()
        course_name_id=0
        print(course)
        for c in course_details:
            if(c.course_title==course):
                course_name_id=c.id
                break
        course_instance=Department_wise_Course_Details.objects.get(pk=course_name_id)

        check_obj=Student_Course_Details.objects.filter(course_name_id=course_instance.id,student_roll_id=student_roll_id)
        if(len(check_obj)!=0):
            return redirect('/api/home_course')
        else:

            data={
                'course_name_id':course_instance.id,
                'student_roll_id':student_roll_id

            }
            ob1=Student_Course_Details(course_name_id=course_instance.id,student_roll_id=student_roll_id)
            ob1.save()
            return redirect('/api/home_course')
    
def view_courses(request,roll):
    obj=Student_Course_Details.objects.filter(student_roll_id=roll)
    print(obj)
    temp_list=[]
    
    for ob in obj:
        student_list=[]
        s1=Student_Details.objects.get(pk=roll)
        print(s1.name)
        c1=Department_wise_Course_Details.objects.get(pk=ob.course_name_id)
        print(c1)
        student_list.append(s1.id)
        student_list.append(c1.course_title)
        student_list.append(c1.id)

        
        temp_list.append(student_list)

    
    print(temp_list)
    return render(request,"course_view.html",{'temp_list':temp_list})

def delete_course(request,roll):
    obj=Student_Course_Details.objects.filter(student_roll_id=roll)
    obj.delete()
    return redirect("/api/home_course")
def delete_course_wise(request,roll,course_id):
    print(roll)
    print(course_id)
    obj=Student_Course_Details.objects.filter(student_roll_id=roll,course_name_id=course_id)
    obj.delete()
    return redirect("/api/home_course")

def home_class(request):
    response=requests.get('http://127.0.0.1:8001/api/student-list').json()
    print(response)
    for res in response:
        k=res['department']
        if(k==1):
            res['department']="CSE"
        elif(k==2):
            res['department']="IT"  
        else:
            res['department']='ECE'
    return render(request,'home_class.html',{'response':response})

def add_class_student(request,roll):
    student_object = Student_Details.objects.get(pk=roll)
    department=student_object.department
    department_name = Department_Details.objects.get(pk=department.id)
    return render(request,"add_class.html",{'response':student_object,'department':department_name.department_name})

@api_view(['POST'])
def Class_StudentCreate(request):
    print("entered class student")
    if request.method=='POST':
        print("entered Post")
        student_roll=request.POST.get('roll')
        student_class=request.POST.get('student_class')
        print(student_roll)
        print(student_class)
        student_object=Student_Details.objects.filter(roll=student_roll)
        check_class=Class_Student.objects.filter(class_name=student_class,student_id=student_object[0])
        if len(check_class)!=0:
            return redirect('/api/home_class')
        else:
            class_student_object=Class_Student(class_name=student_class,student_id=student_object[0])
            class_student_object.save()
        
            return redirect('/api/home_class')
        
    
def view_class_students(request):
    class_A=Class_Student.objects.filter(class_name="A")
    class_B=Class_Student.objects.filter(class_name="B")
    class_C=Class_Student.objects.filter(class_name="C")

    class_a=[]
    class_b=[]
    class_c=[]

    for obj in class_A:
        temp_list=[]
        s1=obj.student_id
        sub=Student_Details.objects.get(pk=s1.id)
        Dep=Department_Details.objects.get(pk=sub.department_id)
        temp_list.append(sub.roll)
        temp_list.append(sub.name)
        temp_list.append(Dep.department_name)
        class_a.append(temp_list)

    for obj in class_B:
        temp_list=[]
        s1=obj.student_id
        sub=Student_Details.objects.get(pk=s1.id)
        Dep=Department_Details.objects.get(pk=sub.department_id)
        temp_list.append(sub.roll)
        temp_list.append(sub.name)
        temp_list.append(Dep.department_name)
        class_b.append(temp_list)

    for obj in class_C:
        temp_list=[]
        s1=obj.student_id
        sub=Student_Details.objects.get(pk=s1.id)
        Dep=Department_Details.objects.get(pk=sub.department_id)
        dep_name=Dep.department_name
        temp_list.append(sub.roll)
        temp_list.append(sub.name)
        
        temp_list.append(dep_name)

        class_c.append(temp_list)

    return render(request,"view_class_students.html",{'class_a':class_a,'class_b':class_b,'class_c':class_c})

def delete_class(request,roll):
    print(roll)
    stu = Student_Details.objects.get(pk=roll)
    class_obj=Class_Student.objects.filter(student_id=stu)
    class_obj.delete()
    return redirect('/api/home_class/')

def TimeTable(request):
    dep=Department_wise_Course_Details.objects.all()
    courses=[]
    for d in dep:
        courses.append(d.course_title)
    
    return render(request, "timetable.html",{'courses':courses})

def view_time_table(request,class_title):
    class_object=Class_Details.objects.get(class_name=class_title)

    t1=Time_Table_Model.objects.get(class_id=class_object)
    
   
    
    f=Department_wise_Course_Details.objects.get(pk=t1.first_hour_course.id)
    s=Department_wise_Course_Details.objects.get(pk=t1.second_hour_course.id)
    t=Department_wise_Course_Details.objects.get(pk=t1.third_hour_course.id)
    return render(request,"view_time_table.html",{'class_name':class_title,'first_hour':f.course_title,'second_hour':s.course_title,'third_hour':t.course_title})

@api_view(['POST'])
def createTimeTable(request):
    if request.method=='POST':
        
        class_title=request.POST.get("class_name")
        
        first_hour=request.POST.get("first_hour")
        second_hour=request.POST.get("second_hour")
        third_hour=request.POST.get("third_hour")
       
        class_object=Class_Details.objects.get(class_name=class_title)
        f=Department_wise_Course_Details.objects.get(course_title=first_hour)
        s=Department_wise_Course_Details.objects.get(course_title=second_hour)
        t=Department_wise_Course_Details.objects.get(course_title=third_hour)
        print(class_object.id)
        print(f.id)
        print(s.id)
        print(t.id)
        
        
        t1=Time_Table_Model.objects.get(class_id=class_object)

        t1.first_hour_course=f
        t1.second_hour_course=s
        t1.third_hour_course=t
        t1.save()
        print(t1)

        url_s='/api/view_time_table/'+class_title
        return redirect(url_s)

def set_class(request):
    if request.method=='POST':
        class_section=request.POST.get('class_name')
        print(class_section)
        classes=['A','B','C']
        class_titles=[]
        for i in classes:
            if i!=class_section:
                class_titles.append(i)
        print(class_titles)
        
        f_l=[]
        s_l=[]
        t_l=[]
        dep=Department_wise_Course_Details.objects.all()
        for d in dep:
            f_l.append(d.course_title)
            s_l.append(d.course_title)
            t_l.append(d.course_title)
        print(f_l)
        print(s_l)
        print(t_l)
        
        for cls in class_titles:
            c1=Class_Details.objects.get(class_name=cls)
            t1=Time_Table_Model.objects.get(class_id=c1)
            f_h=t1.first_hour_course.course_title
            s_h=t1.second_hour_course.course_title
            t_h=t1.third_hour_course.course_title
            print(f_h)
            print(s_h)
            print(t_h)
            f_l.remove(f_h)
            s_l.remove(s_h)
            t_l.remove(t_h)

        

        return render(request,"timetable.html",{'class_section':class_section,'f_l':f_l,'s_l':s_l,'t_l':t_l})
    
def choose_class(request):
    return render(request,"choose_class.html")

def view_all_time_tables(request):
    
    class_a=[]
    class_b=[]
    class_c=[]
    
    c1=Class_Details.objects.get(class_name='A')
    t1=Time_Table_Model.objects.get(class_id=c1)
    f_h=t1.first_hour_course.course_title
    s_h=t1.second_hour_course.course_title
    t_h=t1.third_hour_course.course_title

    class_a.append(f_h)
    class_a.append(s_h)
    class_a.append(t_h)

    c2=Class_Details.objects.get(class_name='B')
    t2=Time_Table_Model.objects.get(class_id=c2)
    f_h2=t2.first_hour_course.course_title
    s_h2=t2.second_hour_course.course_title
    t_h2=t2.third_hour_course.course_title
    
    class_b.append(f_h2)
    class_b.append(s_h2)
    class_b.append(t_h2)

    c3=Class_Details.objects.get(class_name='C')
    t3=Time_Table_Model.objects.get(class_id=c3)
    f_h3=t3.first_hour_course.course_title
    s_h3=t3.second_hour_course.course_title
    t_h3=t3.third_hour_course.course_title
    
    class_c.append(f_h3)
    class_c.append(s_h3)
    class_c.append(t_h3)

    return render(request,"view_all_timetables.html",{'class_a':class_a,'class_b':class_b,'class_c':class_c})

def add_home_class(request):
    classes=Class_Details.objects.all()
    return render(request,"display_classes.html",{'classes':classes})

def add_class(request):
    return render(request,"new_class.html")

def classObjectCreate(request):
    if request.method == 'POST':
        class_name = request.POST.get('class_name')
        check_object = Class_Details.objects.filter(class_name=class_name)
        if len(check_object)==0:
            class_object = Class_Details(class_name=class_name)
            class_object.save()
            return redirect('/api/add_home_class')
        else:
            return redirect('/api/add_home_class')


    










    




    
    





