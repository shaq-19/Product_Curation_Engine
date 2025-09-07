import streamlit as st
import altair as alt
import os
import traceback
import pandas as pd
import json
import re
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from openai import OpenAI
from AssortmentEngineLanggraph import assortment_workflow
from feedback_helper import apply_feedback_to_output

# --- Setup ---
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

st.set_page_config(page_title="College Store Assortment Engine", layout="centered")
st.title("🎓 College Store Assortment Engine")

# --- Initialize session state variables safely ---
if "final_state" not in st.session_state:
    st.session_state.final_state = None
if "feedback_text" not in st.session_state:
    st.session_state.feedback_text = ""
if "file_paths" not in st.session_state:
    st.session_state.file_paths = None
if "files_processed" not in st.session_state:
    st.session_state.files_processed = False
if "data_viz" not in st.session_state:
    st.session_state.data_viz = False
if "show_data_viz" not in st.session_state:
    st.session_state.show_data_viz = False

# --- Caching functions ---
@st.cache_data
def load_sales_data(path):
    return pd.read_csv(path)

@st.cache_data
def get_top_selling_products(sales_df):
    return (
        sales_df.groupby("name")["total_units_sold"]
        .sum()
        .reset_index()
        .sort_values(by="total_units_sold", ascending=False)
        .head(5)
    )

@st.cache_data
def load_trend_text(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

@st.cache_data
def analyze_trends_with_llm(trend_text):
    llm_prompt = f"""
    You are an expert trend analyst.
    Analyze the social media trend data below and identify the top 5 trending products based ONLY on the number of times each product is explicitly mentioned in the text.
    - Mentions are case-insensitive.
    - Count only exact whole word matches for each product, including plural forms (e.g., 'laptop stand' and 'laptop stands' count as the same product).
    - Do NOT estimate, guess, or add any extra mentions beyond those explicitly in the text.
    - Your counts must exactly match the real number of occurrences.
    - Rank products strictly by mention counts, highest first.
    - If multiple products have the same mention count, sort those products alphabetically.
    - Return ONLY a JSON array in this exact format, without extra text:

    [
        {{ "rank": 1, "product": "Product Name", "mentions": 5 }},
        {{ "rank": 2, "product": "Product Name", "mentions": 4 }},
        ...
    ]

    Trend data:
    \"\"\"
    {trend_text}
    \"\"\"
    """

    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": llm_prompt}
        ]
    )

    raw_output = response.choices[0].message.content
    json_str = re.search(r'\[.*\]', raw_output, re.DOTALL).group(0)
    trend_items = json.loads(json_str)
    trend_df = pd.DataFrame(trend_items)
    return trend_df

@st.cache_data
def load_survey_text(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

@st.cache_data
def analyze_survey_with_llm(survey_text):
    llm_prompt_survey = f"""
    You are a product analyst.
    Analyze the following survey feedback text and extract a list of products mentioned along with the exact number of times each product is explicitly mentioned.
    - Mentions are case-insensitive.
    - Count only exact whole word matches, including plural forms.
    - Do NOT guess or add any extra mentions beyond the explicit text.
    - Return ONLY a JSON array in this exact format:
    [
        {{ "product": "Product Name", "mentions": 3 }},
        {{ "product": "Product Name", "mentions": 2 }},
            ...
    ]
    Survey feedback text:
    \"\"\"
    {survey_text}
    \"\"\"
    """
    client = OpenAI()
    response_survey = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": llm_prompt_survey}
        ]
    )

    raw_survey_output = response_survey.choices[0].message.content

    json_match = re.search(r'\[.*\]', raw_survey_output, re.DOTALL)
    if json_match:
        json_str_survey = json_match.group(0)
        survey_products = json.loads(json_str_survey)

        if survey_products and all('product' in item and 'mentions' in item for item in survey_products):
            product_mentions = {item["product"]: item["mentions"] for item in survey_products}
        else:
            product_mentions = {}
    else:
        product_mentions = {}

    return product_mentions

@st.cache_data
def load_competitor_data(path):
    return pd.read_csv(path)

# --- Step 1: College Profile ---
st.subheader("1. College Profile")
store_id = st.text_input("Store ID", value="UCLA-001")
region = st.selectbox("Region", ["Northeast", "Midwest", "South", "West"])
school_type = st.selectbox("School Type", ["STEM", "Liberal Arts", "HBCU", "Community", "Other"])
themes = st.multiselect("Themes", ["Tech-savvy", "Climate-conscious", "Budget-minded", "Design-focused"])

