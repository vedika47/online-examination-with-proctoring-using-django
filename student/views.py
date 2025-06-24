from django.shortcuts import render,redirect,reverse
from .import forms,models
from django.db.models import Sum
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required,user_passes_test
from django.conf import settings
from datetime import date, timedelta
from exam import models as QMODEL
from teacher import models as TMODEL
from django.contrib.auth import logout as lg
import json

# from .pr import run
#  myapp/views.py

import tkinter as tk
from PIL import Image, ImageTk
import io

from PIL import Image, ImageTk, ImageGrab
import base64

import threading
import asyncio
from asgiref.sync import sync_to_async

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

import base64
import cv2
import numpy as np

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import Course, Question  # Import your models here

def start_exam_view(request, pk):
    print("inside start exam view")
    
    # Process camera stream if needed
    # process_camera_stream(request)
    
    course = Course.objects.get(id=pk)
    questions = Question.objects.filter(course=course)
    
    # Handle POST request
    if request.method == 'POST':
        print("post method ")
        
        # Retrieve base64-encoded image data from the POST request
        image_data = request.POST.get('image_data', '')
        if image_data:
            # Decode base64-encoded image data
            image_data = base64.b64decode(image_data.split(",")[1])

            # Convert image data to a numpy array
            nparr = np.frombuffer(image_data, np.uint8)

            # Decode numpy array to an OpenCV image
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            # Process the frame for cheating detection
            gray_frame = process_frame_for_cheating_detection(frame)

            # Perform cheating detection algorithm
            cheating_percentage = perform_cheating_detection(gray_frame)

            # Determine if cheating percentage is above threshold
            if cheating_percentage > 60:
                warning_message = 'Warning: Possible cheating detected! Please focus on the exam.'
            else:
                warning_message = None

            # Convert processed frame back to base64-encoded image data
            _, encoded_frame = cv2.imencode('.jpg', gray_frame)
            encoded_image_data = base64.b64encode(encoded_frame).decode('utf-8')

            # Return processed frame as base64-encoded image data in JSON response
            return JsonResponse({'status': 'success', 'processed_image_data': encoded_image_data, 'warning_message': warning_message})

        else:
            # Handle case where image data is missing
            return JsonResponse({'status': 'error', 'message': 'No image data provided'})

    # Handle GET request
    else:
        response = render(request, 'student/start_exam.html', {'course': course, 'questions': questions})
        response.set_cookie('course_id', course.id)
        return response





# def my_view(request):
#     # Create a Tkinter window with a label
#     root = tk.Tk()
#     root.geometry("400x300")
#     label = tk.Label(root, text="Hello, Tkinter!", font=("Arial", 20))
#     label.pack()

#     # Capture the screenshot of the Tkinter window
#     image = ImageGrab.grab(bbox=(0, 0, 400, 300))  # Adjust the coordinates as needed
#     img_byte_array = io.BytesIO()
#     image.save(img_byte_array, format='PNG')
#     img_byte_array.seek(0)

#     # Convert the screenshot to base64
#     img_base64 = base64.b64encode(img_byte_array.read()).decode('utf-8')

#     # Pass the base64-encoded image to the template
#     context = {'image': img_base64}
#     return render(request, 'student/my_template.html', context)




#for showing signup/login button for student
def studentclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'student/studentclick.html')

def student_signup_view(request):
    userForm=forms.StudentUserForm()
    studentForm=forms.StudentForm()
    mydict={'userForm':userForm,'studentForm':studentForm}
    if request.method=='POST':
        userForm=forms.StudentUserForm(request.POST)
        studentForm=forms.StudentForm(request.POST,request.FILES)
        if userForm.is_valid() and studentForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            student=studentForm.save(commit=False)
            student.user=user
            student.save()
            my_student_group = Group.objects.get_or_create(name='STUDENT')
            my_student_group[0].user_set.add(user)
        return HttpResponseRedirect('studentlogin')
    return render(request,'student/studentsignup.html',context=mydict)

def is_student(user):
    return user.groups.filter(name='STUDENT').exists()

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_dashboard_view(request):
    dict={
    
    'total_course':QMODEL.Course.objects.all().count(),
    'total_question':QMODEL.Question.objects.all().count(),
    }
    return render(request,'student/student_dashboard.html',context=dict)

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_exam_view(request):
    courses=QMODEL.Course.objects.all()
    return render(request,'student/student_exam.html',{'courses':courses})

@login_required(login_url='studentlogin')
@user_passes_test(is_student)

def take_exam_view(request,pk):
    course=QMODEL.Course.objects.get(id=pk)
    total_questions=QMODEL.Question.objects.all().filter(course=course).count()
    questions=QMODEL.Question.objects.all().filter(course=course)
    total_marks=0
    for q in questions:
        total_marks=total_marks + q.marks
    
    return render(request,'student/take_exam.html',{'course':course,'total_questions':total_questions,'total_marks':total_marks})

def logout(request):
    lg(request)
    return redirect("")

# def start_exam_view(request,pk):
    
#     process_camera_stream(request)
    
