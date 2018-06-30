import rescape_graphene.ramda as R
from graphene import InputObjectType, InputField, ObjectType, DateTime, String, Float, Int, Mutation, Field, List

###
# Data fields are not a Django model, rather a json blob that is the field data of the Region and Resource models
# So we list all the fields here and create a Graphene model RegionDataType and ResourceDataType
###

region_data_fields = dict(
    example=dict(type=Float)
)

RegionDataType = type(
    'RegionDataType',
    (ObjectType,),
    R.map_with_obj(
        # Here we use type_arg for List construction
        lambda k, v: R.prop('type', v)(*R.compact([R.prop_or(None, 'type_arg', v)])),
        region_data_fields)
)

stage_data_fields = dict(
    source=dict(type=String),
    name=dict(type=String),
    targets=dict(type=List, type_arg=String)
)

StageDataType = type(
    'StageDataType',
    (ObjectType,),
    R.map_with_obj(
        # Here we use type_arg for List construction
        lambda k, v: R.prop('type', v)(*R.compact([R.prop_or(None, 'type_arg', v)])),
        stage_data_fields)
)

resource_data_fields = R.merge_dicts(
    dict(
        default_location=dict(type=List, type_arg=String),
        columns=dict(type=List, type_arg=String),
        stage_key=dict(type=String),
        value_key=dict(type=String),
        location_key=dict(type=String),
        node_name_key=dict(type=String),
        stages=dict(graphene_type=StageDataType, fields=stage_data_fields, type=List, type_arg=StageDataType)
    )
)

ResourceDataType = type(
    'ResourceDataType',
    (ObjectType,),
    R.map_with_obj(
        # Here we use type_arg for List construction
        lambda k, v: R.prop('type', v)(*R.compact([R.prop_or(None, 'type_arg', v)])),
        resource_data_fields))
