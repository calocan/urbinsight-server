from django.http import HttpResponse
from rest_framework import exceptions
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from graphene_django.views import GraphQLView
import simplejson as json


# https://github.com/graphql-python/graphene-django/issues/264
class JWTGraphQLView(JSONWebTokenAuthentication, GraphQLView):

    def dispatch(self, request, *args, **kwargs):
        try:
            # if not already authenticated by django cookie sessions
            # check the JWT token by re-using our DRF JWT
            if not request.user.is_authenticated():
                request.user, request.token = self.authenticate(request)
        except exceptions.AuthenticationFailed as e:
            response = HttpResponse(
                json.dumps({
                    'errors': [str(e)]
                }),
                status=401,
                content_type='application/json'
            )
            return response
        return super(JWTGraphQLView, self).dispatch(request, *args, **kwargs)