"""
Admin Konfiguration für Users App.

Verwendet Django's Standard User Admin.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

# User Admin ist bereits registriert durch django.contrib.auth
# Keine zusätzliche Konfiguration nötig