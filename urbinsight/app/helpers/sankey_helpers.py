from rescape_graphene import ramda as R


def stages_by_name(stages):
    return R.map_prop_value_as_index('name', stages)


def aberrate_location(index, location, factor=.005):
    """
       Minutely move locations so they don't overlap
    :param index: a counter to help with the aberration. Increment before calling each time
    :param location: Simple point location (two item array) of lat lon value
    :param factor: Sensitivity of aberration, defaults to .005
    :return:
    """
    return [coord + factor * (-index if index % 2 else index) * (i or -1) for coord, i in enumerate(location)]


def create_raw_nodes(columns):
    """
        Creates nodes for each column from the csv
    :param columns:
    :return:
    """
    return R.map(
        lambda line: R.from_pairs(
            zip(*
                columns,
                ';'.split(line)
                )
        )
    )


def resolve_location(default_location, coordinates, i):
    """
        Resolves the lat/lon based on the given coordinates string. If it is NA then default to BRUSSELS_LOCATION
    :param default_location: [lat, lon] representing the default location for coordinates marked 'NA'
    :param coordinates: comma separated lon/lat. We flip this since the software wants [lat, lon]
    :param i: Current index of coordinates, used for aberration
    :return: lat/lon array
    """
    if coordinates == 'NA':
        return dict(
            is_generalized=True,
            location=aberrate_location(i, default_location)
        )
    else:
        return dict(
            is_generalized=False,
            location=reversed(R.map(lambda coord: float(coord), ','.split(coordinates)))
        )


def create_links(stages, value_key, nodes_by_stages):
    """
    Creates Sankey Links for the given ordered stages for the given nodes by stage
    :param [Object] stages Array of stage objects.
    :param {String} The value_key
    :param [Object] nodesByStages Keyed by stage key and valued by an array of nodes
    :return {*}
    """

    def process_stage(stage, i):
        # Get the current stage as the source
        sources = nodes_by_stages[stage.key]
        if not sources:
            return []
        # Iterate through the stages until one with nodes is found
        target_stage = R.find(
            lambda stage: nodes_by_stages[stage.key],
            stages[i + 1, R.length(stages)]
        )
        # If no more stages contain nodes, we're done
        if not target_stage:
            return []
        targets = nodes_by_stages[target_stage.key]
        return R.chain(lambda source:
                       R.map(lambda target:
                             dict(
                                 source=source.index,
                                 target=target.index,
                                 value=float(R.prop(value_key, source))
                             ),
                             targets),
                       sources
                       )

    return [process_stage(stage, i) for stage, i in enumerate(stages)]


def generate_sankey_data(resource):
    """
        Generates nodes and links for the given Resrouce object
    :param resource:  Resource object
    :return: A dict containing nodes and links. nodes are a dict key by stage name
        Results can be assigned to resource.data.sankey and saved
    """

    settings = resource.settings
    stages = settings.stages
    stage_key = settings.stage_key
    value_key = settings.value_key
    node_name_key = settings.node_name_key
    default_location = settings.default_location
    # A dct of stages by name
    stage_by_name = stages_by_name(stages)

    def accumulate_nodes(accum, node, i):
        """
            Accumulate each node, keying by the name of the node's stage key
            Since nodes share stage keys these each result is an array of nodes
        :param accum:
        :param node:
        :param i:
        :return:
        """
        location_obj = resolve_location(default_location, node.coordinates, i)
        location = R.prop('location', location_obj)
        is_generalized = R.prop('is_generalized', location_obj)
        # The key where then node is stored is the stage key
        key = stage_by_name[node[stage_key]].key

        return R.merge(
            # Omit accum[key] since we'll concat it with the new node
            R.omit([key], accum),
            {
                # concat accum[key] or [] with the new node
                key: R.concat(
                    R.prop_or([], key, accum),
                    [{
                        # Note that the value is an array so we can combine nodes with the same stage key
                        stage_by_name[node[stage_key]].key: [
                            R.merge(
                                node,
                                dict(
                                    material=resource.material,
                                    value=float(node[value_key]),
                                    type='Feature',
                                    geometry=dict(
                                        type='Point',
                                        coordinates=location
                                    ),
                                    name=node[node_name_key],
                                    is_generalized=is_generalized,
                                    properties={}
                                )
                            )]
                    }]
                )
            }
        )

    # Reduce the nodes
    nodes_by_stage = R.reduce(
        lambda accum, node_and_i: accumulate_nodes(accum, node_and_i[0], node_and_i[1]),
        {},
        enumerate(resource.nodes)
    )
    return dict(
        nodes=nodes_by_stage,
        links=create_links(stages, value_key, nodes_by_stage)
    )


def accumulate_sankey_graph_from_rsource(accumulated_graph, resource):
    """
        Same as accumulate_sankey_graph but extracts the resource's sankey graph
    :param accumulated_graph:
    :param resource:
    :return:
    """
    return accumulate_sankey_graph(
        accumulated_graph,
        R.item_path(['settings', 'sankey'], resource)
    )


def accumulate_sankey_graph(accumulated_graph, graph):
    """
        Given an accumulated graph, a dict of nodes and links
        and a current Resource object, process the resource object and add the results to the accumulated graph
    :param accumulated_graph:
    :param nodes_by_stage: Dict of nodes by stage key. Each stage contains an array of nodes
    :return:
    """
    nodes_by_stage = R.prop('nodes', graph)
    links = R.prop('links', graph)

    # Combine the nodes and link with previous accumulated_graph nodes and links
    return dict(
        nodes=R.concat(R.prop_or([], 'nodes', accumulated_graph), R.flatten(R.values(nodes_by_stage))),
        # Naively create a link between every node of consecutive stages
        links=R.concat(R.prop_or([], 'links', accumulated_graph), links)
    )


def index_sankey_graph(graph):
    """
        Once all nodes are generated for a sankey graph the nodes need indices. This updates each node with
        and index property
    :param graph:
    :return: Updates graph.nodes, adding an index to each
    """
    for (node, i) in enumerate(graph.nodes):
        node['index'] = i


def process_sankey_data(resources):
    """
        Given Sankey data process it into Sankey graph data
    :param resources: Resource instances
    :return:
    """
    return R.reduce(
        accumulate_sankey_graph,
        dict(nodes=[], links=[]),
        resources
    )
