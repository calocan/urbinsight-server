from collections import namedtuple

from rescape_graphene import ramda as R
from inflection import underscore

###
# Helpers for data fields. Data fields are not a Django model,
# rather a json blob that is the field data of the Region and Resource models
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
        Resolver for the data field that is a list. This extracts the desired json fields from the context
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