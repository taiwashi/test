import json
import logging
import re
import os
import datetime

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
    path="accep-test/movies.json",
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
    path="accep-test/schedules.json",
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
    path="accep-test/specifications.json",
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


# Define tool properties for the diff comparison tool
diff_tool_properties = json.dumps([
    ToolProperty("oldVersion", "string", "古いバージョンの仕様ID").to_dict(),
    ToolProperty("newVersion", "string", "新しいバージョンの仕様ID").to_dict()
])

@app.generic_trigger(
    arg_name="context",
    type="mcpToolTrigger",
    toolName="compare_specifications",
    description="2つの仕様バージョン間の差分を比較します。",
    toolProperties=diff_tool_properties,
)
@app.generic_input_binding(
    arg_name="file",
    type="blob",
    connection="AzureWebJobsStorage",
    path="accep-test/specifications.json",
)
def compare_specifications(file: func.InputStream, context) -> str:
    """
    2つの仕様バージョン間の差分を比較し、変更点を抽出します。

    Args:
        file (func.InputStream): 仕様情報を含むJSONファイル
        context: トリガーコンテキスト（入力引数を含む）

    Returns:
        str: 差分情報をJSON形式で返します
    """
    try:
        content = json.loads(context)
        old_version = content["arguments"]["oldVersion"]
        new_version = content["arguments"]["newVersion"]

        if not validate_specification_id(old_version) or not validate_specification_id(new_version):
            return json.dumps({"error": "Invalid specification ID format"})

        specifications_data = json.loads(file.read().decode("utf-8"))
        
        old_spec = next(
            (spec for spec in specifications_data 
             if spec["specification_id"] == old_version),
            None
        )
        
        new_spec = next(
            (spec for spec in specifications_data 
             if spec["specification_id"] == new_version),
            None
        )

        if not old_spec or not new_spec:
            return json.dumps({"error": "One or both specifications not found"})

        # 差分を計算
        differences = {
            "title_changed": old_spec["title"] != new_spec["title"],
            "description_changed": old_spec["description"] != new_spec["description"],
            "changes": {
                "title": {
                    "old": old_spec["title"],
                    "new": new_spec["title"]
                } if old_spec["title"] != new_spec["title"] else None,
                "description": {
                    "old": old_spec["description"],
                    "new": new_spec["description"]
                } if old_spec["description"] != new_spec["description"] else None
            }
        }

        return json.dumps({
            "diff_result": differences,
            "old_version": old_version,
            "new_version": new_version,
            "comparison_date": content.get("timestamp", "")
        })

    except Exception as e:
        logging.error(f"Error comparing specifications: {str(e)}")
        return json.dumps({"error": f"Failed to compare specifications: {str(e)}"})

# Define tool properties for test item creation
create_test_items_properties = json.dumps([
    ToolProperty("specificationId", "string", "仕様書のID").to_dict(),
    ToolProperty("pastTestItemId", "string", "過去の試験項目のID").to_dict()
])

@app.generic_trigger(
    arg_name="context",
    type="mcpToolTrigger",
    toolName="create_test_items",
    description="仕様書や過去の項目書を元に試験項目を作成します。",
    toolProperties=create_test_items_properties,
)
@app.generic_input_binding(
    arg_name="specifications",
    type="blob",
    connection="AzureWebJobsStorage",
    path="accep-test/specifications.json",
)
@app.generic_input_binding(
    arg_name="past_items",
    type="blob",
    connection="AzureWebJobsStorage",
    path="accep-test/past_test_items.json",
)
@app.generic_output_binding(
    arg_name="output_items",
    type="blob",
    connection="AzureWebJobsStorage",
    path="accep-test/test_items/{mcptoolargs.specificationId}.json",
)
def create_test_items(specifications: func.InputStream, past_items: func.InputStream, output_items: func.Out[str], context) -> str:
    """
    仕様書と過去の試験項目を元に新しい試験項目を作成します。

    Args:
        specifications (func.InputStream): 仕様書データ
        past_items (func.InputStream): 過去の試験項目データ
        output_items (func.Out[str]): 出力する試験項目データ
        context: トリガーコンテキスト

    Returns:
        str: 作成された試験項目のJSON文字列
    """
    try:
        content = json.loads(context)
        specification_id = content["arguments"]["specificationId"]
        past_test_item_id = content["arguments"]["pastTestItemId"]

        # バリデーション
        if not validate_specification_id(specification_id):
            return json.dumps({"error": "Invalid specification ID format"})
        if not validate_test_item_id(past_test_item_id):
            return json.dumps({"error": "Invalid test item ID format"})

        # データ取得
        specifications_data = json.loads(specifications.read().decode("utf-8"))
        past_items_data = json.loads(past_items.read().decode("utf-8"))

        # 該当データ検索
        specification = next(
            (spec for spec in specifications_data 
             if spec["specification_id"] == specification_id),
            None
        )
        past_item = next(
            (item for item in past_items_data 
             if item["test_item_id"] == past_test_item_id),
            None
        )

        if not specification or not past_item:
            return json.dumps({"error": "Specification or past test item not found"})

        # 試験項目の生成
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        new_test_items = {
            "test_item_id": f"TEST{int(specification_id[4:]):03d}",
            "specification_id": specification_id,
            "items": generate_test_items(specification, past_item),
            "created_at": current_date,
            "updated_at": current_date
        }

        # 結果の保存と返却
        output_items.set(json.dumps(new_test_items))
        return json.dumps({"testItems": new_test_items})

    except Exception as e:
        logging.error(f"Error creating test items: {str(e)}")
        return json.dumps({"error": f"Failed to create test items: {str(e)}"})

def validate_test_item_id(test_item_id: str) -> bool:
    """試験項目IDのバリデーション"""
    return bool(re.match(r"^TEST\d{3}$", test_item_id))

def generate_test_items(specification: dict, past_item: dict) -> list:
    """
    仕様と過去の試験項目から新しい試験項目を生成します。

    Args:
        specification (dict): 仕様データ
        past_item (dict): 過去の試験項目データ

    Returns:
        list: 生成された試験項目のリスト
    """
    base_items = []
    
    # 基本的な機能確認項目
    base_items.append(f"{specification['title']}の動作を確認")
    base_items.append(f"{specification['title']}の表示内容が正しいことを確認")
    
    # 過去の試験項目から関連する項目を追加
    for item in past_item["items"]:
        if any(keyword in item for keyword in [specification["title"], specification["description"]]):
            base_items.append(item)
    
    # 仕様書から特定の動作に関する項目を生成
    if "表示" in specification["description"]:
        base_items.append(f"{specification['title']}の表示速度を確認")
    if "遷移" in specification["description"]:
        base_items.append(f"{specification['title']}の遷移先が正しいことを確認")
    
    return base_items
