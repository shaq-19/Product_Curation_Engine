import json
from langchain_core.messages import ToolMessage

def parse_tool_content(tool_output):
    """Utility to handle ToolMessage or dict transparently."""
    if isinstance(tool_output, ToolMessage):
        return json.loads(tool_output.content)
    return tool_output

def generate_output(state):
    """
    Prepares final product recommendations and rationale.
    """
    scored = state.get("scored_products", [])
    college_name = state.get("store_id", "the college")

    # Safely handle ToolMessages
    profile_data = parse_tool_content(state.get("college_profile_data", {}))
    trend_data = parse_tool_content(state.get("trend_data", {}))
    survey_data = parse_tool_content(state.get("survey_data", {}))

    themes = profile_data.get("themes", [])
    sentiment = (
        survey_data.get("average_sentiment", 0.0) +
        trend_data.get("average_sentiment", 0.0)
    ) / 2

    rationale = (
        f"""Recommendations for **{college_name}** are based on:
- Alignment with campus themes: {', '.join(themes) if themes else 'N/A'}
- Recent sales performance trends
- Positive student feedback and social media sentiment (avg score: {round(sentiment, 2)})

Products scoring highest across these factors are prioritized below."""
    )

    return {**state, "final_output": {"products": scored[:20], "rationale": rationale}}
