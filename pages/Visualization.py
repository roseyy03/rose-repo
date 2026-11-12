
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# --------------------------------------------------
# 1. PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Malaysian District Data Visualisation",
    page_icon="📊",
    layout="wide"
)

st.title("Malaysian District Data Visualisation")
st.write(
    "Explore differences in household income, population "
    "and school distribution across Malaysian districts."
)

# --------------------------------------------------
# 2. LOAD DATASET
# --------------------------------------------------

@st.cache_data
def load_data():
    file_path = Path(__file__).resolve().parent.parent / "merged_dataset.csv"
    data = pd.read_csv(file_path)

    # Convert numerical columns
    numerical_columns = [
        "year", "income_median", "population", "schools"
    ]

    for column in numerical_columns:
        data[column] = pd.to_numeric(data[column], errors="coerce")

    return data


df = load_data()

# Check required columns
required_columns = [
    "district", "state", "year",
    "income_median", "population", "schools"
]

missing_columns = [
    col for col in required_columns if col not in df.columns
]

if missing_columns:
    st.error(f"Missing columns in dataset: {missing_columns}")
    st.stop()

# --------------------------------------------------
# 3. SIDEBAR FILTERS
# --------------------------------------------------

st.sidebar.header("Data Filters")

years = sorted(df["year"].dropna().unique())

if not years:
    st.error("No valid year values found in the dataset.")
    st.stop()

selected_year = st.sidebar.selectbox(
    "Select Year",
    years,
    index=len(years) - 1
)

states = sorted(df["state"].dropna().unique())

selected_state = st.sidebar.selectbox(
    "Select State",
    ["All States"] + states
)

# Apply filters
filtered_df = df[df["year"] == selected_year].copy()

if selected_state != "All States":
    filtered_df = filtered_df[
        filtered_df["state"] == selected_state
    ]

if filtered_df.empty:
    st.warning("No data available for the selected filters.")
    st.stop()

st.caption(
    f"Selected year: {int(selected_year)} | "
    f"Selected state: {selected_state}"
)

# --------------------------------------------------
# 4. SUMMARY BOX FUNCTION
# --------------------------------------------------

def summary_box(data, column, title, unit="", decimal=0):

    valid_data = data.dropna(subset=[column])

    if valid_data.empty:
        st.warning(f"No valid data available for {title}.")
        return

    highest = valid_data.loc[valid_data[column].idxmax()]
    lowest = valid_data.loc[valid_data[column].idxmin()]

    with st.container(border=True):
        st.subheader(f"{title} Summary ({int(selected_year)})")

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                label=f"Highest - {highest['district']}",
                value=f"{unit}{highest[column]:,.{decimal}f}"
            )

        with col2:
            st.metric(
                label=f"Lowest - {lowest['district']}",
                value=f"{unit}{lowest[column]:,.{decimal}f}"
            )

        st.write(
            f"The difference between the highest and lowest "
            f"district values is "
            f"{unit}{highest[column] - lowest[column]:,.{decimal}f}."
        )


# --------------------------------------------------
# 5. CREATE THREE OBJECTIVE TABS
# --------------------------------------------------

income_tab, population_tab, schools_tab = st.tabs([
    "💰 Household Income",
    "👥 Population",
    "🏫 School Distribution"
])


# ==================================================
# PAGE 1: HOUSEHOLD INCOME
# ==================================================

