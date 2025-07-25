import json
import logging
import re
import os

import azure.functions as func
from azure.storage.blob import BlobServiceClient

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

# Constants for the Azure Blob Storage container, file, and blob path
_SNIPPET_NAME_PROPERTY_NAME = "snippetname"
_SNIPPET_PROPERTY_NAME = "snippet"
_BLOB_PATH = "snippets/{mcptoolargs." + _SNIPPET_NAME_PROPERTY_NAME + "}.json"


class ToolProperty:
    def __init__(self, property_name: str, property_type: str, description: str):
        self.propertyName = property_name
        self.propertyType = property_type
        self.description = description

    def to_dict(self):
        return {
            "propertyName": self.propertyName,
            "propertyType": self.propertyType,
            "description": self.description,
        }


# Define the tool properties using the ToolProperty class
tool_properties_save_snippets_object = [
    ToolProperty(_SNIPPET_NAME_PROPERTY_NAME, "string", "The name of the snippet."),
    ToolProperty(_SNIPPET_PROPERTY_NAME, "string", "The content of the snippet."),
]

tool_properties_get_snippets_object = [ToolProperty(_SNIPPET_NAME_PROPERTY_NAME, "string", "The name of the snippet.")]

# Convert the tool properties to JSON
tool_properties_save_snippets_json = json.dumps([prop.to_dict() for prop in tool_properties_save_snippets_object])
tool_properties_get_snippets_json = json.dumps([prop.to_dict() for prop in tool_properties_get_snippets_object])


@app.generic_trigger(
    arg_name="context",
    type="mcpToolTrigger",
    toolName="hello_mcp",
    description="Hello world.",
    toolProperties="[]",
)
def hello_mcp(context) -> None:
    """
    A simple function that returns a greeting message.

    Args:
        context: The trigger context (not used in this function).

    Returns:
        str: A greeting message.
    """
    return "Hello I am MCPTool!"


@app.generic_trigger(
    arg_name="context",
    type="mcpToolTrigger",
    toolName="get_snippet",
    description="Retrieve a snippet by name.",
    toolProperties=tool_properties_get_snippets_json,
)
@app.generic_input_binding(arg_name="file", type="blob", connection="AzureWebJobsStorage", path=_BLOB_PATH)
def get_snippet(file: func.InputStream, context) -> str:
    """
    Retrieves a snippet by name from Azure Blob Storage.

    Args:
        file (func.InputStream): The input binding to read the snippet from Azure Blob Storage.
        context: The trigger context containing the input arguments.

    Returns:
        str: The content of the snippet or an error message.
    """
    snippet_content = file.read().decode("utf-8")
    logging.info(f"Retrieved snippet: {snippet_content}")
    return snippet_content


@app.generic_trigger(
    arg_name="context",
    type="mcpToolTrigger",
    toolName="save_snippet",
    description="Save a snippet with a name.",
    toolProperties=tool_properties_save_snippets_json,
)
@app.generic_output_binding(arg_name="file", type="blob", connection="AzureWebJobsStorage", path=_BLOB_PATH)
def save_snippet(file: func.Out[str], context) -> str:
    content = json.loads(context)
    snippet_name_from_args = content["arguments"][_SNIPPET_NAME_PROPERTY_NAME]
    snippet_content_from_args = content["arguments"][_SNIPPET_PROPERTY_NAME]

    if not snippet_name_from_args:
        return "No snippet name provided"

    if not snippet_content_from_args:
        return "No snippet content provided"

    file.set(snippet_content_from_args)
    logging.info(f"Saved snippet: {snippet_content_from_args}")
    return f"Snippet '{snippet_content_from_args}' saved successfully"


# Define tool properties for the movie retrieval tool
movie_tool_properties = json.dumps([])

