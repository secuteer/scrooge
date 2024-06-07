from src.entity.Request import StaticRequest, AsyncRequest
from src.entity.Snapshot import Snapshot
from src.entity.Comparator import Comparator, JaccardComparator, ParamComperator, \
    AsyncRequestsComparator, DHashComparator, AsyncStructureComparator, PagePresenceComparator
from src.schema.json_schema import create_request_json_schema, create_content_json_schema
from src.entity.TreeComparator import TreeComparator
from src.shared.helpers import find_by_identifier, get_unique_identifier, is_relevant, is_static, \
    is_async

import os
import json

def parse_har_to_snapshot(name: str, snapshot_directory: str) -> Snapshot:
    """
    Parse HAR to Snapshot.

    This method parses a HAR (HTTP Archive) file and converts it into a Snapshot object.

    Parameters:
    - name (str): The name of the HAR file (without the extension).
    - snapshot_directory (str): The directory where the HAR file and associated files are located.

    Returns:
    - Snapshot: The parsed snapshot object.

    Example Usage:
        snapshot = parse_har_to_snapshot('example', '/path/to/snapshot')

    """
    with open(os.path.join(snapshot_directory, name + '.har'), 'r') as f:
        data = json.load(f)

    with open(os.path.join(snapshot_directory, name + '.domain.txt'), 'r') as f:
        base_url = f.read()

    snapshot = Snapshot(base_url=base_url)
    current_static_request: StaticRequest = StaticRequest()
    current_static_request.identifier = 'Root'
    for entry in data['log']['entries']:
        if is_relevant(entry, base_url):
            if is_async(entry):
                print('async request')
                identifier = get_unique_identifier(entry, base_url)
                request = find_by_identifier(current_static_request.async_requests, identifier)
                if not request:
                    request = AsyncRequest()
                    request.har = entry
                    request.paramSchema = create_request_json_schema(entry)
                    request.responseSchema = create_content_json_schema(entry)
                    request.content = entry['response']['content']['text']
                    request.identifier = identifier
                else:
                    request.merge_counter += 1
                if not find_by_identifier(current_static_request.async_requests, identifier):
                    current_static_request.async_requests.append(request)

            if is_static(entry):
                print('static request')
                identifier = get_unique_identifier(entry, base_url)
                request = find_by_identifier(snapshot.static_requests, identifier)
                if not request:
                    request = StaticRequest()
                    request.har = entry
                    request.paramSchema = create_request_json_schema(entry)
                    request.identifier = identifier
                    if 'text' in entry['response']['content']:
                        request.content = entry['response']['content']['text']
                    snapshot.static_requests.append(request)
                else:
                    request.merge_counter += 1
                if current_static_request and not find_by_identifier(request.previous_requests, current_static_request.identifier):
                    request.previous_requests.append(current_static_request)

                current_static_request = request
    return snapshot

def compare_snapshots(snap1: Snapshot, snap2: Snapshot, compare_name: str):
    """

    Compare Snapshots

    Compares two Snapshots using multiple Comparators and checks the similarity of various components.

    Parameters:
    snap1 (Snapshot): The first Snapshot to be compared.
    snap2 (Snapshot): The second Snapshot to be compared.
    compare_name (str): Name for the comparison

    Returns:
    None

    Examples:
    compare_snapshots(snap1, snap2, "example_comparison")

    """
    comparators:[Comparator] = []
    comparators.append(AsyncRequestsComparator(snap1, snap2))
    comparators.append(JaccardComparator(snap1, snap2))
    comparators.append(TreeComparator(snap1, snap2))
    comparators.append(ParamComperator(snap1, snap2))
    comparators.append(DHashComparator(snap1, snap2, f'./reports/screenshots/{compare_name}/'))
    comparators.append(AsyncStructureComparator(snap1, snap2))
    comparators.append(PagePresenceComparator(snap1, snap2))

    for static_request in snap1.static_requests:
        print('processing', static_request.identifier)
        for comparator in comparators:
            comparator.check_similarity(static_request.identifier)

    for comparator in comparators:
        comparator.check_similarity_global()