#     course=QMODEL.Course.objects.get(id=pk)
#     questions=QMODEL.Question.objects.all().filter(course=course)
#     if request.method=='POST':
#         print("post method ")
#         pass
    
#     response= render(request,'student/start_exam.html',{'course':course,'questions':questions})
#     response.set_cookie('course_id',course.id)
#     # run.cam()
#     return response





# def calculate_marks_view(request):
#     if request.COOKIES.get('course_id') is not None:
#         course_id = request.COOKIES.get('course_id')
#         course=QMODEL.Course.objects.get(id=course_id)
        
#         total_marks=0
#         questions=QMODEL.Question.objects.all().filter(course=course)
#         for i in range(len(questions)):
            
#             selected_ans = request.COOKIES.get(str(i+1))
#             actual_answer = questions[i].answer
#             if selected_ans == actual_answer:
#                 total_marks = total_marks + questions[i].marks
#         student = models.Student.objects.get(user_id=request.user.id)
#         result = QMODEL.Result()
#         result.marks=total_marks
#         result.exam=course
#         result.student=student
#         result.save()

#         return HttpResponseRedirect('view-result')
    

# another try for above function

def calculate_marks_view(request):
    if request.COOKIES.get('course_id') is not None:
        course_id = request.COOKIES.get('course_id')
        course = QMODEL.Course.objects.get(id=course_id)
        
        total_marks = 0
        questions = QMODEL.Question.objects.filter(course=course)
        
        for i, question in enumerate(questions, start=1):
            selected_ans = request.COOKIES.get(str(i))
            if selected_ans == question.answer:
                total_marks += question.marks
        
        student = models.Student.objects.get(user_id=request.user.id)
        result = QMODEL.Result.objects.create(
            marks=total_marks,
            exam=course,
            student=student
        )
        
        return HttpResponseRedirect('view-result')
    
    # If 'course_id' cookie is not found or condition is not met,
    # return a response to handle the situation.
    return HttpResponseRedirect('/')  # Redirect to the homepage, for example




@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def view_result_view(request):
    courses=QMODEL.Course.objects.all()
    return render(request,'student/view_result.html',{'courses':courses})
    

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def check_marks_view(request,pk):
    course=QMODEL.Course.objects.get(id=pk)
    student = models.Student.objects.get(user_id=request.user.id)
    results= QMODEL.Result.objects.all().filter(exam=course).filter(student=student)
    return render(request,'student/check_marks.html',{'results':results})

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_marks_view(request):
    courses=QMODEL.Course.objects.all()
    return render(request,'student/student_marks.html',{'courses':courses})



@csrf_exempt
def pcs(request):
   

    print("Request Method:", request.method)
    print("HELLo CAMERA CHECKING FUNCtion")
    if request.method == 'POST':
        print("IN IF")
        # Retrieve the base64-encoded image data from the POST request
        image_data = request.POST.get('image_data', '')

        # Decode the base64-encoded image data
        image_data = base64.b64decode(image_data.split(",")[1])

        # Convert the image data to a numpy array
        nparr = np.frombuffer(image_data, np.uint8)

        # Decode the numpy array to an OpenCV image
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # Process the frame for cheating detection
        gray_frame = process_frame_for_cheating_detection(frame)

        # Perform cheating detection algorithm
        cheating_percentage = perform_cheating_detection(gray_frame)

        # If cheating percentage is more than 60%, send a warning message
        if cheating_percentage > 60:
            warning_message = 'Warning: Possible cheating detected! Please focus on the exam.'
        else:
            warning_message = None

        # Convert the processed frame back to base64-encoded image data
        _, encoded_frame = cv2.imencode('.jpg', gray_frame)
        encoded_image_data = base64.b64encode(encoded_frame).decode('utf-8')

        # Return the processed frame as base64-encoded image data in JSON response
        return JsonResponse({'status': 'success', 'processed_image_data': encoded_image_data, 'warning_message': warning_message})
    else:
        # Return a JSON response with an error message if the request method is not POST
        print("not a post method")
        return JsonResponse({'status': 'error', 'message': 'Only POST requests are allowed'})


def process_frame_for_cheating_detection(frame):
    # Convert the frame to grayscale
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    return gray_frame

def perform_cheating_detection(frame):
    # Load pre-trained face detection model
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    # Detect faces in the grayscale frame
    faces = face_cascade.detectMultiScale(frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    # Calculate cheating percentage based on the number of detected faces
    cheating_percentage = len(faces) * 60  # Assuming each detected face adds 10% to the cheating percentage

    # Ensure the cheating percentage does not exceed 100%
    cheating_percentage = min(cheating_percentage, 100)

    # return cheating_percentage
    return 100


def start_exam_view(request,pk):
    print("inside start exam view")
    # process_camera_stream(request)
    
    course=QMODEL.Course.objects.get(id=pk)
    questions=QMODEL.Question.objects.all().filter(course=course)
    if request.method=='POST':
        print("post method ")
        pass
    
    response= render(request,'student/start_exam.html',{'course':course,'questions':questions})
    response.set_cookie('course_id',course.id)
    return response