@app.generic_trigger(
    arg_name="context",
    type="mcpToolTrigger",
    toolName="get_movie_list",
    description="Retrieve the list of movies.",
    toolProperties=movie_tool_properties,
)
@app.generic_input_binding(
    arg_name="file",
    type="blob",
    connection="AzureWebJobsStorage",
    path="movies/movies.json",
)
def get_movie_list(file: func.InputStream, context) -> str:
    """
    Retrieves the list of movies from Azure Blob Storage.

    Args:
        file (func.InputStream): The input binding to read the movie list from Azure Blob Storage.
        context: The trigger context containing the input arguments.

    Returns:
        str: The content of the movie list or an error message.
    """
    try:
        movie_list_content = file.read().decode("utf-8")
        logging.info(f"Retrieved movie list: {movie_list_content}")
        return movie_list_content
    except Exception as e:
        logging.error(f"Error retrieving movie list: {str(e)}")
        return json.dumps({"error": "Failed to retrieve movie list."})


# Define tool properties for the movie schedule retrieval tool
schedule_tool_properties = json.dumps([])

@app.generic_trigger(
    arg_name="context",
    type="mcpToolTrigger",
    toolName="get_movie_schedule",
    description="Retrieve the movie schedule.",
    toolProperties=schedule_tool_properties,
)
@app.generic_input_binding(
    arg_name="file",
    type="blob",
    connection="AzureWebJobsStorage",
    path="schedules/schedules.json",
)
def get_movie_schedule(file: func.InputStream, context) -> str:
    """
    Retrieves the movie schedule from Azure Blob Storage.

    Args:
        file (func.InputStream): The input binding to read the movie schedule from Azure Blob Storage.
        context: The trigger context containing the input arguments.

    Returns:
        str: The content of the movie schedule or an error message.
    """
    try:
        schedule_content = file.read().decode("utf-8")
        logging.info(f"Retrieved raw schedule content: {schedule_content}")

        # Validate if the content is a valid JSON
        try:
            schedule_json = json.loads(schedule_content)
            logging.info("Schedule content successfully parsed as JSON.")
            return json.dumps(schedule_json)
        except json.JSONDecodeError as json_error:
            logging.error(f"Failed to parse schedule content as JSON: {str(json_error)}")
            return json.dumps({"error": "Invalid JSON format in schedule content."})

    except Exception as e:
        logging.error(f"Error retrieving movie schedule: {str(e)}")
        return json.dumps({"error": "Failed to retrieve movie schedule.", "details": str(e)})


def get_blob_service_client():
    connection_string = os.getenv("AzureWebJobsStorage")
    return BlobServiceClient.from_connection_string(connection_string)


def validate_specification_id(specification_id: str) -> bool:
    """仕様IDのバリデーション"""
    return bool(re.match(r"^SPEC\d{3}$", specification_id))


# Define tool properties for the specification understanding tool
specification_tool_properties = json.dumps([
    ToolProperty("specificationId", "string", "The ID of the specification to understand.").to_dict()
])

@app.generic_trigger(
    arg_name="context",
    type="mcpToolTrigger",
    toolName="understand_specification",
    description="Understand and extract system information from a specification.",
    toolProperties=specification_tool_properties,
)
@app.generic_input_binding(
    arg_name="file",
    type="blob",
    connection="AzureWebJobsStorage",
    path="movies/specifications.json",
)
def understand_specification(file: func.InputStream, context) -> str:
    """
    Analyzes a specification and extracts system information.

    Args:
        file (func.InputStream): The input binding to read the specifications from Azure Blob Storage.
        context: The trigger context containing the input arguments.

    Returns:
        str: The extracted system information in JSON format.
    """
    try:
        content = json.loads(context)
        specification_id = content["arguments"]["specificationId"]

        if not validate_specification_id(specification_id):
            return json.dumps({"error": "Invalid specification ID format"})

        specifications_data = json.loads(file.read().decode("utf-8"))
        
        specification = next(
            (spec for spec in specifications_data 
             if spec["specification_id"] == specification_id),
            None
        )

        if not specification:
            return json.dumps({"error": "Specification not found"})

        system_info = {
            "title": specification["title"],
            "description": specification["description"],
            "updated_at": specification["updated_at"]
        }

        return json.dumps({"systemInfo": system_info})

    except Exception as e:
        logging.error(f"Error processing specification: {str(e)}")
        return json.dumps({"error": f"Failed to process specification: {str(e)}"})
