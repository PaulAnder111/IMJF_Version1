from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect

def admin_required(function):
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role == 'admin':
            return function(request, *args, **kwargs)
        raise PermissionDenied
    return wrap

def resp_admin_required(function):
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role in ['admin', 'resp_admin']:
            return function(request, *args, **kwargs)
        raise PermissionDenied
    return wrap

def teacher_required(function):
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role in ['admin', 'teacher']:
            return function(request, *args, **kwargs)
        raise PermissionDenied
    return wrap

def secretaire_required(function):
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role in ['admin', 'secretaire']:
            return function(request, *args, **kwargs)
        raise PermissionDenied
    return wrap

def directeur_required(function):
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role in ['admin', 'directeur']:
            return function(request, *args, **kwargs)
        raise PermissionDenied
    return wrap