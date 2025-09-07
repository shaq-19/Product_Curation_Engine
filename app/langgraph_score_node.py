import logging
import json

def score_products(state):
    """ If a product has: 
        2 theme matches → +1.0
        150 units sold → +1.5
        Base score: 1.0 + 1.0 + 1.5 = 3.5
        Trend sentiment = 0.6 → multiplier = 0.5 + 0.5×0.6 = 0.8
        Survey sentiment = 0.8 → multiplier = 0.5 + 0.5×0.8 = 0.9
        Final Score = 3.5 × 0.8 × 0.9 = 2.52
    """

    logging.basicConfig(level=logging.INFO)
    logging.info("🔍 Scoring Products Node Activated")

    # Deserialize tool messages
    vendor_data = json.loads(state["vendor_data"].content) if "vendor_data" in state else []

    sales_data = json.loads(state["sales_data"].content) if "sales_data" in state else {}

    trend = json.loads(state["trend_data"].content) if "trend_data" in state else {}
    trend_sentiment = trend.get("average_sentiment", 0.5)

    survey = json.loads(state["survey_data"].content) if "survey_data" in state else {}
    survey_sentiment = survey.get("average_sentiment", 0.5)

    profile = json.loads(state["college_profile_data"].content) if "college_profile_data" in state else {}
    store_themes = profile.get("themes", [])

    logging.info(f"Trend Sentiment Score: {trend_sentiment}")
    logging.info(f"Survey Sentiment Score: {survey_sentiment}")
    logging.info(f"Store Themes: {store_themes}")

    product_scores = []

    for product in vendor_data:
        name = product.get("name", "")
        price = product.get("price", 0)
        
        # Some themes are double encoded, so fix them
        raw_themes = product.get("themes", [])
        try:
            themes = json.loads(raw_themes[0]) if raw_themes and isinstance(raw_themes[0], str) else raw_themes
        except Exception:
            themes = raw_themes
        
        # Base score logic
        score = 1.0

        # Theme match bonus
        match_count = sum(1 for theme in themes if theme in store_themes)
        score += match_count * 0.5

        # Sales bonus
        sales = sales_data.get(name, {}).get("total_units_sold", 0)
        score += min(sales / 100, 2.0)  # capped sales weight

        # Sentiment boost
        score *= (0.5 + 0.5 * trend_sentiment)
        score *= (0.5 + 0.5 * survey_sentiment)

        product_scores.append((name, round(score, 2)))

    # Sort and save
    product_scores = sorted(product_scores, key=lambda x: x[1], reverse=True)
    logging.info(f"🏁 Final Sorted Scores: {product_scores}")

    state["scored_products"] = product_scores
    return state