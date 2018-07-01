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
    default_location=dict(type=Float, type_modifier=lambda typ: List(Float)),
    columns=dict(type=String, type_modifier=lambda typ: List(typ)),
    stage_key=dict(type=String),
    value_key=dict(type=String),
    location_key=dict(type=String),
    node_name_key=dict(type=String),
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

geometry_data_fields = dict(
    type=dict(type=String),
    coordinates=dict(type=String, type_modifier=lambda typ: List(typ))
)

GeometryDataType = type(
    'GeometryDataType',
    (ObjectType,),
    R.map_with_obj(
        # If we have a type_modifier function, pass the type to it, otherwise simply construct the type
        lambda k, v: R.prop_or(lambda typ: typ(), 'type_modifier', v)(R.prop('type', v)),
        geometry_data_fields)
)

node_data_fields = dict(
    name=dict(type=String),
    type=dict(type=String),
    value=dict(type=Float),
    geometry=dict(type=GeometryDataType, graphene_type=GeometryDataType, fields=geometry_data_fields, type_modifier=lambda typ: List(typ)),
    location=dict(type=String),
    material=dict(type=String),
    siteName=dict(type=String),
    coordinates=dict(type=String),
    annualTonnage=dict(type=String),
    junctionStage=dict(type=String),
    is_generalized=dict(type=String),
)

NodeDataType = type(
    'NodeDataType',
    (ObjectType,),
    R.map_with_obj(
        # If we have a type_modifier function, pass the type to it, otherwise simply construct the type
        lambda k, v: R.prop_or(lambda typ: typ(), 'type_modifier', v)(R.prop('type', v)),
        node_data_fields)
)

link_data_fields = dict(
    value=dict(type=Float),
    source=dict(type=NodeDataType, graphene_type=NodeDataType, fields=node_data_fields, type_modifier=lambda typ: List(typ)),
    target=dict(type=NodeDataType, graphene_type=NodeDataType, fields=node_data_fields, type_modifier=lambda typ: List(typ))
)

LinkDataType = type(
    'LinkDataType',
    (ObjectType,),
    R.map_with_obj(
        # If we have a type_modifier function, pass the type to it, otherwise simply construct the type
        lambda k, v: R.prop_or(lambda typ: typ(), 'type_modifier', v)(R.prop('type', v)),
        link_data_fields)
)

graph_data_fields = dict(
    links=dict(type=LinkDataType, graphene_type=LinkDataType, fields=link_data_fields, type_modifier=lambda typ: List(typ)),
    nodes=dict(type=NodeDataType, graphene_type=NodeDataType, fields=node_data_fields, type_modifier=lambda typ: List(typ))
)

GraphDataType = type(
    'GraphDataType',
    (ObjectType,),
    R.map_with_obj(
        # If we have a type_modifier function, pass the type to it, otherwise simply construct the type
        lambda k, v: R.prop_or(lambda typ: typ(), 'type_modifier', v)(R.prop('type', v)),
        graph_data_fields)
)

resource_data_fields = dict(
    settings=dict(
        type=SettingsDataType,
        graphene_type=SettingsDataType,
        fields=settings_data_fields,
        type_modifier=lambda typ: List(typ)
    ),
    raw_data=dict(
        type=String,
        type_modifier=lambda typ: List(String)
    ),
    graph=dict(
        type
    )
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
