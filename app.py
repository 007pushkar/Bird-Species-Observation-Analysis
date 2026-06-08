
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Bird Species Observation Analysis",
    page_icon="🦜",
    layout="wide"
)

st.title("🦜 Bird Species Observation Analysis")
st.markdown("Analyze bird monitoring data from Forest and Grassland habitats.")

# ---------------------------
# Load Dataset
# ---------------------------
@st.cache_data
def load_data():
    forest = pd.read_excel("Bird_Monitoring_Data_FOREST.xlsx")
    grassland = pd.read_excel("Bird_Monitoring_Data_GRASSLAND.xlsx")

    forest["Habitat"] = "Forest"
    grassland["Habitat"] = "Grassland"

    data = pd.concat([forest, grassland], ignore_index=True)
    return data

try:
    df = load_data()

    st.success("Datasets loaded successfully!")

    # ---------------------------
    # Sidebar Filters
    # ---------------------------
    st.sidebar.header("Filter Data")

    habitat_filter = st.sidebar.multiselect(
        "Select Habitat",
        options=df["Habitat"].unique(),
        default=df["Habitat"].unique()
    )

    year_filter = st.sidebar.multiselect(
        "Select Year",
        options=sorted(df["Year"].dropna().unique()),
        default=sorted(df["Year"].dropna().unique())
    )

    filtered_df = df[
        (df["Habitat"].isin(habitat_filter)) &
        (df["Year"].isin(year_filter))
    ]

    # ---------------------------
    # Basic Information
    # ---------------------------
    st.subheader("Dataset Overview")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Records", len(filtered_df))

    with col2:
        st.metric("Unique Bird Species",
                  filtered_df["Common_Name"].nunique())

    with col3:
        st.metric("Observers",
                  filtered_df["Observer"].nunique())

    st.write("### Preview of Dataset")
    st.dataframe(filtered_df.head())

    # ---------------------------
    # Species Distribution
    # ---------------------------
    st.subheader("Top 10 Most Observed Bird Species")

    species_count = (
        filtered_df["Common_Name"]
        .value_counts()
        .head(10)
    )

    fig1, ax1 = plt.subplots(figsize=(10, 5))
    species_count.plot(kind="bar", ax=ax1)

    ax1.set_xlabel("Bird Species")
    ax1.set_ylabel("Observation Count")
    ax1.set_title("Top 10 Bird Species")

    st.pyplot(fig1)

    # ---------------------------
    # Habitat Distribution
    # ---------------------------
    st.subheader("Habitat Distribution")

    habitat_count = filtered_df["Habitat"].value_counts()

    fig2, ax2 = plt.subplots(figsize=(6, 6))
    habitat_count.plot(kind="pie", autopct="%1.1f%%", ax=ax2)

    ax2.set_ylabel("")
    ax2.set_title("Forest vs Grassland Observations")

    st.pyplot(fig2)

    # ---------------------------
    # Weather Analysis
    # ---------------------------
    st.subheader("Weather Condition Analysis")

    weather_col = st.selectbox(
        "Select Weather Parameter",
        ["Temperature", "Humidity", "Wind"]
    )

    weather_data = (
        filtered_df[weather_col]
        .value_counts()
        .head(10)
    )

    fig3, ax3 = plt.subplots(figsize=(10, 5))
    weather_data.plot(kind="bar", ax=ax3)

    ax3.set_xlabel(weather_col)
    ax3.set_ylabel("Count")
    ax3.set_title(f"{weather_col} Distribution")

    st.pyplot(fig3)

    # ---------------------------
    # Observation by Year
    # ---------------------------
    st.subheader("Observations by Year")

    year_data = filtered_df["Year"].value_counts().sort_index()

    fig4, ax4 = plt.subplots(figsize=(8, 4))
    year_data.plot(kind="line", marker="o", ax=ax4)

    ax4.set_xlabel("Year")
    ax4.set_ylabel("Observations")
    ax4.set_title("Year-wise Observations")

    st.pyplot(fig4)

    # ---------------------------
    # Download Processed Data
    # ---------------------------
    st.subheader("Download Filtered Data")

    csv = filtered_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download CSV",
        data=csv,
        file_name="filtered_bird_data.csv",
        mime="text/csv"
    )

except FileNotFoundError:
    st.error(
        "Dataset files not found. "
        "Please keep the Excel files in the same folder as app.py"
    )
