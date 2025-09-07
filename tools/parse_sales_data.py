import pandas as pd
from datetime import datetime

def parse_sales_data(file_path: str) -> dict:
    """
    Parses sales data CSV and returns aggregated product-level metrics.

    Args:
        file_path (str): Path to the sales data CSV file.

    Returns:
        Dict[str, dict]: Dictionary with product name as key and metrics as values.
    """
    df = pd.read_csv(file_path)

    required_columns = [
        "name", "total_units_sold"
    ]

    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    # Convert Date to datetime
    # df["Date"] = pd.to_datetime(df["Date"], errors='coerce')
    # df.dropna(subset=["Date"], inplace=True)

    # Aggregate by product
    product_stats = {}
    grouped = df.groupby("name")

    for name, group in grouped:
        product_stats[name] = {
            "total_units_sold": int(group["total_units_sold"].sum()),
            # "total_revenue": float(group["Revenue"].sum()),
            # "avg_units_per_day": float(group.groupby("Date")["Units Sold"].sum().mean()),
            # "store_coverage": group["Store ID"].nunique(),
            # "last_sale_date": group["Date"].max().strftime("%Y-%m-%d")
        }
    return product_stats