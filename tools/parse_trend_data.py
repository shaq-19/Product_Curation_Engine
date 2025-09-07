import os
import json
from openai import OpenAI

def parse_trend_data(file_path: str) -> dict:
    """
    Parses trend data from a text file (social mentions) using an LLM to identify sentiment,
    themes, and keyword frequency. Keeps the same structure as the original TextBlob version.

    Args:
        file_path (str): Path to the trend data .txt file.

    Returns:
        Dict[str, any]: Dictionary with keyword frequency, sentiment, and trend themes.
    """
    client = OpenAI()

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Trend data TXT file not found: {file_path}")

    lines = [line.strip() for line in text.split("\n") if line.strip()]
    keywords = ["tech", "decor", "desk", "aesthetic", "study", "wellness", "bedding", "gadgets"]

    prompt = f"""
You are a data analyst assistant.

Given the following list of social media mentions:
{json.dumps(lines)}

Perform the following:
1. Analyze the sentiment of each line (range -1 to 1), and return the average sentiment rounded to 3 decimals.
2. Identify themes by matching each line to these keywords: {keywords} (case-insensitive). Each keyword should be a key in the "themes" dictionary, and values should be the list of matching lines.
3. Extract all individual words from the lines (alphabetic only, lowercase), and return the top 20 most frequent words as a list of JSON arrays like: ["word", count]
4. Return a JSON object in this exact structure:

{{
  "average_sentiment": float,
  "top_words": [["word", count], ...],
  "themes": {{
    "tech": [...],
    "decor": [...],
    "desk": [...],
    "aesthetic": [...],
    "study": [...],
    "wellness": [...],
    "bedding": [...],
    "gadgets": [...]
  }},
  "raw_mentions": [original list of lines]
}}

Only return a JSON object. Do not include any explanation, formatting, or code.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt.strip()}],
        temperature=0.3
    )

    content = response.choices[0].message.content.strip()

    try:
        result = json.loads(content)
    except json.JSONDecodeError:
        raise ValueError("LLM response could not be parsed as JSON:\n" + content)

    return result