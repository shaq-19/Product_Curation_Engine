import os
import json
from openai import OpenAI

def parse_survey_feedback(file_path: str) -> dict:
    """
    Parses survey feedback from a TXT file and returns sentiment summaries and key themes using LLM.
    Keeps the same structure and key names as the original version using TextBlob.

    Args:
        file_path (str): Path to the TXT file.

    Returns:
        Dict[str, any]: Dictionary containing sentiment scores and extracted feedback themes.
    """
    client = OpenAI()

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            text = file.read()
        # print("\ntext: ", text)
    except FileNotFoundError:
        raise FileNotFoundError(f"Survey feedback TXT file not found: {file_path}")

    feedback_lines = [line.strip() for line in text.split("\n") if line.strip()]
    # print("\nfeedback_lines: ", feedback_lines)

    keywords = ["pricing", "delivery", "selection", "dorm", "health", "tech", "supplies"]

    prompt = f"""
You are a language model tasked with analyzing survey feedback.

Perform the following:
1. Analyze the sentiment of each feedback line and calculate the average sentiment score (range -1 to 1, rounded to 3 decimals).
2. Match each feedback line to any relevant keywords from this list: {keywords}. A line may match more than one theme.
3. Create a dictionary with exactly these keys:
    - "average_sentiment": float
    - "themes": dictionary with exactly the 7 keywords as keys, values are lists of matching feedback lines
    - "raw_feedback": list of all the original feedback lines

Only respond with the JSON object. Do not explain anything. Do not include any code or comments.

Feedback lines:
{json.dumps(feedback_lines)}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt.strip()}],
        temperature=0.2
    )

    content = response.choices[0].message.content.strip()

    try:
        result = json.loads(content)
    except json.JSONDecodeError:
        raise ValueError("LLM response could not be parsed as JSON:\n" + content)

    print("\n avg_sentiment: ", result.get("average_sentiment"))
    print("\n themes: ", result.get("themes"))
    # print("\n feedback_lines : ", result.get("raw_feedback"))
    # print("\n LLM response: ", content)
    # print("\n result: ", result)
    return result