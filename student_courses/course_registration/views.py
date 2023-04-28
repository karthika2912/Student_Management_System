from django.shortcuts import render,redirect
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import StudentSerializer,Department_DetailsSerializer,Student_Course_DetailsSerializer
from .models import Account,Student_Details,Department_Details,Department_wise_Course_Details,Student_Course_Details,Class_Student,Class_Details,Time_Table_Model,Resumes
from django.db.models import Count
from django.contrib.auth.models import User,auth
from django.contrib.auth import authenticate, login
from django.contrib import messages
import os
from importlib import import_module
from django.http import HttpRequest,Http404,HttpResponseNotFound,HttpResponse,HttpResponseRedirect
from django.contrib.sessions.backends.db import SessionStore
from io import BytesIO
from django.conf import settings
from django.core.files.storage import default_storage
import uuid
from django.http import FileResponse
import io
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.mail import send_mail
import requests
from datetime import datetime
from django.views import View

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

class HomePageApi(View):
    def get(self,request):
        print("Entered Home")
        response=requests.get('http://127.0.0.1:8001/api/student-list/').json()
        print(response)
        for res in response:
            k=res['department']
            if(k==1):
                res['department']="CSE"
            elif(k==2):
                res['department']="IT"  
            else:
                res['department']='ECE'
       
        if request.user.is_staff:
            return render(request,'home.html',{'response':response})
        else:
            return render(request,'unauthorized_page.html')

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
    
        return redirect('/api/home/')

def Update(request,pk):
    print("Entered Update function")
    if request.method=='POST':
        task=Student_Details.objects.get(pk=pk)
        roll=request.POST.get('roll')
        name=request.POST.get('name')
        department=request.POST.get('department')

        task.roll=roll
        task.name=name

        dept=Department_Details.objects.get(pk=int(department))

        task.department=dept
        task.save()
        print(task.roll,task.name,task.department)
        recently_updated_student = None
        student_id=pk
        if 'recently_updated' in request.session:
            if student_id in request.session['recently_updated']:
                request.session['recently_updated'].remove(student_id)
        
            recently_updated_student = Student_Details.objects.filter(pk__in=request.session['recently_updated'])
            request.session['recently_updated'].insert(0,student_id)

            if len(request.session['recently_updated'])>5:
                request.session['recently_updated'].pop()
        else:
            request.session['recently_updated'] = [student_id]

        request.session.modified = True
        print("recently_updated",recently_updated_student)
        response=requests.get('http://127.0.0.1:8001/api/student-list/').json()
        for res in response:
            k=res['department']
            if(k==1):
                res['department']="CSE"
            elif(k==2):
                res['department']="IT"  
            else:
                res['department']='ECE'
        return render(request,"home.html",{'response':response,'recently_updated_student':recently_updated_student})

        

def Delete(request,pk):
    task=Student_Details.objects.get(id=pk)
    task.delete()
    return redirect('/api/home/')

class AddStudent(View):
    def get(self,request):
        return render(request,"add_student.html")

def UpdateStudent(request,pk):
    std=Student_Details.objects.get(pk=pk)
    return render(request,"update.html",{"std":std})

class CoursesHomePage(View):
    def get(self,request):
        response=requests.get('http://127.0.0.1:8001/api/student-list/').json()
        if not request.user.is_staff:
            print("Authorized")
            return render(request,"home_course.html",{'response':response})
        else:
            return render(request,"unauthorized_page.html")

class AddCourse(View):
    def get(self,request,roll):
        res=Student_Details.objects.get(pk=roll)
        d1=res.department
        d2=Department_Details.objects.get(pk=d1.id)
        dept_name=d2.department_name
        dep=Department_wise_Course_Details.objects.filter(department_name_id=d1)

        return render(request,"add_course.html",{"res":res,"courses":dep,"dept_name":dept_name})


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
            
            ob1=Student_Course_Details(course_name_id=course_instance.id,student_roll_id=student_roll_id)
            ob1.save()
            return redirect('/api/home_course')

class ViewCourses(View):

    def get(self,request,roll):
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

class DeleteCourse(View):
    def get(self,request,roll):
        obj=Student_Course_Details.objects.filter(student_roll_id=roll)
        obj.delete()
        return redirect("/api/home_course")

class DeleteSingleCourse(View):
    def get(self,request,roll,course_id):
        print(roll)
        print(course_id)
        obj=Student_Course_Details.objects.filter(student_roll_id=roll,course_name_id=course_id)
        obj.delete()
        return redirect("/api/home_course")

class ClassHomePage(View):
    def get(self,request):
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

