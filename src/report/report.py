from src.entity.Request import AsyncRequest
from src.entity.Snapshot import Snapshot
from src.shared.helpers import is_change_in_request
from src.entity.Change import NewRequestChange, MissingRequestChange


def generate_report(snapshot: Snapshot, snapshot2: Snapshot, filename: str = ''):
    """
    Generates a report based on two snapshot objects and writes it to a file if a filename is provided.

    Parameters:
    - snapshot (Snapshot): The first snapshot object
    - snapshot2 (Snapshot): The second snapshot object
    - filename (str, optional): The filename to write the report to (default is an empty string)

    Returns:
    - str: The generated report

    """
    report = ''
    report += f'========= Snapshot 1 =========\n'
    for static_request in snapshot.static_requests:
        if len(static_request.changes):
            report += print_request_changes(static_request)
        for async_request in static_request.async_requests:
            if len(async_request.changes):
                report += print_request_changes(async_request)

    report_snapshot2 = ''
    report_snapshot2 += f'\n========= Snapshot 2 =========\n'

    for static_request in snapshot2.static_requests:
        if is_change_in_request(static_request, NewRequestChange):
            report_snapshot2 += print_request_changes(static_request)

        for async_request in static_request.async_requests:
            if is_change_in_request(async_request, NewRequestChange):
                report_snapshot2 += print_request_changes(async_request)

    if report == '':
        report = 'No changes found'

    if not report_snapshot2 == '':
        report += report_snapshot2

    if filename:
        file = open(filename, 'w')
        file.write(report)
        file.close()
    return report

def list_requests(snapshot: Snapshot, filename: str = ''):
    """
    Generates a report of requests from a given snapshot.

    Parameters:
    - snapshot (Snapshot): The snapshot object containing the requests.
    - filename (str, optional): The filename to save the report. If provided, the report will be saved to the file.

    Returns:
    - report (str): The generated report.

    """
    report = 'METHOD; IDENTIFIER; REQUEST TYPE\n'
    split_identifier = ''
    count = 0
    for static_request in snapshot.static_requests:
        count+=1
        identifier = static_request.identifier.replace('&amp;', '&')
        if 'POST' in identifier:
            split_identifier = identifier.replace('POST', 'POST; ')
        if 'GET' in identifier:
            split_identifier = identifier.replace('GET', 'GET; ')
        report += split_identifier + '; static\n'
        for async_request in static_request.async_requests:
            count+=1
            identifier = async_request.identifier
            if 'POST' in identifier:
                split_identifier = identifier.replace('POST', 'POST; ')
            if 'GET' in identifier:
                split_identifier = identifier.replace('GET', 'GET; ')
            report += '\t' + split_identifier + '; async\n'
    report += 'Count: ' + str(count)
    if filename:
        file = open(filename + '.csv', 'w')
        file.write(report)
        file.close()
    return report


def print_request_changes(request):
    """
    Print the changes made in a request.

    Parameters:
    - request: The request object to print the changes for.

    Returns:
    - report: A string containing the formatted report of the changes made in the request.

    """
    report = ''
    t = 'Static'
    if type(request) is AsyncRequest:
        t = 'Async'

    report += f"{t} URL: {request.identifier.replace('&amp;', '&')}\n"
    #report += f"\n"
    for change in request.changes:
        report += f"{change}"
        if change.__class__.show_score:
            report += f" ({change.get_score()})"

        reformatted_notice = change.notice
        if type(reformatted_notice) is str:
            reformatted_notice = '\n\t'.join(change.notice.split('\n'))
        report += f": {reformatted_notice}\n"
    report += f"\n"
    report += f"\n"
    return report


