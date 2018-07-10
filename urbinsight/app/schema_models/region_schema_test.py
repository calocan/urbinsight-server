import logging

from app.schema_models.user_sample import sample_users, create_user
from django.contrib.auth import get_user_model
from rescape_graphene import ramda as R
from app.helpers.geometry_helpers import ewkt_from_feature
from django.db import transaction
from app.models import Region, Feature

from .region_schema import graphql_query_regions, graphql_update_or_create_region

from graphene.test import Client
from snapshottest import TestCase

from app.schema import schema
from .region_sample import sample_regions, create_sample_region, create_sample_regions

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
omit_props = ['createdAt', 'updatedAt']


class RegionSchemaTestCase(TestCase):
    client = None

    def setUp(self):
        self.client = Client(schema)
        self.regions = create_sample_regions()
        self.users = list(set(map(lambda region: region.owner, self.regions)))

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
                geometry=dict(
                    type="Polygon",
                    coordinates=[
                        [[49.4426671413, 5.67405195478], [50.1280516628, 5.67405195478], [50.1280516628, 6.24275109216],
                         [49.4426671413, 6.24275109216], [49.4426671413, 5.67405195478]]]
                )
            ),
            data=dict(),
            owner=dict(id=R.head(self.users).id)
        )
        result = graphql_update_or_create_region(self.client, values)
        result_path_partial = R.item_path(['data', 'createRegion', 'region'])
        assert not R.has('errors', result), R.dump_json(R.prop('errors', result))
        created = result_path_partial(result)
        # look at the users added and omit the non-determinant dateJoined
        self.assertMatchSnapshot(R.omit_deep(omit_props, created))
        # Try creating the same resource again, because of the unique contraint on key and the unique_with property
        # on its field definition value, it will increment to luxembourg1
        new_result = graphql_update_or_create_region(self.client, values)
        assert not R.has('errors', new_result), R.dump_json(R.prop('errors', new_result))
        created_too = result_path_partial(new_result)
        assert created['id'] != created_too['id']
        assert created_too['key'] == 'luxembourg1'

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
