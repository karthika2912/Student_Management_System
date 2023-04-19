from rest_framework import serializers
from .models import Student_Details,Department_Details,Department_wise_Course_Details,Student_Course_Details

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model=Student_Details
        fields='__all__'

class Department_DetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model=Department_Details
        fields='__all__'

class Department_wise_Course_DetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model=Department_wise_Course_Details
        fields='__all__'

class Student_Course_DetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model=Student_Course_Details
        fields='__all__'
