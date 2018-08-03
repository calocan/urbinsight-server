import logging

from app.schema.schema import dump_errors, schema
from rescape_graphene import ramda as R
from graphene.test import Client
from snapshottest import TestCase
from .user_state_sample import sample_settings, delete_sample_user_states, create_sample_user_states
from .user_state_schema import graphql_query_user_states, graphql_update_or_create_user_state

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
omit_props = ['created', 'updated']


class UserStateSchemaTestCase(TestCase):
    client = None
    region = None
    user_state = None

    def setUp(self):
        self.client = Client(schema)
        delete_sample_user_states()
        self.user_states = create_sample_user_states()
        # Gather all unique sample users
        self.users = list(set(R.map(
            lambda user_state: user_state.user,
            self.user_states
        )))
        # Gather all unique sample regions
        self.regions = list(set(R.chain(
            lambda user_state: R.item_str_path('data.regions', user_state),
            self.user_states
        )))

    def test_query(self):
        all_results = graphql_query_user_states(self.client)
        assert not R.has('errors', all_results), R.dump_json(R.prop('errors', all_results))
        # Make sure that we can filter
        results = graphql_query_user_states(self.client,
                                            dict(user_id='Integer'),
                                            variable_values=dict(user_id=self.users[0].id))
        # Check against errors
        assert not R.has('errors', results), R.dump_json(R.prop('errors', results))
        assert 1 == R.length(R.item_path(['data', 'user_states'], results))

    def test_create(self):
        values = dict(
            name='Candy',
            region=dict(id=R.head(self.regions).id),
            data=R.merge(
                sample_settings,
                dict(
                    material='Candy',
                    raw_data=[
                        'Other Global Imports;Shipments, location generalized;51.309933, 3.055030;Source;22,469,843',
                        'Knauf (Danilith) BE;Waregemseweg 156-142 9790 Wortegem-Petegem, Belgium;50.864762, 3.479308;Conversion;657,245',
                        "MPRO Bruxelles;Avenue du Port 67 1000 Bruxelles, Belgium;50.867486, 4.352543;Distribution;18,632",
                        'Residential Buildings (all typologies);Everywhere in Brussels;NA;Demand;3,882,735',
                        'Duplex House Typology;Everywhere in Brussels;NA;Demand;13,544',
                        'Apartment Building Typology;Everywhere in Brussels;NA;Demand;34,643',
                        'New West Gypsum Recycling;9130 Beveren, Sint-Jansweg 9 Haven 1602, Kallo, Belgium;51.270229, 4.261048;Reconversion;87,565',
                        'Residential Buildings (all typologies);Everywhere in Brussels;NA;Sink;120,000',
                        'RecyPark South;1190 Forest, Belgium;50.810799, 4.314789;Sink;3,130',
                        'RecyPark Nord;Rue du Rupel, 1000 Bruxelles, Belgium;50.880181, 4.377136;Sink;1,162'
                    ]
                )
            )
        )
        result = graphql_update_or_create_user_state(self.client, values)
        dump_errors(result)
        assert not R.has('errors', result), R.dump_json(R.prop('errors', result))
        # look at the users added and omit the non-determinant dateJoined
        result_path_partial = R.item_path(['data', 'createUserState', 'user_state'])
        self.assertMatchSnapshot(R.omit(omit_props, result_path_partial(result)))

    def test_update(self):
        values = dict(
            name='Candy',
            region=dict(id=R.head(self.regions).id),
            data=R.merge(
                sample_settings,
                dict(
                    material='Candy',
                    raw_data=[
                        'Other Global Imports;Shipments, location generalized;51.309933, 3.055030;Source;22,469,843',
                        'Knauf (Danilith) BE;Waregemseweg 156-142 9790 Wortegem-Petegem, Belgium;50.864762, 3.479308;Conversion;657,245',
                        "MPRO Bruxelles;Avenue du Port 67 1000 Bruxelles, Belgium;50.867486, 4.352543;Distribution;18,632",
                        'Residential Buildings (all typologies);Everywhere in Brussels;NA;Demand;3,882,735',
                        'Duplex House Typology;Everywhere in Brussels;NA;Demand;13,544',
                        'Apartment Building Typology;Everywhere in Brussels;NA;Demand;34,643',
                        'New West Gypsum Recycling;9130 Beveren, Sint-Jansweg 9 Haven 1602, Kallo, Belgium;51.270229, 4.261048;Reconversion;87,565',
                        'Residential Buildings (all typologies);Everywhere in Brussels;NA;Sink;120,000',
                        'RecyPark South;1190 Forest, Belgium;50.810799, 4.314789;Sink;3,130',
                        'RecyPark Nord;Rue du Rupel, 1000 Bruxelles, Belgium;50.880181, 4.377136;Sink;1,162'
                    ]
                )
            )
        )
        create_raw = graphql_update_or_create_user_state(self.client, values)
        dump_errors(create_raw)
        assert not R.has('errors', create_raw), R.dump_json(R.prop('errors', create_raw))
        result_path_partial = R.item_path(['data', 'createUserState', 'user_state'])
        create_result = result_path_partial(create_raw)

        update_raw = graphql_update_or_create_user_state(self.client, R.merge(values, dict(name='Popcorn', id=int(create_result['id']))))
        dump_errors(update_raw)
        assert not R.has('errors', update_raw), R.dump_json(R.prop('errors', update_raw))
        result_path_partial = R.item_path(['data', 'updateUserState', 'user_state'])
        update_result = result_path_partial(update_raw)
        # Assert same instance
        assert update_result['id'] == create_result['id']
        # Assert the name updated
        assert update_result['name'] == 'Popcorn'

    # def test_delete(self):
    #     self.assertMatchSnapshot(self.client.execute('''{
    #         user_states {
    #             username,
    #             first_name,
    #             last_name,
    #             password
    #         }
    #     }'''))
