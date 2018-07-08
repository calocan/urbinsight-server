import graphene
from app.helpers.sankey_helpers import add_sankey_graph_to_resource_dict
from app.schema_models.region_schema import RegionType, region_fields
from app.schema_models.data_schema import ResourceDataType, resource_data_fields
from django.db import models
from django.db.models import Model
from graphene import InputObjectType, InputField, ObjectType, DateTime, String, Mutation, Field
from graphene_django.types import DjangoObjectType
from app.models import Resource, Region
from rescape_graphene import resolver
from rescape_graphene import input_type_fields, REQUIRE, DENY, CREATE, \
    input_type_parameters_for_update_or_create, UPDATE, \
    guess_update_or_create, graphql_update_or_create, graphql_query, merge_with_django_properties

class ResourceType(DjangoObjectType):
    class Meta:
        model = Resource


# Modify data field to use the resolver.
# I guess there's no way to specify a resolver upon field creation, since graphene just reads the underlying
# Django model to generate the fields
ResourceType._meta.fields['data'] = Field(ResourceDataType, resolver=resolver)

resource_fields = merge_with_django_properties(ResourceType, dict(
    id=dict(create=DENY, update=REQUIRE),
    name=dict(create=REQUIRE),
    # This refers to the Resource, which is a representation of all the json fields of Resource.data
    data=dict(graphene_type=ResourceDataType, fields=resource_data_fields, default=lambda: dict()),
    # This is a Foreign Key. Graphene generates these relationships for us, but we need it here to
    # support our Mutation subclasses nd query_argument generation
    region=dict(graphene_type=RegionType, fields=region_fields)
))

resource_mutation_config = dict(
    class_name='Resource',
    crud={
        CREATE: 'createResource',
        UPDATE: 'updateResource'
    },
    resolve=guess_update_or_create
)


class UpsertResource(Mutation):
    """
        Abstract base class for mutation
    """
    resource = Field(ResourceType)

    def mutate(self, info, resource_data=None):
        """
            In addition to creating the correct default and update values, this also adds the sankey graph
            data to resource.data['graph']
        :param info:
        :param resource_data:
        :return:
        """
        update_or_create_values = input_type_parameters_for_update_or_create(resource_fields, resource_data)
        add_sankey_graph_to_resource_dict(update_or_create_values['defaults'])
        resource, created = Resource.objects.update_or_create(**update_or_create_values)
        return UpsertResource(resource=resource)


class CreateResource(UpsertResource):
    """
        Create Resource mutation class
    """

    class Arguments:
        resource_data = type('CreateResourceInputType', (InputObjectType,),
                             input_type_fields(resource_fields, CREATE, ResourceType))(required=True)


class UpdateResource(UpsertResource):
    """
        Update Resource mutation class
    """

    class Arguments:
        resource_data = type('UpdateResourceInputType', (InputObjectType,),
                             input_type_fields(resource_fields, UPDATE, ResourceType))(required=True)


graphql_update_or_create_resource = graphql_update_or_create(resource_mutation_config, resource_fields)
graphql_query_resources = graphql_query('resources', resource_fields)
