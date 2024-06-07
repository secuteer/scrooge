from genson import SchemaBuilder
import json
from urllib.parse import parse_qs
import jsondiff


def create_json_schema(data: dict):
    """
    Constructs a JSON schema from the given data dictionary.

    :param data: A dictionary containing the data to be used for creating the JSON schema.
    :type data: dict
    :return: The JSON schema generated from the given data dictionary.
    :rtype: dict
    """
    builder = SchemaBuilder()
    builder.add_object(data)

    return builder.to_schema()


def create_content_json_schema(request: dict) -> dict:
    """
    Function that creates a JSON schema from the content of a request.

    Args:
        request (dict): The request object containing response content.

    Returns:
        dict: The JSON schema created from the content, or an empty dictionary if the content is invalid JSON.
    """
    try:
        if 'text' in request['response']['content']:
            data = json.loads(request['response']['content']['text'])
            return create_json_schema(data)

    except json.decoder.JSONDecodeError:
        print("Invalid JSON", request)

    return {}


def create_request_json_schema(request: dict) -> dict:
    """

    Create a JSON schema for the request data.

    Parameters:
    - request (dict): The request object containing the data.

    Return:
    - dict: The JSON schema for the request data.


    This method takes a `request` object as input and checks if it contains 'postData' and 'params' keys.
    If it does, it parses the data and creates a JSON schema using the `create_json_schema` function.
    If there is any error in decoding the JSON data, an "Invalid JSON" message is printed.

    The method returns the JSON schema for the request data if it exists, otherwise an empty dictionary is returned.

    """
    try:
        if 'postData' in request['request'] and 'params' in request['request']['postData']:
            data = json.dumps(parse_qs(request['request']['postData']['text']))
            # data = data.replace("'", "\"")
            data = json.loads(data)

            return create_json_schema(data)

    except json.decoder.JSONDecodeError:
        print("Invalid JSON")

    return {}


def visualize_schema(schema: dict, depth=0) -> None:
    """
    Visualizes the given schema recursively.

    Args:
        schema (dict): The schema to visualize.
        depth (int, optional): The current depth of recursion. Defaults to 0.

    Returns:
        None
    """
    s = ""
    for i in range(depth * 2):
        s += str(" ")
    if schema:
        for item in schema:
            print(f"{s}|===", item)
            if type(schema[item]) is dict:
                visualize_schema(schema[item], depth=depth+1)
            else:
                print(f"{s}|===", schema[item])


def compare_schema(schema1: dict, schema2: dict) -> bool:
    """
    Compare two schema dictionaries and return a boolean indicating whether they are equal.

    Parameters:
    schema1 (dict): The first schema dictionary to compare.
    schema2 (dict): The second schema dictionary to compare.

    Returns:
    bool: True if the two schema dictionaries are equal, False otherwise.
    """
    return schema1 == schema2


def json_compare(schema1: dict, schema2: dict) -> str:
    """
    Compare two JSON schemas and return the differences.

    :param schema1: The first JSON schema to compare.
    :type schema1: dict
    :param schema2: The second JSON schema to compare.
    :type schema2: dict
    :return: The differences between the two JSON schemas.
    :rtype: str
    """
    return jsondiff.diff(schema1, schema2)