with income_tab:

    st.header("Objective 1: Median Household Income")

    st.write(
        "To analyze the distribution of median household "
        "income across Malaysian districts and identify "
        "differences between districts."
    )

    # Summary box
    summary_box(
        filtered_df,
        "income_median",
        "Median Household Income",
        unit="RM",
        decimal=0
    )

    income_data = filtered_df.dropna(
        subset=["district", "income_median"]
    )

    st.subheader("Visualisation 1: Median Household Income by District")

    income_sorted = income_data.sort_values(
        "income_median", ascending=True
    )

    fig1 = px.bar(
        income_sorted,
        x="income_median",
        y="district",
        color="state",
        orientation="h",
        title="Median Household Income Across Districts",
        labels={
            "income_median": "Median Household Income (RM)",
            "district": "District",
            "state": "State"
        },
        hover_data=["state"]
    )

    fig1.update_layout(height=max(600, len(income_sorted) * 18))
    st.plotly_chart(fig1, use_container_width=True)

    st.caption(
        "The bar chart compares median household income "
        "between districts and highlights the highest and lowest values."
    )

    st.subheader("Visualisation 2: Income Distribution")

    fig2 = px.histogram(
        income_data,
        x="income_median",
        nbins=20,
        title="Distribution of Median Household Income",
        labels={
            "income_median": "Median Household Income (RM)"
        },
        color_discrete_sequence=["#3498DB"]
    )

    fig2.update_layout(
        xaxis_title="Median Household Income (RM)",
        yaxis_title="Number of Districts"
    )

    st.plotly_chart(fig2, use_container_width=True)

    st.caption(
        "The histogram shows how median household income "
        "values are distributed across Malaysian districts."
    )

    st.subheader("Visualisation 3: Income Variation by State")

    fig3 = px.box(
        income_data,
        x="state",
        y="income_median",
        color="state",
        title="Variation in Median Household Income by State",
        labels={
            "state": "State",
            "income_median": "Median Household Income (RM)"
        }
    )

    fig3.update_layout(showlegend=False)

    st.plotly_chart(fig3, use_container_width=True)

    st.caption(
        "The box plot compares income variation across states "
        "and helps identify potential outliers."
    )

    st.subheader("Interpretation and Discussion")

    st.write(
        "The bar chart identifies differences in median household "
        "income between districts. The histogram illustrates the "
        "overall income distribution, while the box plot compares "
        "income variation across states. Together, these charts "
        "provide an overview of district-level income inequality."
    )


# ==================================================
# PAGE 2: POPULATION
# ==================================================

with population_tab:

    st.header("Objective 2: Population Distribution")

    st.write(
        "To examine population distribution across Malaysian "
        "districts and identify districts with the largest "
        "and smallest populations."
    )

    # Summary box
    summary_box(
        filtered_df,
        "population",
        "Population Distribution",
        unit="",
        decimal=1
    )

    population_data = filtered_df.dropna(
        subset=["district", "state", "population"]
    )

    st.subheader("Visualisation 1: Population by District")

    population_sorted = population_data.sort_values(
        "population", ascending=True
    )

    fig4 = px.bar(
        population_sorted,
        x="population",
        y="district",
        color="state",
        orientation="h",
        title="Population Across Malaysian Districts",
        labels={
            "population": "Population (Thousands)",
            "district": "District",
            "state": "State"
        }
    )

    fig4.update_layout(height=max(600, len(population_sorted) * 18))
    st.plotly_chart(fig4, use_container_width=True)

    st.caption(
        "The bar chart compares population sizes and identifies "
        "the most and least populated districts."
    )

    st.subheader("Visualisation 2: Population Distribution")

    fig5 = px.histogram(
        population_data,
        x="population",
        nbins=20,
        title="Distribution of Population Across Districts",
        labels={
            "population": "Population (Thousands)"
        },
        color_discrete_sequence=["#2ECC71"]
    )

    fig5.update_layout(
        xaxis_title="Population (Thousands)",
        yaxis_title="Number of Districts"
    )

    st.plotly_chart(fig5, use_container_width=True)

    st.caption(
        "The histogram shows the frequency distribution "
        "of population sizes across districts."
    )

    st.subheader("Visualisation 3: Population Treemap")

    fig6 = px.treemap(
        population_data,
        path=["state", "district"],
        values="population",
        title="Population Distribution by State and District",
        color="population",
        color_continuous_scale="Blues"
    )

    st.plotly_chart(fig6, use_container_width=True)

    st.caption(
        "The treemap represents population size using rectangle "
        "areas. Larger rectangles indicate more populated districts."
    )

    st.subheader("Interpretation and Discussion")

    st.write(
        "The bar chart identifies districts with the largest "
        "and smallest populations. The histogram demonstrates "
        "whether population is concentrated in a small number "
        "of districts. The treemap provides a visual comparison "
        "of population sizes across states and their districts."
    )


