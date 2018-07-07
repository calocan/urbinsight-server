from graphql_geojson import GeoJSONType

from graphene import InputObjectType, InputField, ObjectType, DateTime, String, Mutation, Field

from app.models import Feature
from rescape_graphene.schema_helpers import REQUIRE, graphql_update_or_create, graphql_query, guess_update_or_create, \
    CREATE, UPDATE, input_type_parameters_for_update_or_create, input_type_fields, merge_with_django_properties


class FeatureType(GeoJSONType):
    """
        This models the Feature type for Graphene/graphql. Because of the superclass GeoJSONType,
        the actually queryable object is in the form
        {
            geometry {
                type
                coordinates
            }
            properties {
              name
              description
              createdAt
              updatedAt
              data
            }
        }
    """
    class Meta:
        model = Feature
        geojson_field = 'location'


feature_fields = merge_with_django_properties(FeatureType, dict(
    name=dict(),
    description=dict(),
    created_at=dict(),
    updated_at=dict(),
    location=dict(create=REQUIRE),
))

feature_mutation_config = dict(
    class_name='Feature',
    crud={
        CREATE: 'createFeature',
        UPDATE: 'updateFeature'
    },
    resolve=guess_update_or_create
)


class UpsertFeature(Mutation):
    """
        Abstract base class for mutation
    """
    feature = Field(FeatureType)

    def mutate(self, info, feature_data=None):
        update_or_create_values = input_type_parameters_for_update_or_create(feature_fields, feature_data)
        feature, created = Feature.objects.update_or_create(**update_or_create_values)
        return UpsertFeature(feature=feature)


class CreateFeature(UpsertFeature):
    """
        Create Feature mutation class
    """

    class Arguments:
        feature_data = type('CreateFeatureInputType', (InputObjectType,),
                            input_type_fields(feature_fields, CREATE))(required=True)


class UpdateFeature(UpsertFeature):
    """
        Update Feature mutation class
    """

    class Arguments:
        feature_data = type('UpdateFeatureInputType', (InputObjectType,),
                            input_type_fields(feature_fields, UPDATE))(required=True)


graphql_update_or_create_feature = graphql_update_or_create(feature_mutation_config, feature_fields)
graphql_query_features = graphql_query('features', feature_fields)