class AddClassStudent(View):
    def get(self,request,roll):
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
        
class ViewClassStudents(View):   
    def get(self,request):
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

class DeleteClass(View):
    def get(self,request,roll):
        print(roll)
        stu = Student_Details.objects.get(pk=roll)
        class_obj=Class_Student.objects.filter(student_id=stu)
        class_obj.delete()
        return redirect('/api/home_class/')

class TimeTable(View):
    def get(request):
        dep=Department_wise_Course_Details.objects.all()
        courses=[]
        for d in dep:
            courses.append(d.course_title)
        
        return render(request, "timetable.html",{'courses':courses})

class ViewTimeTable(View):
    def get(self,request,class_title):
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

class SetClass(View):
    def get(self,request):
        if request.method=='POST':
            class_name=request.POST.get('class_name')
            
            time_obj=Time_Table_Model.objects.all()
            class_obj=Class_Details.objects.all()
            dep_obj=Department_wise_Course_Details.objects.all()
            class_list=[]
            first_list=[]
            second_list=[]
            third_list=[]
            for dep in dep_obj:
                first_list.append(dep.course_title)
                second_list.append(dep.course_title)
                third_list.append(dep.course_title)

            for cls in class_obj:
                class_list.append(cls.class_name)
            class_list.remove(class_name)

            
            for tym_obj in time_obj:
                first_hour=tym_obj.first_hour_course.course_title
                second_hour=tym_obj.second_hour_course.course_title
                third_hour=tym_obj.third_hour_course.course_title
                first_list.remove(first_hour)
                second_list.remove(second_hour)
                third_list.remove(third_hour)


            print(first_list,second_list,third_list)
            
            return render(request,"timetable.html",{'first_list':first_list,'second_list':second_list,'third_list':third_list,'class_section':class_name})

class ChooseClass(View):      
    def get(self,request):
        classes=Class_Details.objects.all()
        return render(request,"choose_class.html",{'classes':classes})

class ViewAllTimeTables(View):
    def get(self,request):
        time_table_objects=Time_Table_Model.objects.all()
        response_list=[]
        for time_obj in time_table_objects:
            temp_list=[]
            class_id = time_obj.class_id
            class_object=Class_Details.objects.get(pk=class_id.id)
            class_name=class_object.class_name
            fh=time_obj.first_hour_course.course_title
            sh=time_obj.second_hour_course.course_title
            th=time_obj.third_hour_course.course_title

            temp_list.append(class_name)
            temp_list.append(fh)
            temp_list.append(sh)
            temp_list.append(th)

            response_list.append(temp_list)
        print(temp_list)

        return render(request,"view_all_timetables.html",{'response_list':response_list})

class AddClassHomePage(View):
    def get(self,request):
        classes=Class_Details.objects.all()
        return render(request,"display_classes.html",{'classes':classes})

class AddClass(View):
    def get(self,request):
        return render(request,"new_class.html")

class ClassObjectCreate(View):
    def classObjectCreate(request):
        if request.method == 'POST':
            class_name = request.POST.get('class_name')
            check_object = Class_Details.objects.filter(class_name=class_name)
            if len(check_object)==0:
                class_object = Class_Details(class_name=class_name)
                class_object.save()
                d1=Department_wise_Course_Details.objects.get(pk=1)
                t1=Time_Table_Model(class_id=class_object,first_hour_course=d1,second_hour_course=d1,third_hour_course=d1)
                t1.save()

                return redirect('/api/add_home_class')
            else:
                return redirect('/api/add_home_class')

class DeleteSection(View):
    def get(self,request,class_id):
        c1=Class_Details.objects.get(pk=class_id)
        c1.delete()
        return redirect('/api/add_home_class')

class SearchStudentHome(View):
    def search_student(request):
        return render(request,"search.html")

class SearchStudent(View):  
    def post(self,request):
        if request.method == 'POST':
            student_name = request.POST.get('name')
            objects = Student_Details.objects.filter(name__contains=student_name)
            student_list=[]
            for obj in objects:
                temp=[]
                temp.append(obj.name)
                temp.append(obj.roll)
                print(obj.department)
                temp.append(obj.department.department_name)
                student_list.append(temp)

            return render(request,"search_details.html",{'response':student_list})

class TopNthCourse(View):    
    def get(self,request):
        if request.method == 'POST':
            top_n=request.POST.get("name")
            temp_list=[]
            top_course=(Student_Course_Details.objects.values('course_name').annotate(count=Count('id')).order_by('-count')[:int(top_n)])
            for item in top_course:
                l=[]
                l.append(Department_wise_Course_Details.objects.get(pk=item['course_name']).course_title)
                l.append(item['count'])
                temp_list.append(l)
            return render(request,"topNthCourse.html",{'n':top_n,'courses':temp_list}) 

