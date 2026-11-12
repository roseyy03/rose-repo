from pathlib import Path
import pandas as pd
import streamlit as st
import pandas as pd
import streamlit as st
import plotly.express as px

# ---------------------------------
# PAGE CONFIGURATION
# ---------------------------------

st.set_page_config(
    page_title="District Data Visualization",
    page_icon="📊",
    layout="wide"
)

# ---------------------------------
# LOAD DATASET
# ---------------------------------

@st.cache_data
def load_data():
    # Locate the main project folder
    BASE_DIR = Path(__file__).resolve().parent.parent

    # Locate the CSV file
    DATA_PATH = BASE_DIR / "merged_dataset.csv"

    # Check whether the file exists
    if not DATA_PATH.exists():
        st.error(f"Dataset not found: {DATA_PATH}")
        st.stop()

    # Load the dataset
    data = pd.read_csv(DATA_PATH)

    return data


df = load_data()
# ---------------------------------
# PAGE TITLE
# ---------------------------------

st.title("District Data Visualization")
st.write(
    "An interactive visualization of household income, "
    "population and public education institutions "
    "across Malaysian districts."
)

st.divider()

# ---------------------------------
# SIDEBAR FILTERS
# ---------------------------------

st.sidebar.header("Data Filters")

available_years = sorted(df["year"].dropna().unique())

selected_year = st.sidebar.selectbox(
    "Select Year",
    available_years,
    index=len(available_years) - 1
)

available_states = ["All States"] + sorted(
    df["state"].dropna().unique().tolist()
)

selected_state = st.sidebar.selectbox(
    "Select State",
    available_states
)

# Filter data
filtered_df = df[df["year"] == selected_year].copy()

if selected_state != "All States":
    filtered_df = filtered_df[
        filtered_df["state"] == selected_state
    ]

# ---------------------------------
# SUMMARY BOXES
# ---------------------------------

st.subheader(f"Overview for {selected_year}")

if filtered_df.empty:
    st.warning("No data available for the selected filters.")

else:
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Districts Covered",
            filtered_df["district"].nunique()
        )

    with col2:
        st.metric(
            "Average Median Household Income",
            f"RM {filtered_df['income_median'].mean():,.0f}"
        )

    with col3:
        st.metric(
            "Total Population",
            f"{filtered_df['population'].sum():,.1f} thousand"
        )

    st.divider()

    # ---------------------------------
    # VISUALIZATION 1: HOUSEHOLD INCOME
    # ---------------------------------

    st.header("1. Median Household Income Distribution")

    st.write(
        "Objective: Analyze the distribution of median household "
        "income across Malaysian districts and identify differences "
        "between districts."
    )

    income_data = filtered_df.sort_values(
        "income_median",
        ascending=False
    )

   fig_income = px.bar(
    income_data,
    x="district",
    y="income_median",
    color_discrete_sequence=["#E75480"],
    title="Median Household Income by District",
    labels={
        "district": "District",
        "income_median": "Median Household Income (RM)"
    },
    hover_data=["state", "year"]
)

fig_income.update_layout(
    xaxis_tickangle=-45,
    height=550,
    plot_bgcolor="#FFFFFF",
    paper_bgcolor="#FFFFFF",
    font_color="#374151"
)
    )

    fig_income.update_layout(
        xaxis_tickangle=-45,
        height=550
    )

    st.plotly_chart(fig_income, use_container_width=True)

    highest_income = income_data.iloc[0]
    lowest_income = income_data.iloc[-1]

    st.info(
        f"**Summary:** {highest_income['district']} has the highest "
        f"median household income at RM {highest_income['income_median']:,.0f}, "
        f"while {lowest_income['district']} has the lowest at "
        f"RM {lowest_income['income_median']:,.0f}."
    )

    st.divider()

    # ---------------------------------
    # VISUALIZATION 2: POPULATION
    # ---------------------------------

    st.header("2. Population Distribution")

    st.write(
        "Objective: Examine population distribution across "
        "Malaysian districts and identify districts with the "
        "largest and smallest populations."
    )

    population_data = filtered_df.sort_values(
        "population",
        ascending=False
    )

    fig_population = px.bar(
    population_data,
    x="district",
    y="population",
    color_discrete_sequence=["#8956B3"],
    title="Population by District",
    labels={
        "district": "District",
        "population": "Population (thousand people)"
    },
    hover_data=["state", "year"]
)

fig_population.update_layout(
    xaxis_tickangle=-45,
    height=550,
    plot_bgcolor="#FFFFFF",
    paper_bgcolor="#FFFFFF",
    font_color="#374151"
)
    )

    fig_population.update_layout(
        xaxis_tickangle=-45,
        height=550
    )

    st.plotly_chart(fig_population, use_container_width=True)

    largest_population = population_data.iloc[0]
    smallest_population = population_data.iloc[-1]

    st.info(
        f"**Summary:** {largest_population['district']} has the "
        f"largest population at {largest_population['population']:,.1f} "
        f"thousand people, while {smallest_population['district']} "
        f"has the smallest at "
        f"{smallest_population['population']:,.1f} thousand people."
    )

    st.divider()

    # ---------------------------------
    # VISUALIZATION 3: EDUCATION
    # ---------------------------------

    st.header("3. Public Education Institution Distribution")

    st.write(
        "Objective: Visualize the distribution of public primary "
        "and secondary education institutions across Malaysian "
        "districts and identify differences between districts."
    )

    education_data = filtered_df.sort_values(
        "schools",
        ascending=False
    )

    fig_education = px.bar(
    education_data,
    x="district",
    y="schools",
    color_discrete_sequence=["#269B91"],
    title="Public Education Institutions by District",
    labels={
        "district": "District",
        "schools": "Number of Institutions"
    },
    hover_data=["state", "year"]
)

fig_education.update_layout(
    xaxis_tickangle=-45,
    height=550,
    plot_bgcolor="#FFFFFF",
    paper_bgcolor="#FFFFFF",
    font_color="#374151"
)
    )

    fig_education.update_layout(
        xaxis_tickangle=-45,
        height=550
    )

    st.plotly_chart(fig_education, use_container_width=True)

    highest_schools = education_data.iloc[0]
    lowest_schools = education_data.iloc[-1]

    st.info(
        f"**Summary:** {highest_schools['district']} has the "
        f"highest number of public primary and secondary "
        f"institutions ({highest_schools['schools']:,}), while "
        f"{lowest_schools['district']} has the lowest "
        f"({lowest_schools['schools']:,})."
    )

    # ---------------------------------
    # DATA TABLE
    # ---------------------------------

    st.divider()

    st.subheader("Dataset Preview")

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

    st.caption(
        "Sources: OpenDOSM and Ministry of Education Malaysia. "
        "Population values are expressed in thousands of people. "
        "Education counts represent public primary and secondary "
        "institutions."
    )