# --- Step 2: Upload Files ---
st.subheader("2. Upload Files")
vendor_file = st.file_uploader("Vendor Catalog (.csv)", type="csv")
sales_file = st.file_uploader("Sales Data (.csv)", type="csv")
survey_file = st.file_uploader("Survey Feedback (.txt)", type="txt")
trend_file = st.file_uploader("Trend Data (.txt)", type="txt")
profile_file = st.file_uploader("College Profile (.json)", type="json")
competitor_file = st.file_uploader("Competitor Data (.csv)", type="csv")

# --- Step 3: Process Files ---
st.subheader("3. Process Files")
if st.button("🚀 Process Files"):
    if not all([vendor_file, sales_file, survey_file, trend_file, profile_file, competitor_file]):
        st.error("Please upload all required files.")
    else:
        # Save uploaded files
        paths = {
            "vendor": os.path.join(UPLOAD_FOLDER, "vendor_catalog.csv"),
            "sales": os.path.join(UPLOAD_FOLDER, "sales_data.csv"),
            "survey": os.path.join(UPLOAD_FOLDER, "survey_feedback.txt"),
            "trend": os.path.join(UPLOAD_FOLDER, "trend_data.txt"),
            "college_profile": os.path.join(UPLOAD_FOLDER, "college_profile.json"),
            "competitor": os.path.join(UPLOAD_FOLDER, "competitor_data.csv"),
        }

        with open(paths["vendor"], "wb") as f:
            f.write(vendor_file.read())
        with open(paths["sales"], "wb") as f:
            f.write(sales_file.read())
        with open(paths["survey"], "wb") as f:
            f.write(survey_file.read())
        with open(paths["trend"], "wb") as f:
            f.write(trend_file.read())
        with open(paths["college_profile"], "wb") as f:
            f.write(profile_file.read())
        with open(paths["competitor"], "wb") as f:
            f.write(competitor_file.read())

        # Save paths in session_state
        st.session_state.file_paths = paths
        st.session_state.files_processed = True  # ✅ Set the flag


if st.session_state.files_processed:
    st.success("✅ Files processed successfully!")

# --- Step 4: Run Data Visualization ---
st.subheader("4. Data Visualization")
if st.button("📊 Data Visualization"):
    if not st.session_state.files_processed:
        st.error("Please process the files before running the engine.")
    else:
        st.session_state.data_viz = True

if st.session_state.data_viz:
    row1_col1, row1_col2 = st.columns(2)
    row2_col1, row2_col2 = st.columns(2)

    # Top Selling Products - row 1, col 1
    try:
        sales_df = load_sales_data(st.session_state.file_paths["sales"])

        if "name" not in sales_df.columns or "total_units_sold" not in sales_df.columns:
            row1_col1.warning("Sales file must contain 'name' and 'total_units_sold' columns.")
        else:
            top_products = get_top_selling_products(sales_df)
            chart = (
                alt.Chart(top_products)
                .mark_bar()
                .encode(
                    x=alt.X("name:N", sort="-y", title="Product Name"),
                    y=alt.Y("total_units_sold:Q", title="Total Units Sold"),
                    tooltip=["name", "total_units_sold"],
                )
                .properties(
                    title="🏆Top 5 Selling Products",
                    width=280,
                    height=350,
                )
            )
            row1_col1.altair_chart(chart, use_container_width=True)

    except Exception as e:
        row1_col1.error(f"Failed to create sales graph: {e}")

    # Top Trending Products - row 1, col 2
    try:
        trend_text = load_trend_text(st.session_state.file_paths["trend"])
        trend_df = analyze_trends_with_llm(trend_text)

        bars = alt.Chart(trend_df).mark_bar(color="#FF8C00").encode(
            y=alt.Y("product:N", sort=alt.EncodingSortField(field="mentions", order="descending"), title="Product"),
            x=alt.X("mentions:Q", title="Mentions"),
            tooltip=["rank", "product", "mentions"]
        )

        labels = bars.mark_text(
            align='left',
            baseline='middle',
            dx=3
        ).encode(
            text='rank:N'
        )

        trend_chart = (bars + labels).properties(
            title="🔥Top 5 Trending Products",
            width=280,
            height=350
        )

        row1_col2.altair_chart(trend_chart, use_container_width=True)

    except Exception as e:
        row1_col2.error(f"Failed to analyze trend data using LLM: {e}")

    # Word Cloud from Survey Feedback - row 2, col 1
    try:
        survey_text = load_survey_text(st.session_state.file_paths["survey"])
        product_mentions = analyze_survey_with_llm(survey_text)

        if not product_mentions:
            row2_col1.warning("No product mentions found or failed to parse survey feedback.")

        # Generate and show word cloud inside column
        wordcloud = WordCloud(
            width=200,
            height=200,
            background_color="white",
            colormap="viridis",
            collocations=False
        ).generate_from_frequencies(product_mentions)

        fig, ax = plt.subplots(figsize=(8, 5))
        ax.imshow(wordcloud, interpolation="bilinear")
        ax.axis("off")

        row2_col1.markdown("###### 💬 Survey Wordcloud")
        row2_col1.pyplot(fig)

    except Exception as e:
        row2_col1.error(f"Failed to generate product word cloud from survey feedback: {e}")

    # Top Popular Products Among Competitors - row 2, col 2
    try:
        competitor_df = load_competitor_data(st.session_state.file_paths["competitor"])

        if "name" not in competitor_df.columns:
            row2_col2.warning("Competitor file must contain a 'name' column.")
        else:
            # Count the occurrences of each product name
            top_competitor_products = (
                competitor_df["name"]
                .value_counts()
                .reset_index()
                .rename(columns={"name": "product", "count": "frequency"})
                .head(5)
            )
            top_competitor_products["product"] = top_competitor_products["product"].astype(str)
            top_competitor_products["frequency"] = top_competitor_products["frequency"].astype(int)

            # Create the Altair bar chart
            competitor_chart = (
                alt.Chart(top_competitor_products)
                .mark_bar(color="#1f77b4")
                .encode(
                    x=alt.X("product:N", sort="-y", title="Product Name"),
                    y=alt.Y("frequency:Q", title="Number of Listings"),
                    tooltip=["product", "frequency"]
                )
                .properties(
                    title="🛒 Top 5 Popular Products Among Competitors",
                    width=380,
                    height=450
                )
            )

            row2_col2.altair_chart(competitor_chart, use_container_width=True)

        st.session_state.show_data_viz = True
    except Exception as e:
        row2_col2.error(f"Failed to analyze competitor data: {e}")

