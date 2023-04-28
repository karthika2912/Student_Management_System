from django.contrib import admin
from .models import Account
from django.contrib.sessions.models import Session
# Register your models here.
admin.site.register(Account)
admin.site.register(Session)