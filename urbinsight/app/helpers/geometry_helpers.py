from json import dumps
from django.contrib.gis.geos import GeometryCollection, GEOSGeometry, Polygon


def geometry_from_feature(feature):
    str = dumps(feature['geometry'])
    return GEOSGeometry(str)

def ewkt_from_feature(feature):
    return geometry_from_feature(feature).ewkt


# https://gis.stackexchange.com/questions/177254/create-a-geosgeometry-from-a-featurecollection-in-geodango
def geometrycollection_from_featurecollection(feature_collection):
    from rescape_graphene import ramda as R
    return GeometryCollection(tuple(R.map(geometry_from_feature, feature_collection)))