if st.session_state.show_data_viz:
    row1_col1, row1_col2 = st.columns(2)
    row2_col1, row2_col2 = st.columns(2)

# --- Step 5: Run Assortment Engine ---
st.subheader("5. Run Assortment Engine")
if st.button("🚀 Run Assortment Engine"):
    if "file_paths" not in st.session_state:
        st.error("Please process the files before running the engine.")
    else:
        state = {
            "store_id": store_id,
            "profile": {
                "region": region,
                "school_type": school_type,
                "themes": themes
            },
            "file_inputs": st.session_state.file_paths
        }

        try:
            st.session_state.final_state = assortment_workflow.invoke(state)
            st.success("✅ Assortment Generated!")
        except Exception as e:
            st.error(f"❌ Failed to run engine: {e}")
            st.text("Detailed traceback:")
            st.text(traceback.format_exc())

# --- Step 6: Show Results & Feedback ---
if st.session_state.final_state:
    current_output = st.session_state.final_state["final_output"]

    st.subheader("📦 Suggested Products")
    for product, score in current_output["products"]:
        st.markdown(f"- **{product}** (Score: {score})")

    st.subheader("📄 Rationale")
    st.markdown(current_output["rationale"])

    st.subheader("🗣️ Ask Your Assistant")
    st.session_state.feedback_text = st.text_area(
        "Suggest changes (e.g., 'remove bed', 'add lamp') or ask a question",
        value=st.session_state.feedback_text,
        key="feedback_input"
    )

    if st.button("🔁 Apply Feedback with AI"):
        feedback = st.session_state.feedback_text.strip()
        if not feedback:
            st.warning("Please enter some feedback before applying.")
        else:
            try:
                whole_state = st.session_state.final_state
                current_output = whole_state["final_output"]
                updated_output = apply_feedback_to_output(whole_state, current_output, feedback)

                # Normalize both to list of tuples before comparison
                def to_tuple_list(products):
                    return [tuple(p) for p in products]

                current_products = to_tuple_list(current_output["products"])
                updated_products = to_tuple_list(updated_output["products"])

                # Compare normalized products
                if updated_products != current_products:
                    st.session_state.final_state["final_output"] = updated_output
                    st.success("✅ Product list updated based on your feedback.")

                    st.subheader("📦 Updated Products")
                    for product, score in updated_products:
                        st.markdown(f"- **{product}** (Score: {score})")
                else:
                    st.success("💬 Feedback received. No changes made to the product list.")

                st.subheader("📄 Updated Rationale")
                st.markdown(updated_output["rationale"])

            except Exception as e:
                st.error(f"Feedback processing failed: {e}")

    # --- Optional: Download Updated Results ---
    export_df = pd.DataFrame(
        st.session_state.final_state["final_output"]["products"],
        columns=["Product", "Score"]
    )
    export_path = os.path.join("outputs", f"{store_id}_updated_assortment.csv")
    os.makedirs("outputs", exist_ok=True)
    export_df.to_csv(export_path, index=False)
    with open(export_path, "rb") as f:
        st.download_button("⬇️ Download Updated Results", f, file_name=f"{store_id}_updated_assortment.csv")
