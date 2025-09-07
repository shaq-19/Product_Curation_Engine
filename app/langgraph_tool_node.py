import sys
import os
import json
# from uuid import uuid4

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from tools.wrapped_tools import get_all_tools

# Get list of tools and map by name
tools_list = get_all_tools()
tools_dict = {tool_.name: tool_ for tool_ in tools_list}

def tool_node(state):
    inputs = state.get("file_inputs", {})
    results = {}

    tool_mapping = [
        ("vendor", "vendor_tool"),
        ("sales", "sales_tool"),
        ("survey", "survey_tool"),
        ("trend", "trend_tool"),
        ("college_profile", "college_profile_tool"),
        ("competitor", "competitor_tool"),
    ]

    for key, tool_name in tool_mapping:
        if key in inputs:
            file_path = inputs[key]
            print(f"Invoking tool: {tool_name} with file: {file_path}")
            try:
                tool_func = tools_dict[tool_name]
                tool_output = tool_func.invoke({"file_path": file_path})
                results[f"{key}_data"] = tool_output or {}
            except Exception as e:
                print(f"Error invoking {tool_name}: {e}")
                results[f"{key}_data"] = {}

    return {**state, **results}