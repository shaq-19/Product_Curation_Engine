import pandas as pd

def parse_competitor_data(file_path: str) -> dict:
    """
    Parses competitor product and pricing data from CSV and returns pricing benchmarks.

    Args:
        file_path (str): Path to the competitor data CSV.

    Returns:
        Dict[str, any]: Summary statistics across all competitor products.
    """
    df = pd.read_csv(file_path)

    required_columns = ["name", "competitor_price", "source"]

    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    prices = df["competitor_price"]

    return {
        "min_price": float(prices.min()),
        "max_price": float(prices.max()),
        "avg_price": float(prices.mean()),
        "products": df["name"].unique().tolist(),
        "sources": df["source"].unique().tolist()
    }
