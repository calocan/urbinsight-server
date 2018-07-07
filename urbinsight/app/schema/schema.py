import graphene
import rescape_graphene.ramda as R
import graphql_jwt
from app.models import Resource, Region, Feature
from app.schema_models.feature_schema import CreateFeature, UpdateFeature, feature_fields, FeatureType
from app.schema_models.region_schema import UpdateRegion, CreateRegion, RegionType, region_fields
from app.schema_models.resource_schema import ResourceType, resource_fields, CreateResource, UpdateResource
from graphene import ObjectType, Schema
from graphene_django.debug import DjangoDebug
#from graphql_jwt.decorators import login_required
from graphql_jwt.decorators import login_required
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

    region = graphene.Field(
        RegionType,
        **allowed_query_arguments(region_fields)
    )

    resources = graphene.List(
        ResourceType,
        **allowed_query_arguments(resource_fields)
    )

    resource = graphene.Field(
        ResourceType,
        **allowed_query_arguments(resource_fields)
    )

    features = graphene.List(
        FeatureType,
        **allowed_query_arguments(feature_fields)
    )

    feature = graphene.Field(
        FeatureType,
        **allowed_query_arguments(feature_fields)
    )

    def resolve_users(self, info, **kwargs):
        return get_user_model().objects.filter(**kwargs)

    def resolve_current_user(self, info):
        context = info.context
        user = get_user(context)
        if not user:
            raise Exception('Not logged in!')

        return user

    def resolve_resources(self, info, **kwargs):
        # Small correction here to change the data filter to data__contains to handle any json
        # https://docs.djangoproject.com/en/2.0/ref/contrib/postgres/fields/#std:fieldlookup-hstorefield.contains
        return Resource.objects.filter(
            **R.map_keys(lambda key: 'data__contains' if R.equals('data', key) else key, kwargs))


    def resolve_resource(self, info, **kwargs):
        return Resource.objects.get(**kwargs)


    def resolve_regions(self, info, **kwargs):
        # Small correction here to change the data filter to data__contains to handle any json
        # https://docs.djangoproject.com/en/2.0/ref/contrib/postgres/fields/#std:fieldlookup-hstorefield.contains
        return Region.objects.filter(
            **R.map_keys(lambda key: 'data__contains' if R.equals('data', key) else key, kwargs))


    def resolve_region(self, info, **kwargs):
        return Region.objects.get(**kwargs)


    def resolve_features(self, info, **kwargs):
        return Feature.objects.filter(**kwargs)

    def resolve_feature(self, info, **kwargs):
        return Feature.objects.get(**kwargs)


class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()
    update_user = UpdateUser.Field()
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()

    create_region = CreateRegion.Field()
    update_region = UpdateRegion.Field()
    create_resource = CreateResource.Field()
    update_resource = UpdateResource.Field()
    create_feature = CreateFeature.Field()
    update_feature = UpdateFeature.Field()


schema = Schema(query=Query, mutation=Mutation)