# Rendering Home Page 
class MainHomePage(View):
    def get(self,request):
        return render(request,"main_home.html")   

class RegisterUser(View):
    def post(self,request):
        if request.method == 'POST':
            print("entered register_user")
            first_name = request.POST['first_name']
            last_name = request.POST['last_name']
            username = request.POST['username']
            email = request.POST['email']
            password = request.POST['password']
            confirm_password = request.POST['confirm_password']
            if password == confirm_password:
                print("same password")
                if User.objects.filter(username=username).exists():
                    print("user already exists")
                    messages.info(request,'User Already Exists')
                    return redirect('/api/register_user/')
                else:
                    
                    user=User.objects.create_user(username=username,password=password,email=email,first_name=first_name,last_name=last_name)
                    
                    user.set_password(password)
                    auth_token=str(uuid.uuid4())
                    account_obj = Account.objects.create(user = user,auth_token = auth_token)
                    account_obj.save()


                    user.is_staff=False
                    user.save()

                    send_mail_after_registration(auth_token,email)
                
                    return redirect('/api/token_send/')
                
    def get(self,request):
        return render(request,"register.html")

class RegisterStaff(View):   
    def post(self,request):

        print("entered register_staff")
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        if password == confirm_password:
            print("same password")
            if User.objects.filter(username=username).exists():
                print("user already exists")
                messages.info(request,'User Already Exists')
                return redirect('/api/register_staff/')
            else:
                    
                user=User.objects.create_user(username=username,password=password,email=email,first_name=first_name,last_name=last_name)
                    
                user.set_password(password)
                auth_token=str(uuid.uuid4())
                account_obj = Account.objects.create(user = user,auth_token = auth_token)
                account_obj.save()


                user.is_staff=True
                user.save()
               # send_mail_after_registration(auth_token,email)
                return redirect('/api/token_send/')
               
    def get(self,request):
        return render(request,"register_staff.html")

class LoginUser(View):
    def get(self,request):
        print("entered login user")
        return render(request,"login.html")

    def post(self,request):
            print("entered login page")
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = auth.authenticate(username=username,password=password)
            account_obj = Account.objects.filter(user=user)
            #if(account_obj[0].is_verified == False):
               #return redirect('/api/token_send/')

            if user is not None:                                                                                                                                                                                     
                print("login successful")
                login(request, user)
               
                if user.is_staff:                                                                                                                                                                                                                                                                                       
                    return redirect('/api/home/')
                else:
                    return redirect('/api/home_course')
            else:
                messages.info(request,'Invaid User')
                return redirect('/api/login_user/')
            
        
            
class LogoutUser(View):
    def get(self,request):
        auth.logout(request)
        return redirect('/api/')

class ViewPDF(View):
    def get(self,request):
        buf = io.BytesIO()
        c =  canvas.Canvas(buf,pagesize=letter,bottomup=0)
        ob = c.beginText()
        ob.setTextOrigin(inch,inch)
        ob.setFont("Helvetica",14)
        
        time_table_objects=Time_Table_Model.objects.all()
        lines = []

        for obj in time_table_objects:
            lines.append("Class-"+obj.class_id.class_name+" Time-Table")
            lines.append("First Hour Course: "+obj.first_hour_course.course_title)
            lines.append("Second Hour Course: "+obj.second_hour_course.course_title)
            lines.append("Third Hour Course: "+obj.third_hour_course.course_title)
            lines.append(" ")

        for line in lines:
            ob.textLine(line)

        c.drawText(ob)
        c.showPage()
        c.save()
        buf.seek(0)

        return FileResponse(buf,as_attachment=True,filename='Time-Table.pdf')

class ResumeUpload(View):
    def get(self,request):
        student_objs=Student_Details.objects.all()
        
        return render(request,"resume_upload.html",{'student_list':student_objs})

class SaveResume(View):
    def post(self,request):
        if request.method == 'POST':
            student_id = request.POST.get('student')
            file = request.FILES['file_id']
            print(student_id)
            print(file)
            file_name = default_storage.save(file.name, file)

            file = default_storage.open(file_name)
            file_url = default_storage.url(file_name)
            print(file_url)

            student_obj=Student_Details.objects.get(pk=student_id)
            if Resumes.objects.filter(student_id=student_obj).exists():
                res=Resumes.objects.get(student_id=student_obj)
                res.resume=file_url
                res.save()
            else:
                resume_object =Resumes(student_id=student_obj,resume=file_url)
                resume_object.save()

            return redirect('/api/')

