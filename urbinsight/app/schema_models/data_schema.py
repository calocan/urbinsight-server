import rescape_graphene.ramda as R
from graphene import InputObjectType, InputField, ObjectType, DateTime, String, Float, Int, Mutation, Field

###
# Data fields are not a Django model, rather a json blob that is the field data of the Region and Resource models
# So we list all the fields here and create a Graphene model RegionDataType and ResourceDataType
###

region_data_fields = R.merge_dicts(
    dict(
        example=dict(type=Float)
    )
)

RegionDataType = type('RegionDataType', (ObjectType,), R.map_with_obj(lambda k, v: R.prop('type', v)(), region_data_fields))

resource_data_fields = R.merge_dicts(
    dict(
        example=dict(type=Float)
    )
)

ResourceDataType = type('ResourceDataType', (ObjectType,), R.map_with_obj(lambda k, v: R.prop('type', v)(), resource_data_fields))
