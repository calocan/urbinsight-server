import graphene
from app.schema_models.data_schema import RegionDataType, region_data_fields
from graphene_django.types import DjangoObjectType
from graphene import InputObjectType, InputField, ObjectType, DateTime, String, Mutation, Field

from app.models import Region
from rescape_graphene import resolver
from rescape_graphene.schema_helpers import REQUIRE, graphql_update_or_create, graphql_query, guess_update_or_create, \
    CREATE, UPDATE, input_type_parameters_for_update_or_create, input_type_fields, merge_with_django_properties


class RegionType(DjangoObjectType):
    class Meta:
        model = Region


# Modify data field to use the resolver.
# I guess there's no way to specify a resolver upon field creation, since graphene just reads the underlying
# Django model to generate the fields
RegionType._meta.fields['data'] = Field(RegionDataType, resolver=resolver)

region_fields = merge_with_django_properties(RegionType, dict(
    key=dict(create=REQUIRE),
    name=dict(create=REQUIRE),
    created_at=dict(),
    updated_at=dict(),
    # This refers to the RegionDataType, which is a representation of all the json fields of Region.data
    data=dict(graphene_type=RegionDataType, fields=region_data_fields, default=lambda: dict())
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

    def mutate(self, info, region_data=None):
        update_or_create_values = input_type_parameters_for_update_or_create(region_fields, region_data)
        region, created = Region.objects.update_or_create(**update_or_create_values)
        return UpsertRegion(region=region)


class CreateRegion(UpsertRegion):
    """
        Create Region mutation class
    """

    class Arguments:
        region_data = type('CreateRegionInputType', (InputObjectType,),
                           input_type_fields(region_fields, CREATE))(required=True)


class UpdateRegion(UpsertRegion):
    """
        Update Region mutation class
    """

    class Arguments:
        region_data = type('UpdateRegionInputType', (InputObjectType,),
                           input_type_fields(region_fields, UPDATE))(required=True)


graphql_update_or_create_region = graphql_update_or_create(region_mutation_config, region_fields)
graphql_query_regions = graphql_query('regions', region_fields)
