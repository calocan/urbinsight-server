from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt
from rescape_graphene.graphql_helpers.views import SafeGraphQLView


from rest_framework.routers import DefaultRouter
from app.views import views

router = DefaultRouter()

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^graphql', csrf_exempt(SafeGraphQLView.as_view(graphiql=True))),
]
