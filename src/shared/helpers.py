import cgi
import email
import io
from email import message_from_bytes
from typing import List
from src.entity.Request import Request
from src.entity.Change import Change
import html
from urllib.parse import parse_qs
from bs4 import BeautifulSoup
import json
import re



def find_by_identifier(requests: List[Request], identifier: str) -> Request | None:
    """
    Searches for a request in the given list of requests based on the provided identifier.

    Args:
        requests (List[Request]): The list of requests to search in.
        identifier (str): The identifier to be used for searching.

    Returns:
        Request | None: The found Request object if a matching identifier is found, or None if no match is found.

    """
    for request in requests:
        if request.identifier == identifier:
            return request
    return None


def get_unique_identifier(entry, base_url: str):
    """
    Creates an unique identifier for the given entry.

    Parameters:
    - entry: A dictionary representing an entry.
    - base_url: A string representing the base URL for the entry.

    Returns:
    - A unique identifier for the entry, using the entry's request method and URL.

    """
    url = entry['request']['url'].replace(base_url, '')

    url_base = url.split('?')[0]

    if len(url.split('?')) > 1:
        url_params = url.split('?')[1]

        params = url_params.split('&')
        param_names = []
        for param in params:
            if '=' in param:
                key, value = param.split('=')
                param_names.append(key)

        url = url_base + '?' + '&'.join(param_names)

    return entry['request']['method'] + html.escape(url)


def find_header_value(header_list, name):
    """
    Find the value of a header given its name in a list of header entries.

    Args:
        header_list (list): A list of header entries.
        name (str): The name of the header to search for.

    Returns:
        str: The value of the header, or None if the header is not found.
    """
    for header_entry in header_list:
        if header_entry['name'].lower() == name.lower():
            return header_entry['value']
    return None


def is_relevant(entry, base_url: str):
    """
    Checks if a given entry is relevant based on the provided base URL and content type.

    Parameters:
    - entry: dictionary representing a web request
    - base_url: a string representing the base URL to check against

    Returns:
    - True if the entry is relevant, False otherwise

    """
    if base_url not in entry['request']['url']:
        return False

    if 'favicon.ico' in entry['request']['url']:
        return False

    content_type_value = find_header_value(entry['response']['headers'], 'Content-Type')
    if not content_type_value:
        return False

    relevant_content_type = ['application/json', 'text/html']

    for content_type in relevant_content_type:
        if content_type in content_type_value:
            return True

    return False

def parse_multipart_formdata(data, boundary):
    """

    This method is used to parse a multipart form data string. It takes in two parameters: 'data' which is the multipart form data string to be parsed, and 'boundary' which is the boundary used to separate the different parts of the multipart message.

    Example usage:
    """
    # Split the data into parts using the boundary
    parts = data.split("--" + boundary)

    # Initialize an empty dictionary to store parsed data
    parsed_data = {}

    # Iterate over each part of the multipart message
    for part in parts:
        # Skip empty parts and the final boundary
        if part.strip() == "" or part.strip() == "--":
            continue

        # Split the part into headers and content
        headers, content = part.split("\r\n\r\n", 1)

        # Extract the content disposition header
        content_disposition = None
        for header in headers.split("\r\n"):
            if header.startswith("Content-Disposition:"):
                content_disposition = header
                break

        if content_disposition:
            # Parse the content disposition header to extract the name
            name = content_disposition.split("name=")[1].split(";")[0].strip('"')

            # Store the name-value pair in the parsed_data dictionary
            parsed_data[name] = content.strip()

    return parsed_data


def is_static(entry):
    """
    Check if a given entry is a static resource.

    :param entry: The entry to be checked.
    :type entry: dict
    :return: True if the entry is a static resource, False otherwise.
    :rtype: bool
    """
    requested_with = find_header_value(entry['request']['headers'], 'X-Requested-With')
    if requested_with:
        print(requested_with)
    if requested_with and requested_with == 'XMLHttpRequest':
        return False

    if 'text' in entry['response']['content'] and not bool(BeautifulSoup(entry['response']['content']['text'], "html.parser").find()):
        return False

    content_type_value = find_header_value(entry['response']['headers'], 'Content-Type')
    if not content_type_value:
        return False

    if 'text/html' in content_type_value:
        return True

    return False

def is_async(entry):
    """
    Check if a given entry is asynchronous.

    :param entry: The entry to be checked.
    :type entry: dict
    :return: True if the entry is asynchronous, False otherwise.
    :rtype: bool
    """
    if 'text' in entry['response']['content']:
        content = entry['response']['content']['text']

        try:
            json.loads(content)
            return True
        except ValueError as e:
            print('no json')

    content_type_value = find_header_value(entry['response']['headers'], 'Content-Type')
    if not content_type_value:
        return False

    if 'application/json' in content_type_value:
        return True

    return False

def sequence_matcher_to_txt(diff):
    """
    Converts the input SequenceMatcher object to a formatted text representation.

    Parameters:
        diff (SequenceMatcher): The SequenceMatcher object containing the differences between the two sequences.

    Returns:
        str: A formatted string representing the differences between the two sequences in the SequenceMatcher object.

    Example Usage:
        >>> diff = SequenceMatcher(None, "python", "java")
        >>> result = sequence_matcher_to_txt(diff)
        >>> print(result)
        old: p, y, t, h, o, n
        new: j, a, v, a

    """
    old = ', '.join(diff.a)
    new = ', '.join(diff.b)
    return f'\nold: {old}\nnew: {new}'


def is_change_in_request(request, change) -> bool:
    """
    Check if a specific type of change exists in a request.

    :param request: The request object to check for changes.
    :type request: Request

    :param change: The specific change type to look for.
    :type change: Change

    :return: True if the specified change type exists in the request, False otherwise.
    :rtype: bool
    """
    for req_change in request.changes:
        if isinstance(req_change, change):
            return True
    return False


def remove_numbers_in_string(value):
    """
    Remove numbers from a given string.

    Parameters:
        value (str): The string from which numbers should be removed.

    Returns:
        str: The string with all numbers removed.

    Example:
        >>> remove_numbers_in_string("Hello123")
        'Hello'
        >>> remove_numbers_in_string("abc456xyz")
        'abcxyz'
    """
    pattern = r'[0-9]'
    cleaned = re.sub(pattern, '', value)
    return cleaned
