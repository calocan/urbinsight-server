import logging

import rescape_graphene.ramda as R
from app.helpers.sankey_helpers import generate_sankey_data
from graphene.test import Client
from snapshottest import TestCase
from app.models import Resource
from app.schema import schema
from .resource_sample import sample_resources
from .resource_schema import graphql_query_data_points, graphql_update_or_create_data_point, \
    resource_fields, graphql_query_resources, graphql_update_or_create_resource
from .data_schema import data_fields

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
omit_props = ['date', 'time']


class ResourceTestCase(TestCase):
    client = None

    def setUp(self):
        self.client = Client(schema)

        for resource in sample_resources:
            # Generate our sample resources, computing and storing their Sankey graph data
            graph = generate_sankey_data(resource)
            resource.data.graph = graph
            resource.save()

    def test_query(self):
        result = graphql_query_resources(self.client, params=dict(city='Oakland'))
        # Check against errors
        assert not R.has('errors', result), R.dump_json(R.prop('errors', result))
        # Visual assertion that the query looks good
        self.assertMatchSnapshot(R.map(R.omit(omit_props), R.item_path(['data', 'dataPoints'], result)))

    def test_create(self):
        values = dict(
            country='USA', state='California', city='San Francisco',
            neighborhood='Tenderloin', blockname='Maiden Lane', intersc1='Stockton St', intersc2='Grant Ave',
            version=Resource.VERSIONS['IMI2'],
            #data=OAKLAND_SAMPLE_DATA
        )
        result = graphql_update_or_create_resource(self.client, values)
        assert not R.has('errors', result), R.dump_json(R.prop('errors', result))
        # look at the users added and omit the non-determinant dateJoined
        self.assertMatchSnapshot(R.omit(omit_props, R.item_path(['data', 'createResource', 'user'], result)))

    def test_create_scenario_resource(self):
        # variable_value={'user': 'Peter'}
        original_result = graphql_query_resources(
            self.client,
            dict(city='String'),
            field_overrides=R.merge_deep(
                R.omit(['data'], resource_fields),
                dict(original_resource=dict(fields=R.pick(['id'], data_fields)))
            ),
            variable_values=dict(city='Oakland'))
        id = int(R.item_path(['data', 'dataPoints', 0, 'id'], original_result))
        values = dict(
            # TODO none of this stuff should be specified for a scenario besides the original_resource. It should
            # use the original_resource info
            country='Norway', city='Oslo',
            neighborhood='Grunerlokke', blockname='Maiden Lane', intersc1='Stockton St', intersc2='Grant Ave',
            version=Resource.VERSIONS['IMI2'],
            data=OAKLAND_SAMPLE_DATA,
            original_resource=dict(
                id=id
            )
        )
        result = graphql_update_or_create_resource(self.client, values)
        assert not R.has('errors', result), R.dump_json(R.prop('errors', result))
        # look at the users added and omit the non-determinant dateJoined
        self.assertMatchSnapshot(R.omit(omit_props, R.item_path(['data', 'createResource', 'user'], result)))

    def test_update(self):
        values = dict(
            country='USA', state='California', city='San Francisco',
            neighborhood='Tenderloin', blockname='Maiden Lane', intersc1='Stockton St', intersc2='Grant Ave',
            version=Resource.VERSIONS['IMI2'],
            data=OAKLAND_SAMPLE_DATA
        )

        # Here is our create
        create_result = graphql_update_or_create_resource(self.client, values)
        assert not R.has('errors', create_result), R.dump_json(R.prop('errors', create_result))

        # Unfortunately Graphene returns the ID as a string, even when its an int
        id = int(R.prop('id', R.item_path(['data', 'createResource', 'resource'], create_result)))

        # Here is our update
        result = graphql_update_or_create_resource(
            self.client,
            dict(id=id, blockname='Maiden Ln', data=R.merge(create_result.data, dict(Alley=1)))
        )
        # Check against errors
        assert not R.has('errors', result), R.dump_json(R.prop('errors', result))
        self.assertMatchSnapshot(R.omit(omit_props, R.item_path(['data', 'updateResource', 'data_pint'], result)))

    # def test_delete(self):
    #     self.assertMatchSnapshot(self.client.execute('''{
    #         resources {
    #             username,
    #             first_name,
    #             last_name,
    #             password
    #         }
    #     }'''))
