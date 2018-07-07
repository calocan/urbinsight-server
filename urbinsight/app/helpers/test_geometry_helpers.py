import ast
from unittest import TestCase

from app.helpers.geometry_helpers import geometrycollection_from_featurecollection
from django.contrib.gis.geos import GeometryCollection, GEOSGeometry

fc = { "type": "FeatureCollection",
"features": [
  { "type": "Feature",
    "geometry": {"type": "Point", "coordinates": [102.0, 0.5]},
    "properties": {"prop0": "value0"}
    },
  { "type": "Feature",
    "geometry": {
      "type": "LineString",
      "coordinates": [
        [102.0, 0.0], [103.0, 1.0], [104.0, 0.0], [105.0, 1.0]
        ]
      },
    "properties": {
      "prop0": "value0",
      "prop1": 0.0
      }
    },
  { "type": "Feature",
     "geometry": {
       "type": "Polygon",
       "coordinates": [
         [ [100.0, 0.0], [101.0, 0.0], [101.0, 1.0],
           [100.0, 1.0], [100.0, 0.0] ]
         ]
     },
     "properties": {
       "prop0": "value0",
       "prop1": {"this": "that"}
       }
     }
   ]
 }

class GeometryHelpersTestCase(TestCase):
    client = None

    def test_geometrycollection_from_feature(self):
        assert self.assertMatchSnapshot(geometrycollection_from_featurecollection(fc))