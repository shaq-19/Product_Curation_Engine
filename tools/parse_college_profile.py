import json

def parse_college_profile(file_path: str) -> dict:
    """
    Parses a college profile JSON file and returns a dictionary of store characteristics.

    Args:
        file_path (str): Path to the JSON file.

    Returns:
        Dict[str, any]: Parsed college profile information.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    required_fields = ["store_id", "college_name", "region", "school_type", "themes", 
                       "season", "housing_type", "enrollment_size"]

    for field in required_fields:
        if field not in data:
            raise ValueError(f"Missing required field: {field}")

    return {
        "store_id": data["store_id"],
        "college_name": data["college_name"],
        "region": data["region"],
        "school_type": data["school_type"],
        "themes": data["themes"],
        # "room_size": data["room_size"],
        "season": data["season"],
        "housing_type": data["housing_type"],
        "enrollment_size": data["enrollment_size"]
    }