import json
from langchain.tools import tool
from langchain_core.messages import ToolMessage

from tools.parse_vendor_catalog import parse_vendor_catalog
from tools.parse_sales_data import parse_sales_data
from tools.parse_survey_feedback import parse_survey_feedback
from tools.parse_trend_data import parse_trend_data
from tools.parse_college_profile import parse_college_profile
from tools.parse_competitor_data import parse_competitor_data


@tool
def vendor_tool(file_path: str):
    """Parse the vendor catalog CSV file."""
    parsed = parse_vendor_catalog(file_path)
    return ToolMessage(
        tool_call_id="vendor_tool",
        content=json.dumps(parsed)
    )

@tool
def sales_tool(file_path: str):
    """Parse the sales data CSV file."""
    parsed = parse_sales_data(file_path)
    return ToolMessage(
        tool_call_id="sales_tool",
        content=json.dumps(parsed)
    )

@tool
def survey_tool(file_path: str):
    """Parse the survey feedback PDF."""
    parsed = parse_survey_feedback(file_path)
    print('\n\nparsed: wrapped: ', parsed)
    return ToolMessage(
        tool_call_id="survey_tool",
        content=json.dumps(parsed)
    )

@tool
def trend_tool(file_path: str):
    """Parse the social trend mentions from text."""
    parsed = parse_trend_data(file_path)
    return ToolMessage(
        tool_call_id="trend_tool",
        content=json.dumps(parsed)
    )

@tool
def college_profile_tool(file_path: str):
    """Parse the college profile JSON."""
    parsed = parse_college_profile(file_path)
    print('\n\nparsed: profile: ', parsed)
    return ToolMessage(
        tool_call_id="college_profile_tool",
        content=json.dumps(parsed)
    )

@tool
def competitor_tool(file_path: str):
    """Parse competitor product pricing data from CSV."""
    parsed = parse_competitor_data(file_path)
    return ToolMessage(
        tool_call_id="competitor_tool",
        content=json.dumps(parsed)
    )


def get_all_tools():
    return [
        vendor_tool,
        sales_tool,
        survey_tool,
        trend_tool,
        college_profile_tool,
        competitor_tool
    ]