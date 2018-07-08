import logging

from rescape_graphene import ramda as R
from app.helpers.geometry_helpers import ewkt_from_feature
from django.db import transaction
from app.models import Region, Feature

from .region_schema import graphql_query_regions, graphql_update_or_create_region

from graphene.test import Client
from snapshottest import TestCase

from app.schema import schema
from .region_sample import sample_regions, create_region

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
omit_props = ['created', 'updated']


class RegionSchemaTestCase(TestCase):
    client = None

    def setUp(self):
        self.client = Client(schema)

        Region.objects.all().delete()
        # Convert all sample region dicts to persisted Region instances
        regions = R.map(create_region, sample_regions)

    def test_query(self):
        all_result = graphql_query_regions(self.client)
        assert not R.has('errors', all_result), R.dump_json(R.prop('errors', all_result))
        result = graphql_query_regions(self.client, dict(name='String'), variable_values=dict(name='Belgium'))
        # Check against errors
        assert not R.has('errors', result), R.dump_json(R.prop('errors', result))
        # Visual assertion that the query looks good
        assert 1 == R.length(R.item_path(['data', 'regions'], result))

    def test_create(self):
        values = dict(
            name='Luxembourg',
            key='luxembourg',
            boundary=dict(
                type="Feature",
                geometry=dict(
                    type="Polygon",
                    coordinates=[
                        [[49.4426671413, 5.67405195478], [50.1280516628, 5.67405195478], [50.1280516628, 6.24275109216],
                         [49.4426671413, 6.24275109216], [49.4426671413, 5.67405195478]]]
                )
            ),
            data=dict()
        )
        result = graphql_update_or_create_region(self.client, values)
        assert not R.has('errors', result), R.dump_json(R.prop('errors', result))
        # look at the users added and omit the non-determinant dateJoined
        self.assertMatchSnapshot(R.omit(omit_props, R.item_path(['data', 'createRegion'], result)))

    # def test_create_scenario_region(self):
    #     # variable_value={'user': 'Peter'}
    #     original_result = graphql_query_regions(
    #         self.client,
    #         dict(city='String'),
    #         field_overrides=R.merge_deep(
    #             R.omit(['data'], region_fields),
    #             dict(original_region=dict(fields=R.pick(['id'], data_fields)))
    #         ),
    #         variable_values=dict(city='Oakland'))
    #     id = int(R.item_path(['data', 'dataPoints', 0, 'id'], original_result))
    #     values = dict(
    #         # TODO none of this stuff should be specified for a scenario besides the original_region. It should
    #         # use the original_region info
    #         country='Norway', city='Oslo',
    #         neighborhood='Grunerlokke', blockname='Maiden Lane', intersc1='Stockton St', intersc2='Grant Ave',
    #         version=Region.VERSIONS['IMI2'],
    #         data=OAKLAND_SAMPLE_DATA,
    #         original_region=dict(
    #             id=id
    #         )
    #     )
    #     result = graphql_update_or_create_region(self.client, values)
    #     assert not R.has('errors', result), R.dump_json(R.prop('errors', result))
    #     # look at the users added and omit the non-determinant dateJoined
    #     self.assertMatchSnapshot(R.omit(omit_props, R.item_path(['data', 'createRegion', 'user'], result)))
    #
    # def test_update(self):
    #     values = dict(
    #         country='USA', state='California', city='San Francisco',
    #         neighborhood='Tenderloin', blockname='Maiden Lane', intersc1='Stockton St', intersc2='Grant Ave',
    #         version=Region.VERSIONS['IMI2'],
    #         data=OAKLAND_SAMPLE_DATA
    #     )
    #
    #     # Here is our create
    #     create_result = graphql_update_or_create_region(self.client, values)
    #     assert not R.has('errors', create_result), R.dump_json(R.prop('errors', create_result))
    #
    #     # Unfortunately Graphene returns the ID as a string, even when its an int
    #     id = int(R.prop('id', R.item_path(['data', 'createRegion', 'region'], create_result)))
    #
    #     # Here is our update
    #     result = graphql_update_or_create_region(
    #         self.client,
    #         dict(id=id, blockname='Maiden Ln', data=R.merge(create_result.data, dict(Alley=1)))
    #     )
    #     # Check against errors
    #     assert not R.has('errors', result), R.dump_json(R.prop('errors', result))
    #     self.assertMatchSnapshot(R.omit(omit_props, R.item_path(['data', 'updateRegion', 'data_pint'], result)))

    # def test_delete(self):
    #     self.assertMatchSnapshot(self.client.execute('''{
    #         regions {
    #             username,
    #             first_name,
    #             last_name,
    #             password
    #         }
    #     }'''))
