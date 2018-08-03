from rescape_graphene import ramda as R, merge_with_django_properties, REQUIRE
from graphene import ObjectType, String, Float, List, Field, Int
from app.helpers.data_field_helpers import resolver_for_dict_field, resolver_for_dict_list
from app.schema_models.region_schema import RegionType


mapbox_data_fields = dict(
    type=dict(type=String),
    coordinates=dict(type=String, type_modifier=lambda typ: List(typ))
)

MapboxDataType = type(
    'MapboxDataType',
    (ObjectType,),
    R.map_with_obj(
        # If we have a type_modifier function, pass the type to it, otherwise simply construct the type
        lambda k, v: R.prop_or(lambda typ: typ(), 'type_modifier', v)(R.prop('type', v)),
        mapbox_data_fields)
)

mapbox_data_fields = dict(
    viewport=dict(
        type=MapboxDataType,
        graphene_type=MapboxDataType,
        fields=mapbox_data_fields,
        type_modifier=lambda typ: Field(typ, resolver=resolver_for_dict_field),
    )
)

# Mapbox settings for the User's use of a particular Region
MapboxDataType = type(
    'MapboxDataType',
    (ObjectType,),
    R.map_with_obj(
        # If we have a type_modifier function, pass the type to it, otherwise simply construct the type
        lambda k, v: R.prop_or(lambda typ: typ(), 'type_modifier', v)(R.prop('type', v)),
        mapbox_data_fields)
)


user_state_data_region_fields = dict(
    # Region reference
    # For simplicity we limit fields to id. Mutations can only us id, and a query doesn't need other
    # details of the region--it can query separately for that
    region=dict(graphene_type=RegionType,
                fields=merge_with_django_properties(RegionType, dict(id=dict(create=REQUIRE)))),
    mapbox=dict(type=MapboxDataType, graphene_type=MapboxDataType, fields=mapbox_data_fields,
                type_modifier=lambda typ: List(typ, resolver=resolver_for_dict_list)),
)

# References a Region model instance, dictating settings imposed on or chosen by a user for a particular Region
# to which they have some level of access. This also adds settings like mapbox that are particular to the User's use
# of the Region but that the Region itself doesn't care about
UserStateDataRegionType = type(
    'UserStateDataRegionType',
    (ObjectType,),
    R.map_with_obj(
        # If we have a type_modifier function, pass the type to it, otherwise simply construct the type
        lambda k, v: R.prop_or(lambda typ: typ(), 'type_modifier', v)(R.prop('type', v)),
        user_state_data_region_fields)
)

user_state_data_fields = dict(
    regions=dict(
        type=UserStateDataRegionType,
        graphene_type=UserStateDataRegionType,
        fields=user_state_data_region_fields,
        type_modifier=lambda typ: Field(typ, resolver=resolver_for_dict_field)
    ),
)

UserStateDataType = type(
    'UserStateDataType',
    (ObjectType,),
    R.map_with_obj(
        # If we have a type_modifier function, pass the type to it, otherwise simply construct the type
        lambda k, v: R.prop_or(lambda typ: typ(), 'type_modifier', v)(R.prop('type', v)),
        user_state_data_fields)
)