class ViewAllResumes(View):
    def get(self,request):
        resumes=Resumes.objects.all()
        
        return render(request,"all_resumes.html",{'resumes':resumes})

class ViewPDFFile(View):
    def get(request,file_name):
        url_link="http://127.0.0.1:8001/media/"+file_name
        print(url_link)
        return HttpResponseRedirect(url_link)

class SuccessPage(View):
    def get(self,request):
        return render(request,"success.html")

class SendToken(View):
    def get(self,request):
        return render(request,"token_send.html")

def send_mail_after_registration(token,email):
    subject = 'Account Verification'
    message = f'Hi click the link to verify the account http://127.0.0.1:8001/api/verify/{token}'
    email_from = settings.EMAIL_HOST_USER 
    reception_list = [email]
    send_mail(subject,message,email_from,reception_list)


def verify(request,token):
   
    account_obj = Account.objects.filter(auth_token = token).first()
    print(account_obj.created_at)  
    date_str=str(account_obj.created_at)
    dt_obj = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S.%f%z')
    now_timestamp = datetime.now().timestamp() 
    seconds = int(now_timestamp - dt_obj.timestamp()) 
    print(seconds)   
    if(seconds>=30):
        user=User.objects.get(pk=account_obj.user.id)
        print(user.first_name)
        user.delete()
        account_obj.delete()    

        return render(request,"time_out.html")
    if account_obj:
        print("found")
        account_obj.is_verified = True
        account_obj.save()                                                                                  
    else:                                                                                                                                                                                                                                                                                                                                                                                                                                                            
        return render('/api/error_page/')
        
    return redirect('/api/success/')

class ErrorPage(View):
   def get(self,request):
        return render(request,"error_page.html")
   
def recently_updated(request,student_id):
    recently_updated_student = None
    if 'recently_updated' in request.session:
        if student_id in request.session['recently_updated']:
            request.session['recently_updated'].remove(student_id)
        
        recently_updated_student = Student_Details.objects.filter(pk__in=request.session['recently_updated'])
        request.session['recently_updated'].insert(0,student_id)

        if len(request.session['recently_updated'])>5:
            request.session['recently_updated'].pop()
    else:
        request.session['recently_updated'] = [student_id]

    request.session.modified = True

    return render(request,"home.html",{'recently_updated_student':recently_updated_student})   

def send_mail_for_update_password(token,email,session_key):
    print("In email ",session_key)
    subject = 'Account Verification'
    message = f'Hi click the link to verify the account http://127.0.0.1:8001/api/verify_password/{token}/{session_key}'
    email_from = settings.EMAIL_HOST_USER 
    reception_list = [email]
    send_mail(subject,message,email_from,reception_list)

def update_password_home(request):
    return render(request,"update_password.html")

def update_password(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        update_password_password=request.POST.get('password')
        print("update password in post",update_password_password)
        update_password_id=username
        user = User.objects.filter(username = username).first()
        email=user.email
        update_token=str(uuid.uuid4())
        print("token in mail",update_token)
        request.session = SessionStore()
        request.session['update_password'] = update_password_password
        request.session['update_username'] = username 
        request.session['old_password']=User.objects.get(username=username).password
        request.session['token']=update_token
        if not request.session.session_key:
                request.session.save()
        
        session_key = request.session.session_key
        print("In update passw",session_key)
        request.session.set_expiry(1000000)
        request.session.save()                                                                                                                                                                                                                         
        send_mail_for_update_password(update_token,email,session_key)

        return redirect('/api/token_send/')

def verify_password(request,token,session_key):
    engine = import_module(settings.SESSION_ENGINE)
    session = engine.SessionStore(session_key)
    print("in verify",session_key)
    if 'update_password' in session:

        
        username = session.get('update_username')
        password = session.get('update_password')
        if session.get('token') == token:
            user = User.objects.get(username=username)
            user.set_password(password)
            user.save()
            if(session.get('old_password')==user.password):
                print("Not changed")
            else:
                print("changed")

            return redirect('/api/login_user/')
       
    else:
        return render(request,"time_out.html",{'data':session.get('update_username')})
    
def dashboard_view(request):
    user_id = request.session.get('user_id', None)
    if user_id:
        
        user = User.objects.get(id=user_id)
        
    return render(request, 'dashboard.html')    

def unauthorized(request):
    return render(request,"unauthorized.html")


