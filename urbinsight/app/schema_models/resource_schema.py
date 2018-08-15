from graphene import Field, Mutation, InputObjectType
from graphene_django.types import DjangoObjectType
from rescape_graphene import input_type_fields, REQUIRE, DENY, CREATE, \
    input_type_parameters_for_update_or_create, UPDATE, \
    guess_update_or_create, graphql_update_or_create, graphql_query, merge_with_django_properties
from rescape_graphene import ramda as R
from rescape_graphene import resolver

from app.helpers.sankey_helpers import add_sankey_graph_to_resource_dict
from app.models import Resource
from app.schema_models.resource_data_schema import ResourceDataType, resource_data_fields
from app.schema_models.region_schema import RegionType


class ResourceType(DjangoObjectType):
    """
        ResourceType models Resource, which represents a data resource such as water, energy, material, etc
    """
    class Meta:
        model = Resource


# Modify data field to use the resolver.
# I guess there's no way to specify a resolver upon field creation, since graphene just reads the underlying
# Django model to generate the fields
ResourceType._meta.fields['data'] = Field(ResourceDataType, resolver=resolver('data'))

resource_fields = merge_with_django_properties(ResourceType, dict(
    id=dict(create=DENY, update=REQUIRE),
    name=dict(create=REQUIRE),
    # This refers to the Resource, which is a representation of all the json fields of Resource.data
    data=dict(graphene_type=ResourceDataType, fields=resource_data_fields, default=lambda: dict()),
    # This is a Foreign Key. Graphene generates these relationships for us, but we need it here to
    # support our Mutation subclasses and query_argument generation
    # For simplicity we limit fields to id. Mutations can only us id, and a query doesn't need other
    # details of the region--it can query separately for that
    region=dict(graphene_type=RegionType, fields=merge_with_django_properties(RegionType, dict(id=dict(create=REQUIRE))))
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
        # Modifies defaults value to add .data.graph
        # We could decide in the future to generate this derived data on the client, but it's easy enough to do here
        add_sankey_graph_to_resource_dict(update_or_create_values['defaults'])
        if R.prop_or(False, 'id', update_or_create_values):
            resource, created = Resource.objects.update_or_create(**update_or_create_values)
        else:
            resource = Resource(**update_or_create_values['defaults'])
            resource.save()
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
