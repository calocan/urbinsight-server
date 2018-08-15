from django.db import transaction
from graphene import InputObjectType, Mutation, Field
from graphene_django.types import DjangoObjectType
from rescape_graphene import REQUIRE, graphql_update_or_create, graphql_query, guess_update_or_create, \
    CREATE, UPDATE, input_type_parameters_for_update_or_create, input_type_fields, merge_with_django_properties, \
    resolver, DENY
from rescape_graphene import ramda as R, increment_prop_until_unique, UserType, enforce_unique_props

from app.models import Region
from .feature_schema import FeatureType, feature_fields_in_graphql_geojson_format, mutate_feature
from .region_data_schema import RegionDataType, region_data_fields


class RegionType(DjangoObjectType):
    class Meta:
        model = Region

# Modify data field to use the resolver.
# I guess there's no way to specify a resolver upon field creation, since graphene just reads the underlying
# Django model to generate the fields
RegionType._meta.fields['data'] = Field(RegionDataType, resolver=resolver('data'))

region_fields = merge_with_django_properties(RegionType, dict(
    id=dict(create=DENY, update=REQUIRE),
    key=dict(create=REQUIRE, unique_with=increment_prop_until_unique(Region, None, 'key')),
    name=dict(create=REQUIRE),
    created_at=dict(),
    updated_at=dict(),
    # This refers to the RegionDataType, which is a representation of all the json fields of Region.data
    data=dict(graphene_type=RegionDataType, fields=region_data_fields, default=lambda: dict()),
    # This is a Foreign Key. Graphene generates these relationships for us, but we need it here to
    # support our Mutation subclasses below
    boundary=dict(graphene_type=FeatureType, fields=feature_fields_in_graphql_geojson_format),
    # Require the owner id to be specified for creates
    owner=dict(graphene_type=UserType, fields=merge_with_django_properties(UserType, dict(id=dict(create=REQUIRE))))
))

region_mutation_config = dict(
    class_name='Region',
    crud={
        CREATE: 'createRegion',
        UPDATE: 'updateRegion'
    },
    resolve=guess_update_or_create
)


class UpsertRegion(Mutation):
    """
        Abstract base class for mutation
    """
    region = Field(RegionType)

    @transaction.atomic
    def mutate(self, info, region_data=None):
        # First update/create the Feature. We don't have any way of knowing if the Feature data was modified
        # on an update so save it every time

        boundary_data = R.prop_or(None, 'boundary', region_data)
        if boundary_data:
            feature, feature_created = mutate_feature(boundary_data)
            modified_boundary_data = dict(id=feature.id)
        else:
            modified_boundary_data = boundary_data

        # Make sure that all props are unique that must be, either by modifying values or erring.
        # Merge in the persisted boundary data
        modified_region_data = R.merge(
            enforce_unique_props(region_fields, region_data),
            dict(boundary=modified_boundary_data)
        )

        update_or_create_values = input_type_parameters_for_update_or_create(region_fields, modified_region_data)
        # We can do update_or_create since we have a unique key in addition to the unique id
        region, created = Region.objects.update_or_create(**update_or_create_values)
        return UpsertRegion(region=region)


class CreateRegion(UpsertRegion):
    """
        Create Region mutation class
    """

    class Arguments:
        region_data = type('CreateRegionInputType', (InputObjectType,),
                           input_type_fields(region_fields, CREATE, RegionType))(required=True)


class UpdateRegion(UpsertRegion):
    """
        Update Region mutation class
    """

    class Arguments:
        region_data = type('UpdateRegionInputType', (InputObjectType,),
                           input_type_fields(region_fields, UPDATE, RegionType))(required=True)


graphql_update_or_create_region = graphql_update_or_create(region_mutation_config, region_fields)
graphql_query_regions = graphql_query('regions', region_fields)
