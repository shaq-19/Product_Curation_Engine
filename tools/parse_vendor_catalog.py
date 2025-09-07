import pandas as pd

def parse_vendor_catalog(file_path: str) -> list:
    """
    Parses a vendor catalog CSV file and returns a list of product dictionaries.

    Args:
        file_path (str): Path to the vendor catalog CSV file.

    Returns:
        List[dict]: List of parsed product dictionaries.
    """
    
    df = pd.read_csv(file_path)
    required_columns = [
        "name", "category", "sub_category", "price", "themes"
    ]

    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    products = []
    for _, row in df.iterrows():
        product = {
            "name": row["name"],
            "category": row["category"],
            "sub_category": row["sub_category"],
            "price": float(row["price"]),
            # "vendor": row["Vendor"],
            # "stock": int(row["Stock"]),
            # "eligible_colleges": [c.strip() for c in str(row["Eligible Colleges"]).split(",") if c.strip()],
            "themes": [t.strip() for t in str(row["themes"]).split(",") if t.strip()]
        }
        products.append(product)

    return products