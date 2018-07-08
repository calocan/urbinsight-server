from graphene.types.generic import GenericScalar
from graphql_geojson import GeoJSONType, Geometry

from graphene import InputObjectType, InputField, ObjectType, DateTime, String, Mutation, Field

from app.models import Feature
from rescape_graphene import REQUIRE, graphql_update_or_create, graphql_query, guess_update_or_create, \
    CREATE, UPDATE, input_type_parameters_for_update_or_create, input_type_fields, merge_with_django_properties
from rescape_graphene import ramda as R


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
    location=dict(create=REQUIRE)
))


def as_graphql_geojson_format(geojson_field, field_dict):
    """
    GeoJSONType alters the format of the class, so we need to present the fields in the way that
    matches what it does. It would probably be better to write a function to interpret the the fields
    of GeoJSONType, but this matches our field_dict format
    :param geojson_field:
    :param field_dict:
    :return:
    """
    return dict(
        geometry=dict(
            type=Geometry,
            fields=dict(
                type=dict(type=String),
                coordinates=dict(type=GenericScalar),
            )
        ),
        # All properties minus the geojson_field
        properties=dict(type=FeatureType, fields=R.omit([geojson_field], field_dict))
    )


feature_fields_in_graphql_geojson_format = as_graphql_geojson_format(FeatureType._meta.geojson_field, feature_fields)

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
                            input_type_fields(feature_fields, CREATE, FeatureType))(required=True)


class UpdateFeature(UpsertFeature):
    """
        Update Feature mutation class
    """

    class Arguments:
        feature_data = type('UpdateFeatureInputType', (InputObjectType,),
                            input_type_fields(feature_fields, UPDATE, FeatureType))(required=True)


graphql_update_or_create_feature = graphql_update_or_create(feature_mutation_config, feature_fields)
graphql_query_features = graphql_query('features', feature_fields)
