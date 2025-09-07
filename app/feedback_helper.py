import json
from openai import OpenAI
from langsmith import traceable

client = OpenAI()

def safe_json_stringify(data):
    def default_serializer(obj):
        try:
            return str(obj)
        except:
            return "<unserializable>"
    
    return json.dumps(data, indent=2, default=default_serializer)


@traceable(name="college-assortment-curation.apply_feedback_to_output")
def apply_feedback_to_output(whole_state: dict, final_output: dict, feedback: str) -> dict:
    """
    Uses LLM to modify the final_output based on user feedback.

    Args:
        whole_state (dict): Complete state, useful for answering factual questions.
        final_output (dict): Original output with 'products' and 'rationale'
        feedback (str): User feedback or question
    
    Returns:
        dict: Updated final_output or rationale-only if no product changes are needed.
    """
    products = final_output.get("products", [])
    rationale = final_output.get("rationale", "")

    prompt = f"""
You are a retail AI assistant improving product recommendations based on planner feedback.

Original product list:
{json.dumps(products, indent=2)}

Original rationale:
"{rationale}"

Planner feedback:
"{feedback}"

Full context (whole_state) for answering questions:
{safe_json_stringify(whole_state)}

Instructions:
- If the feedback is a question or unrelated to products, reply with a rationale only. Leave products unchanged.
- If feedback includes specific actions (e.g., "add lamp", "remove desk"), update the products list accordingly.
- Do NOT modify products unless explicitly asked with proper product name that makes a sense and reply a sensible answer clarifying the same.
- If the instructions are unclear, ask for clarification and do not change the product list.
- If asked on how to improve the list, suggest changes based on the feedback.
- If products are unchanged, return the original list with a rationale.
- If products are changed, return the updated list with a new rationale.
- Properly answer if questions on competitors, trends, or product details are asked by analyzing respective data
- If asked for suggestions on more products, add more as part of your understanding with a rationale for why those products would be beneficial.
- Always respond in this exact JSON format:
{{
  "products": [...],   <-- same as original if unchanged
  "rationale": "..."   <-- updated with either answer or change reasoning
}}
- DO NOT invent changes. Only update what’s clearly stated in the feedback.
- Make sure the output is always valid JSON.
- Keep response concise and focused on the products and rationale. 
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4
    )

    content = response.choices[0].message.content.strip()

    try:
        updated = json.loads(content)

        # If the products are unchanged, we assume it's just a question
        if updated.get("products") == products:
            return {
                "products": products,  # Keep unchanged
                "rationale": updated.get("rationale", "No changes needed.")
            }

        # If products have changed, return full updated output
        return updated

    except json.JSONDecodeError:
        raise ValueError(f"LLM returned invalid JSON:\n{content}")
