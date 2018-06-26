import logging

import rescape_graphene.ramda as R
from graphene.test import Client
from snapshottest import TestCase
from sop.webapp.models import DataPoint
from sop.sop_api.schema import schema
from sop.sop_api.schema_models.data_point_sample import OAKLAND_SAMPLE_DATA, OSLO_SAMPLE_DATA
from sop.sop_api.schema_models.data_point_schema import graphql_query_data_points, graphql_update_or_create_data_point, \
    data_point_fields
from sop.sop_api.schema_models.data_schema import data_fields

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
omit_props = ['date', 'time']


class DataPointTestCase(TestCase):
    client = None

    def setUp(self):
        self.client = Client(schema)
        DataPoint.objects.update_or_create(
            defaults=dict(
                version=DataPoint.VERSIONS['IMI2'],
                data=OAKLAND_SAMPLE_DATA
            ),
            country='USA', state='California', city='Oakland',
            neighborhood='Adams Pt', blockname='Grand Ave', intersc1='Bay Pl', intersc2='Park View Terrace',
        )
        (dp, created) = DataPoint.objects.update_or_create(
            defaults=dict(
                version=DataPoint.VERSIONS['IMI2'],
                data=OSLO_SAMPLE_DATA
            ),
            country='Norway', state='', city='Oslo',
            # This has to be here to prevent a duplicate with the scenario data_point below the second time
            # setUp is run
            original=True,
            neighborhood='Grunerlokke', blockname='Thorvold Mayers gate', intersc1='Korsgata', intersc2='Nordre gate',
        )
        DataPoint.objects.update_or_create(
            country='Norway', state='', city='Oslo',
            neighborhood='Grunerlokke', blockname='Thorvold Mayers gate', intersc1='Korsgata', intersc2='Nordre gate',
            version=DataPoint.VERSIONS['IMI2'],
            data=OSLO_SAMPLE_DATA,
            original=False,
            original_data_point_id=dp.id
        )

    def test_query(self):
        result = graphql_query_data_points(self.client, params=dict(city='Oakland'))
        # Check against errors
        assert not R.has('errors', result), R.dump_json(R.prop('errors', result))
        # Visual assertion that the query looks good
        self.assertMatchSnapshot(R.map(R.omit(omit_props), R.item_path(['data', 'dataPoints'], result)))

    def test_create(self):
        values = dict(
            country='USA', state='California', city='San Francisco',
            neighborhood='Tenderloin', blockname='Maiden Lane', intersc1='Stockton St', intersc2='Grant Ave',
            version=DataPoint.VERSIONS['IMI2'],
            #data=OAKLAND_SAMPLE_DATA
        )
        result = graphql_update_or_create_data_point(self.client, values)
        assert not R.has('errors', result), R.dump_json(R.prop('errors', result))
        # look at the users added and omit the non-determinant dateJoined
        self.assertMatchSnapshot(R.omit(omit_props, R.item_path(['data', 'createDataPoint', 'user'], result)))

    def test_create_scenario_data_point(self):
        # variable_value={'user': 'Peter'}
        original_result = graphql_query_data_points(
            self.client,
            dict(city='String'),
            field_overrides=R.merge_deep(
                R.omit(['data'], data_point_fields),
                dict(original_data_point=dict(fields=R.pick(['id'], data_fields)))
            ),
            variable_values=dict(city='Oakland'))
        id = int(R.item_path(['data', 'dataPoints', 0, 'id'], original_result))
        values = dict(
            # TODO none of this stuff should be specified for a scenario besides the original_data_point. It should
            # use the original_data_point info
            country='Norway', city='Oslo',
            neighborhood='Grunerlokke', blockname='Maiden Lane', intersc1='Stockton St', intersc2='Grant Ave',
            version=DataPoint.VERSIONS['IMI2'],
            data=OAKLAND_SAMPLE_DATA,
            original_data_point=dict(
                id=id
            )
        )
        result = graphql_update_or_create_data_point(self.client, values)
        assert not R.has('errors', result), R.dump_json(R.prop('errors', result))
        # look at the users added and omit the non-determinant dateJoined
        self.assertMatchSnapshot(R.omit(omit_props, R.item_path(['data', 'createDataPoint', 'user'], result)))

    def test_update(self):
        values = dict(
            country='USA', state='California', city='San Francisco',
            neighborhood='Tenderloin', blockname='Maiden Lane', intersc1='Stockton St', intersc2='Grant Ave',
            version=DataPoint.VERSIONS['IMI2'],
            data=OAKLAND_SAMPLE_DATA
        )

        # Here is our create
        create_result = graphql_update_or_create_data_point(self.client, values)
        assert not R.has('errors', create_result), R.dump_json(R.prop('errors', create_result))

        # Unfortunately Graphene returns the ID as a string, even when its an int
        id = int(R.prop('id', R.item_path(['data', 'createDataPoint', 'data_point'], create_result)))

        # Here is our update
        result = graphql_update_or_create_data_point(
            self.client,
            dict(id=id, blockname='Maiden Ln', data=R.merge(create_result.data, dict(Alley=1)))
        )
        # Check against errors
        assert not R.has('errors', result), R.dump_json(R.prop('errors', result))
        self.assertMatchSnapshot(R.omit(omit_props, R.item_path(['data', 'updateDataPoint', 'data_pint'], result)))

    # def test_delete(self):
    #     self.assertMatchSnapshot(self.client.execute('''{
    #         data_points {
    #             username,
    #             first_name,
    #             last_name,
    #             password
    #         }
    #     }'''))
