from collections import namedtuple

import rescape_graphene.ramda as R
from inflection import underscore
from rescape_graphene import resolver
from graphene import ObjectType, String, Float, List, Field, Int

###
# Data fields are not a Django model, rather a json blob that is the field data of the Region and Resource models
# So we list all the fields here and create a Graphene model RegionDataType and ResourceDataType
###


def resolver_for_dict_field(resource, context):
    """
        Resolver for the data field. This extracts the desired json fields from the context
        and creates a tuple of the field values. Graphene has no built in way for querying json types
    :param resource:
    :param context:
    :return:
    """
    # Take the camelized keys and underscore (slugify) to get them back to python form
    selections = R.map(lambda sel: underscore(sel.name.value), context.field_asts[0].selection_set.selections)
    field_name = context.field_name
    dct = R.map_keys(lambda key: underscore(key), R.pick(selections, getattr(resource, field_name)))
    return namedtuple('DataTuple', R.keys(dct))(*R.values(dct))


def resolver_for_dict_list(resource, context):
    """
        Resolver for the data field. This extracts the desired json fields from the context
        and creates a tuple of the field values. Graphene has no built in way for querying json types
    :param resource:
    :param context:
    :return:
    """
    # Take the camelized keys and underscore (slugify) to get them back to python form
    selections = R.map(lambda sel: underscore(sel.name.value), context.field_asts[0].selection_set.selections)
    field_name = context.field_name
    dcts = R.map(
        lambda dct: R.map_keys(lambda key: underscore(key), R.pick(selections, dct)),
        getattr(resource, field_name)
    )
    return R.map(lambda dct: namedtuple('DataTuple', R.keys(dct))(*R.values(dct)), dcts)


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
        type_modifier=lambda typ: List(typ, resolver=resolver_for_dict_list)
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
    geometry=dict(
        type=GeometryDataType,
        graphene_type=GeometryDataType,
        fields=geometry_data_fields,
        type_modifier=lambda typ: Field(typ, resolver=resolver_for_dict_field),
    ),
    properties=dict(type=String, type_modifier=lambda typ: List(typ)),
    property_values=dict(type=String, type_modifier=lambda typ: List(typ)),
    coordinates=dict(type=String),
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
    source=dict(type=Int),
    target=dict(type=Int),
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
    links=dict(type=LinkDataType, graphene_type=LinkDataType, fields=link_data_fields, type_modifier=lambda typ: List(typ, resolver=resolver_for_dict_list)),
    nodes=dict(type=NodeDataType, graphene_type=NodeDataType, fields=node_data_fields, type_modifier=lambda typ: List(typ, resolver=resolver_for_dict_list))
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
        type_modifier=lambda typ: Field(typ, resolver=resolver_for_dict_field)
    ),
    raw_data=dict(
        type=String,
        type_modifier=lambda typ: List(typ)
    ),
    graph=dict(
        type=GraphDataType,
        graphene_type=GraphDataType,
        fields=graph_data_fields,
        type_modifier=lambda typ: Field(typ, resolver=resolver_for_dict_field)
    ),
    material=dict(type=String)
)

ResourceDataType = type(
    'ResourceDataType',
    (ObjectType,),
    R.map_with_obj(
        # If we have a type_modifier function, pass the type to it, otherwise simply construct the type
        lambda k, v: R.prop_or(lambda typ: typ(), 'type_modifier', v)(R.prop('type', v)),
        resource_data_fields)
)
