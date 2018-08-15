from collections import namedtuple

from rescape_graphene import ramda as R
from inflection import underscore

###
# Helpers for data fields. Data fields are not a Django model,
# rather a json blob that is the field data of the Region and Resource models
###


def resolve_selections(context):
    """
        Returns the query fields for the current context.
        Take the camelized keys and underscore (slugify) to get them back to python form
    :param {ResolveInfo} context: The graphene resolution context
    :return: {[String]} The field names to that are in the query
    """
    return R.map(lambda sel: underscore(sel.name.value), context.field_asts[0].selection_set.selections)


def pick_selections(selections, data):
    """
        Pick the selections from the current data
    :param {[Sting]} selections: The field names to that are in the query
    :param {dict} data: Data to pick from
    :return: {DataTuple} data with limited to selections
    """
    dct = R.pick(selections, data)
    return namedtuple('DataTuple', R.keys(dct))(*R.values(dct))


def resolver_for_dict_field(resource, context):
    """
        Resolver for the data field. This extracts the desired json fields from the context
        and creates a tuple of the field values. Graphene has no built in way for querying json types
    :param resource:
    :param context:
    :return:
    """
    selections = resolve_selections(context)
    field_name = underscore(context.field_name)
    return pick_selections(selections, getattr(resource, field_name))


def resolver_for_dict_list(resource, context):
    """
        Resolver for the data field that is a list. This extracts the desired json fields from the context
        and creates a tuple of the field values. Graphene has no built in way for querying json types
    :param resource:
    :param context:
    :return:
    """
    # Take the camelized keys and underscore (slugify) to get them back to python form
    selections = resolve_selections(context)
    field_name = underscore(context.field_name)
    return R.map(lambda data: pick_selections(selections, data), getattr(resource, field_name))

@R.curry
def model_resolver_for_dict_field(model_class, resource, context):
    """
        Resolver for the data field. This extracts the desired json fields from the context
        and creates a tuple of the field values. Graphene has no built in way for querying json types
    :param model_class:
    :param resource:
    :param context:
    :return:
    """
    selections = resolve_selections(context)
    field_name = underscore(context.field_name)
    # Assume for simplicity that id is among selections
    return model_class.objects.get(id=R.prop('id', getattr(resource, field_name)))
