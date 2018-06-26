import graphene
import rescape_graphene.ramda as R
import graphql_jwt
from graphene import ObjectType, Schema
from graphene_django.debug import DjangoDebug
#from graphql_jwt.decorators import login_required
from graphql_jwt.decorators import login_required
from sop.webapp.models import *
from sop.sop_api.schema_models import DataPointType, data_point_fields, CreateDataPoint, UpdateDataPoint, \
    GoalType, goal_fields, ScenarioType, scenario_fields, ProjectType, project_fields
from rescape_graphene.schema_helpers import allowed_query_arguments
from rescape_graphene.user_schema import CreateUser, UpdateUser, UserType, user_fields
from django.contrib.auth import get_user_model, get_user


class Query(ObjectType):
    debug = graphene.Field(DjangoDebug, name='__debug')
    users = graphene.List(UserType)
    viewer = graphene.Field(
        UserType,
        **allowed_query_arguments(user_fields)
    )

    @login_required
    def resolve_viewer(self, info, **kwargs):
       return info.context.user

    regions = graphene.List(
        RegionType,
        **allowed_query_arguments(region_fields)
    )

    resource = graphene.Field(
        ResourceType,
        **allowed_query_arguments(resource_fields)
    )

    scenario = graphene.Field(
        ScenarioType,
        **allowed_query_arguments(scenario_fields)
    )


    def resolve_users(self, info, **kwargs):
        return get_user_model().objects.filter(**kwargs)

    def resolve_current_user(self, info):
        context = info.context
        user = get_user(context)
        if not user:
            raise Exception('Not logged in!')

        return user

    def resolve_data_points(self, info, **kwargs):
        # Small correction here to change the data filter to data__contains to handle any json
        # https://docs.djangoproject.com/en/2.0/ref/contrib/postgres/fields/#std:fieldlookup-hstorefield.contains
        return DataPoint.objects.filter(
            **R.map_keys(lambda key: 'data__contains' if R.equals('data', key) else key, kwargs))

    def resolve_scenarios(self, info, **kwargs):
        return Scenario.objects.filter(**kwargs)

    def resolve_goals(self, info, **kwargs):
        return Goal.objects.filter(**kwargs)

    def resolve_projects(self, info, **kwargs):
        return Project.objects.filter(**kwargs)

    def resolve_data_point(self, info, **kwargs):
        return DataPoint.objects.get(**kwargs)

    def resolve_scenario(self, info, **kwargs):
        return Scenario.objects.get(**kwargs)

    def resolve_goal(self, info, **kwargs):
        return Goal.objects.get(**kwargs)

    def resolve_project(self, info, **kwargs):
        return Project.objects.get(**kwargs)


class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()
    update_user = UpdateUser.Field()
    # login = Login.Field()
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()

    create_data_point = CreateDataPoint.Field()
    update_data_point = UpdateDataPoint.Field()


schema = Schema(query=Query, mutation=Mutation)