# ==================================================
# PAGE 3: SCHOOL DISTRIBUTION
# ==================================================

with schools_tab:

    st.header("Objective 3: School Distribution")

    st.write(
        "To visualize the distribution of schools across Malaysian "
        "districts and identify differences in school infrastructure "
        "between districts."
    )

    # Summary box
    summary_box(
        filtered_df,
        "schools",
        "School Distribution",
        unit="",
        decimal=0
    )

    school_data = filtered_df.dropna(
        subset=["district", "schools"]
    )

    st.subheader("Visualisation 1: Number of Schools by District")

    school_sorted = school_data.sort_values(
        "schools", ascending=True
    )

    fig7 = px.bar(
        school_sorted,
        x="schools",
        y="district",
        color="state",
        orientation="h",
        title="Number of Schools Across Malaysian Districts",
        labels={
            "schools": "Number of Schools",
            "district": "District",
            "state": "State"
        }
    )

    fig7.update_layout(height=max(600, len(school_sorted) * 18))
    st.plotly_chart(fig7, use_container_width=True)

    st.caption(
        "The bar chart compares the number of schools "
        "recorded in each district."
    )

    st.subheader("Visualisation 2: Distribution of Schools")

    fig8 = px.histogram(
        school_data,
        x="schools",
        nbins=20,
        title="Distribution of School Counts Across Districts",
        labels={
            "schools": "Number of Schools"
        },
        color_discrete_sequence=["#E67E22"]
    )

    fig8.update_layout(
        xaxis_title="Number of Schools",
        yaxis_title="Number of Districts"
    )

    st.plotly_chart(fig8, use_container_width=True)

    st.caption(
        "The histogram shows how school counts are distributed "
        "among Malaysian districts."
    )

    st.subheader("Visualisation 3: Population versus Number of Schools")

    scatter_data = filtered_df.dropna(
        subset=["district", "state", "population", "schools"]
    )

    fig9 = px.scatter(
        scatter_data,
        x="population",
        y="schools",
        color="state",
        hover_name="district",
        title="Relationship Between Population and Number of Schools",
        labels={
            "population": "Population (Thousands)",
            "schools": "Number of Schools",
            "state": "State"
        }
    )

    fig9.update_traces(marker=dict(size=9, opacity=0.75))

    st.plotly_chart(fig9, use_container_width=True)

    st.caption(
        "The scatter plot explores whether districts with larger "
        "populations also tend to have more schools."
    )

    st.subheader("Interpretation and Discussion")

    st.write(
        "The bar chart identifies districts with the most and "
        "fewest schools. The histogram illustrates differences "
        "in school counts, while the scatter plot explores the "
        "relationship between population size and school numbers. "
        "A positive relationship would suggest that more populated "
        "districts generally have more schools, although school "
        "counts alone do not measure educational accessibility."
    )


# --------------------------------------------------
# 6. DATASET PREVIEW
# --------------------------------------------------

with st.expander("View Merged Dataset"):

    st.dataframe(
        filtered_df[
            [
                "state",
                "district",
                "year",
                "income_median",
                "population",
                "schools"
            ]
        ],
        use_container_width=True
    )

# --------------------------------------------------
# 7. DATA SOURCE
# --------------------------------------------------

st.divider()

st.caption(
    "Data sources: OpenDOSM and the education dataset used "
    "for this project. Population is expressed in thousands. "
    "School counts represent the institutions included in "
    "the selected education dataset."
)
