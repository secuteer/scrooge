import graphviz

from src.entity.Request import StaticRequest
from src.entity.Snapshot import Snapshot
from src.entity.Change import NewRequestChange, MissingRequestChange
from src.shared.helpers import find_by_identifier, is_change_in_request

change_treshold = 0.01

def render_snapshot(snapshot: Snapshot, snapshot2: Snapshot = None, name = 'compare'):
    """
    Render a snapshot graph using graphviz.

    Parameters:
    - snapshot: The original snapshot object.
    - snapshot2: An optional second snapshot object for comparison (default=None).
    - name: The name of the graph (default='compare').

    Returns: None

    Example:
    render_snapshot(snapshot, snapshot2, name='compare')
    """
    dot = graphviz.Digraph(name, node_attr={'shape': 'box'})

    for static_request in snapshot.static_requests:

        [node, color] = create_node(static_request)
        dot.node(str(static_request.id), node, color=color)

        for previous_request in static_request.previous_requests:
            dot.edge(str(previous_request.id), str(static_request.id))

        for async_request in static_request.async_requests:
            [node, color] = create_node(async_request)

            dot.node(str(async_request.id), node, style='dashed', color=color)
            dot.edge(str(static_request.id), str(async_request.id))

        if snapshot2:
            r2: StaticRequest = find_by_identifier(snapshot2.static_requests, static_request.identifier)
            if r2:
                for async_request in r2.async_requests:
                    if is_change_in_request(async_request, NewRequestChange):
                        [node, color] = create_node(async_request)
                        dot.node(str(async_request.id), node, style='dashed', color=color)
                        dot.edge(str(static_request.id), str(async_request.id))

    if snapshot2:
        for static_request in snapshot2.static_requests:

            if not is_change_in_request(static_request, NewRequestChange):
                continue

            [node, color] = create_node(static_request)
            dot.node(str(static_request.id) + '-snap2', node, color=color)

            for previous_request in static_request.previous_requests:
                previous_request = find_by_identifier(snapshot.static_requests, previous_request.identifier)
                if previous_request:
                    dot.edge(str(previous_request.id), str(static_request.id) + '-snap2')

            for next_request in snapshot2.static_requests:
                if static_request in next_request.previous_requests:
                    next_request = find_by_identifier(snapshot.static_requests, next_request.identifier)
                    if next_request:
                        dot.edge(str(static_request.id) + '-snap2', str(next_request.id))

    # doctest_mark_exe()
    dot = dot.unflatten(stagger=3)
    dot.render(directory='./reports/graphs', view=True)


def create_node(request):
    """
    Create Node

    This method takes a request object as input and creates a node for visual representation in a graph.

    Parameters:
    - request: A request object representing the request to be visualized.

    Returns:
    A list containing two elements:
    - node: A string representing the HTML code for the created node.
    - color: A string representing the color of the node.

    """
    color = 'black'
    node = '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0">'
    node = node + '<TR><TD COLSPAN="2">' + request.identifier + '</TD></TR>'

    if len(request.changes) > 0:
        for change in request.changes:
            if isinstance(change, MissingRequestChange):
                color = 'red'
            if isinstance(change, NewRequestChange):
                color = 'green'
            node = node + '<TR>'
            if change.__class__.show_score:
                node = node + '<TD>' + str(change) + '</TD><TD>' + str(change.get_score()) + '</TD>'
            else:
                node = node + '<TD COLSPAN="2">' + str(change) + '</TD>'
            node = node + '</TR>'

    if 'TABLE' in node:
        node = node + '</TABLE>>'

    return [node, color]