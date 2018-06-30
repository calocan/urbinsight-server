import rescape_graphene.ramda as R
from graphene import ObjectType, String, Float, List

###
# Data fields are not a Django model, rather a json blob that is the field data of the Region and Resource models
# So we list all the fields here and create a Graphene model RegionDataType and ResourceDataType
###
from rescape_graphene import input_type_class
from rescape_graphene.schema_helpers import CREATE

region_data_fields = dict(
    example=dict(type=Float)
)

RegionDataType = type(
    'RegionDataType',
    (ObjectType,),
    R.map_with_obj(
        # If we have a type_modifier function, pass the type to it, otherwise simply construct the type
        lambda k, v: R.prop_or(lambda typ: typ(), 'type_modifier', v)(R.prop('type', v)),
        region_data_fields)
)

stage_data_fields = dict(
    key=dict(type=String),
    name=dict(type=String),
    targets=dict(type=String, type_modifier=lambda typ: List(typ))
)

StageDataType = type(
    'StageDataType',
    (ObjectType,),
    R.map_with_obj(
        # If we have a type_modifier function, pass the type to it, otherwise simply construct the type
        lambda k, v: R.prop_or(lambda typ: typ(), 'type_modifier', v)(R.prop('type', v)),
        stage_data_fields)
)

settings_data_fields = dict(
    default_location=dict(type=String, type_modifier=lambda typ: List(String)),
    columns=dict(type=String, type_modifier=lambda typ: List(typ)),
    stage_key=dict(type=String),
    value_key=dict(type=String),
    location_key=dict(type=String),
    node_name_key=dict(type=String),
    raw_data=dict(
        type=String,
        type_modifier=lambda typ: List(String)
    ),
    stages=dict(
        type=StageDataType,
        graphene_type=StageDataType,
        fields=stage_data_fields,
        type_modifier=lambda typ: List(typ)
    )
)

SettingsDataType = type(
    'SettingsDataType',
    (ObjectType,),
    R.map_with_obj(
        # If we have a type_modifier function, pass the type to it, otherwise simply construct the type
        lambda k, v: R.prop_or(lambda typ: typ(), 'type_modifier', v)(R.prop('type', v)),
        settings_data_fields)
)

resource_data_fields = dict(
    settings=dict(
        type=SettingsDataType,
        graphene_type=SettingsDataType,
        fields=settings_data_fields,
        type_modifier=lambda typ: List(typ)
    ),
    material=dict(type=String),
)

ResourceDataType = type(
    'ResourceDataType',
    (ObjectType,),
    R.map_with_obj(
        # If we have a type_modifier function, pass the type to it, otherwise simply construct the type
        lambda k, v: R.prop_or(lambda typ: typ(), 'type_modifier', v)(R.prop('type', v)),
        resource_data_fields)
)
