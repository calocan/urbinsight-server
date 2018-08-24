from django.http import HttpResponse
from rest_framework import exceptions
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from graphene_django.views import GraphQLView
import simplejson as json
from django.shortcuts import render

def home(request):
    is_admin = 'Admin' in [g.name for g in request.user.groups.all()]
    return render(request, 'home.html', {
        'user': {
            # None if anonymous
            'id': '%s' % request.user.id if request.user.id else 'null',
            # None if anonymous
            'name': "'{} {}'".format(request.user.first_name, request.user.last_name) if request.user.id else 'null',
            'admin': 'true' if is_admin else 'false'
        }
    })
