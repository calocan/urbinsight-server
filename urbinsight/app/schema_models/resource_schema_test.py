import logging

from rescape_graphene import ramda as R
from app.helpers.sankey_helpers import generate_sankey_data, index_sankey_graph, accumulate_sankey_graph, \
    create_sankey_graph_from_resources
from graphene.test import Client
from snapshottest import TestCase
from app.models import Resource
from app.schema import schema
from .resource_sample import sample_resources, sample_settings
from .resource_schema import resource_fields, graphql_query_resources, graphql_update_or_create_resource
from .data_schema import resource_data_fields

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
omit_props = ['created', 'updated']


class ResourceSchemaTestCase(TestCase):
    client = None

    def setUp(self):
        self.client = Client(schema)

        def create_resource(resource_dict):
            # Generate our sample resources, computing and storing their Sankey graph data
            graph = generate_sankey_data(resource_dict)
            data = R.merge(
                R.prop('data', resource_dict),
                dict(
                    graph=graph
                )
            )
            # Save the resource with the complete dataa
            resource = Resource(**R.merge(resource_dict, dict(data=data)))
            resource.save()
            return resource

        Resource.objects.all().delete()
        # Convert all sample resource dicts to persisted Resource instances
        resources = R.map(create_resource, sample_resources)
        # Create a graph for all resources
        graph = create_sankey_graph_from_resources(resources)

    def test_query(self):
        all_result = graphql_query_resources(self.client)
        assert not R.has('errors', all_result), R.dump_json(R.prop('errors', all_result))
        result = graphql_query_resources(self.client, dict(name='String'), variable_values=dict(name='Minerals'))
        # Check against errors
        assert not R.has('errors', result), R.dump_json(R.prop('errors', result))
        # Visual assertion that the query looks good
        assert 1 == R.length(R.item_path(['data', 'resources'], result))

    def test_create(self):
        values = dict(
            name='Candy',
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
        result = graphql_update_or_create_resource(self.client, values)
        assert not R.has('errors', result), R.dump_json(R.prop('errors', result))
        # look at the users added and omit the non-determinant dateJoined
        self.assertMatchSnapshot(R.omit(omit_props, R.item_path(['data', 'createResource'], result)))

    # def test_create_scenario_resource(self):
    #     # variable_value={'user': 'Peter'}
    #     original_result = graphql_query_resources(
    #         self.client,
    #         dict(city='String'),
    #         field_overrides=R.merge_deep(
    #             R.omit(['data'], resource_fields),
    #             dict(original_resource=dict(fields=R.pick(['id'], data_fields)))
    #         ),
    #         variable_values=dict(city='Oakland'))
    #     id = int(R.item_path(['data', 'dataPoints', 0, 'id'], original_result))
    #     values = dict(
    #         # TODO none of this stuff should be specified for a scenario besides the original_resource. It should
    #         # use the original_resource info
    #         country='Norway', city='Oslo',
    #         neighborhood='Grunerlokke', blockname='Maiden Lane', intersc1='Stockton St', intersc2='Grant Ave',
    #         version=Resource.VERSIONS['IMI2'],
    #         data=OAKLAND_SAMPLE_DATA,
    #         original_resource=dict(
    #             id=id
    #         )
    #     )
    #     result = graphql_update_or_create_resource(self.client, values)
    #     assert not R.has('errors', result), R.dump_json(R.prop('errors', result))
    #     # look at the users added and omit the non-determinant dateJoined
    #     self.assertMatchSnapshot(R.omit(omit_props, R.item_path(['data', 'createResource', 'user'], result)))
    #
    # def test_update(self):
    #     values = dict(
    #         country='USA', state='California', city='San Francisco',
    #         neighborhood='Tenderloin', blockname='Maiden Lane', intersc1='Stockton St', intersc2='Grant Ave',
    #         version=Resource.VERSIONS['IMI2'],
    #         data=OAKLAND_SAMPLE_DATA
    #     )
    #
    #     # Here is our create
    #     create_result = graphql_update_or_create_resource(self.client, values)
    #     assert not R.has('errors', create_result), R.dump_json(R.prop('errors', create_result))
    #
    #     # Unfortunately Graphene returns the ID as a string, even when its an int
    #     id = int(R.prop('id', R.item_path(['data', 'createResource', 'resource'], create_result)))
    #
    #     # Here is our update
    #     result = graphql_update_or_create_resource(
    #         self.client,
    #         dict(id=id, blockname='Maiden Ln', data=R.merge(create_result.data, dict(Alley=1)))
    #     )
    #     # Check against errors
    #     assert not R.has('errors', result), R.dump_json(R.prop('errors', result))
    #     self.assertMatchSnapshot(R.omit(omit_props, R.item_path(['data', 'updateResource', 'data_pint'], result)))

    # def test_delete(self):
    #     self.assertMatchSnapshot(self.client.execute('''{
    #         resources {
    #             username,
    #             first_name,
    #             last_name,
    #             password
    #         }
    #     }'''))
