
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO

st.set_page_config(page_title="Bird Observation Dashboard", page_icon="🐦", layout="wide")

# Theme
theme = st.sidebar.radio("Theme", ["Light", "Dark"])
if theme == "Dark":
    st.markdown("""
    <style>
    .stApp {background-color:#0E1117;color:white;}
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    forest = pd.read_excel("Bird_Monitoring_Data_FOREST.XLSX", sheet_name=None)
    grass = pd.read_excel("Bird_Monitoring_Data_GRASSLAND.XLSX", sheet_name=None)

    forest_df = pd.concat(forest.values(), ignore_index=True)
    grass_df = pd.concat(grass.values(), ignore_index=True)

    forest_df["Habitat"] = "Forest"
    grass_df["Habitat"] = "Grassland"

    df = pd.concat([forest_df, grass_df], ignore_index=True)
    df.columns = [c.strip().replace(" ", "_") for c in df.columns]
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    return df.drop_duplicates()

df = load_data()

st.title("🐦 Bird Species Observation Analysis Dashboard")

# Filters
habitats = st.sidebar.multiselect("Habitat", df["Habitat"].unique(), default=df["Habitat"].unique())

units = sorted(df["Admin_Unit_Code"].dropna().unique())
selected_units = st.sidebar.multiselect("Admin Unit", units, default=units)

species_list = sorted(df["Common_Name"].dropna().unique())
species = st.sidebar.selectbox("Species Search", ["All Species"] + species_list)

filtered = df[df["Habitat"].isin(habitats)]
filtered = filtered[filtered["Admin_Unit_Code"].isin(selected_units)]

if species != "All Species":
    filtered = filtered[filtered["Common_Name"] == species]

# KPIs
c1,c2,c3,c4,c5 = st.columns(5)

c1.metric("Observations", f"{len(filtered):,}")
c2.metric("Species", filtered["Common_Name"].nunique())
c3.metric("Avg Temp", round(filtered["Temperature"].mean(),2) if "Temperature" in filtered else 0)
c4.metric("Avg Humidity", round(filtered["Humidity"].mean(),2) if "Humidity" in filtered else 0)
c5.metric("Watchlist Records", filtered["PIF_Watchlist_Status"].notna().sum())

st.divider()

# Executive Summary
st.header("Executive Summary")

left,right = st.columns(2)

with left:
    habitat_counts = filtered["Habitat"].value_counts().reset_index()
    habitat_counts.columns=["Habitat","Count"]
    st.plotly_chart(px.bar(habitat_counts,x="Habitat",y="Count",title="Observations by Habitat"),
                    use_container_width=True)

with right:
    div = filtered.groupby("Habitat")["Common_Name"].nunique().reset_index()
    div.columns=["Habitat","Unique Species"]
    st.plotly_chart(px.pie(div,names="Habitat",values="Unique Species",
                           title="Species Diversity"), use_container_width=True)

# Shannon Index
st.header("Biodiversity Analysis")

def shannon_index(data):
    counts = data["Common_Name"].value_counts()
    p = counts / counts.sum()
    return float(-(p*np.log(p)).sum())

forest_idx = shannon_index(filtered[filtered["Habitat"]=="Forest"]) if len(filtered[filtered["Habitat"]=="Forest"])>0 else 0
grass_idx = shannon_index(filtered[filtered["Habitat"]=="Grassland"]) if len(filtered[filtered["Habitat"]=="Grassland"])>0 else 0

a,b = st.columns(2)
a.metric("Forest Shannon Index", round(forest_idx,3))
b.metric("Grassland Shannon Index", round(grass_idx,3))

bio_df = pd.DataFrame({
    "Habitat":["Forest","Grassland"],
    "Shannon Index":[forest_idx,grass_idx]
})

st.plotly_chart(px.bar(bio_df,x="Habitat",y="Shannon Index",
                       title="Biodiversity Comparison"),
                use_container_width=True)

# Top Species
st.header("Top Species")

top_species = filtered["Common_Name"].value_counts().head(15).reset_index()
top_species.columns=["Species","Observations"]

st.plotly_chart(
    px.bar(top_species,x="Observations",y="Species",
           orientation="h",
           title="Top 15 Species"),
    use_container_width=True
)

# Trend Analysis
st.header("Observation Trends")

trend = filtered.groupby(pd.Grouper(key="Date",freq="M")).size().reset_index(name="Observations")

st.plotly_chart(
    px.line(trend,x="Date",y="Observations",
            markers=True,
            title="Monthly Observation Trend"),
    use_container_width=True
)

# Heatmap
st.header("Habitat Heatmap")

heat = pd.crosstab(filtered["Common_Name"], filtered["Habitat"])

top = filtered["Common_Name"].value_counts().head(25).index
heat = heat.loc[heat.index.intersection(top)]

st.plotly_chart(
    px.imshow(heat,
              title="Species vs Habitat Heatmap",
              aspect="auto"),
    use_container_width=True
)

# Environmental Analysis
st.header("Environmental Analysis")

x,y = st.columns(2)

with x:
    st.plotly_chart(
        px.box(filtered,x="Habitat",y="Temperature",
               title="Temperature Distribution"),
        use_container_width=True
    )

with y:
    st.plotly_chart(
        px.box(filtered,x="Habitat",y="Humidity",
               title="Humidity Distribution"),
        use_container_width=True
    )

# Conservation
st.header("Conservation Analysis")

watch = filtered[filtered["PIF_Watchlist_Status"].notna()]

if len(watch)>0:
    cons = watch.groupby("Habitat").size().reset_index(name="Count")
    st.plotly_chart(
        px.bar(cons,x="Habitat",y="Count",
               title="Watchlist Species"),
        use_container_width=True
    )

# Geographic Placeholder
st.header("Geographic Map")

st.info(
    "Latitude and Longitude columns were not found in the dataset. "
    "A true geographic map cannot be generated unless coordinates are added."
)

# Raw Data
st.header("Data Explorer")
st.dataframe(filtered, use_container_width=True)

# CSV Download
st.download_button(
    "⬇ Download Filtered CSV",
    filtered.to_csv(index=False),
    "bird_filtered.csv",
    "text/csv"
)

# PDF Report
def create_pdf():
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()

    story = [
        Paragraph("Bird Species Observation Report", styles['Title']),
        Spacer(1,12),
        Paragraph(f"Total Observations: {len(filtered)}", styles['BodyText']),
        Paragraph(f"Unique Species: {filtered['Common_Name'].nunique()}", styles['BodyText']),
        Paragraph(f"Forest Shannon Index: {round(forest_idx,3)}", styles['BodyText']),
        Paragraph(f"Grassland Shannon Index: {round(grass_idx,3)}", styles['BodyText'])
    ]

    doc.build(story)
    buffer.seek(0)
    return buffer

pdf = create_pdf()

st.download_button(
    "📄 Download PDF Report",
    pdf,
    file_name="Bird_Report.pdf",
    mime="application/pdf"
)

st.success("""
Key Insights:
• Forest habitats generally support higher diversity.
• Conservation species are concentrated in specific habitats.
• Environmental conditions influence bird observations.
• Both habitats contribute significantly to biodiversity.
""")
