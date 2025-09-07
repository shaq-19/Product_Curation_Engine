from langgraph.graph import StateGraph, END

from langgraph_tool_node import tool_node
from langgraph_score_node import score_products
from langgraph_output_node import generate_output

# Define the graph and its state
from typing import TypedDict, List, Dict, Any, Optional, Tuple

class State(TypedDict, total=False):
    store_id: str
    college_profile_data: Dict[str, Any]
    vendor_data: List[Dict[str, Any]]
    sales_data: Dict[str, Any]
    survey_data: Dict[str, Any]
    trend_data: Dict[str, Any]
    competitor_data: Dict[str, Any]
    scored_products: List[Tuple[str, float]]
    final_output: Dict[str, Any]
    file_inputs: Dict[str, str]
    user_feedback: str

workflow = StateGraph(State)


# Add nodes
workflow.add_node("parse_files", tool_node)
workflow.add_node("score_products", score_products)
workflow.add_node("generate_output", generate_output)

# Define flow
workflow.set_entry_point("parse_files")
workflow.add_edge("parse_files", "score_products")
workflow.add_edge("score_products", "generate_output")
workflow.add_edge("generate_output", END)

# Compile into executable workflow
assortment_workflow = workflow.compile()