
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# =====================================================
# 1. PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="Malaysia District Explorer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# 2. CUSTOM DESIGN
# =====================================================

st.markdown("""
<style>
    .main-title {
        font-size: 32px;
        font-weight: 750;
        color: #2563EB;
        margin-bottom: 4px;
    }
    .subtitle {
        color: #64748B;
        font-size: 15px;
        margin-bottom: 22px;
    }
    div[data-testid="stMetric"] {
        background-color: rgba(128,128,128,0.08);
        padding: 16px;
        border-radius: 12px;
        border: 1px solid rgba(128,128,128,0.18);
    }
    .section-note {
        color: #64748B;
        font-size: 13px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="main-title">Malaysia District Data Explorer</div>',
    unsafe_allow_html=True
)
st.markdown(
    '<div class="subtitle">Explore household income, population and school distribution across Malaysian districts.</div>',
    unsafe_allow_html=True
)

# =====================================================
# 3. LOAD DATA
# =====================================================

@st.cache_data
def load_data():
    file_path = (
        Path(__file__).resolve().parent.parent
        / "merged_dataset.csv"
    )

    data = pd.read_csv(file_path)

    required = [
        "district", "state", "year",
        "income_median", "population", "schools"
    ]

    missing = [c for c in required if c not in data.columns]

    if missing:
        raise ValueError(f"Missing columns: {missing}")

    for col in ["year", "income_median", "population", "schools"]:
        data[col] = pd.to_numeric(data[col], errors="coerce")

    data["district"] = data["district"].astype("string").str.strip()
    data["state"] = data["state"].astype("string").str.strip()

    return data.dropna(subset=["district", "state", "year"])


try:
    df = load_data()
except Exception as e:
    st.error(f"Unable to load dataset: {e}")
    st.stop()

# =====================================================
# 4. SIDEBAR FILTERS
# =====================================================

st.sidebar.title("🔎 Explore the Data")
st.sidebar.caption("Use these filters to customise all three analyses.")

years = sorted(df["year"].dropna().unique())

selected_year = st.sidebar.selectbox(
    "Select year",
    years,
    index=len(years) - 1,
    format_func=lambda x: str(int(x))
)

available_states = sorted(
    df["state"].dropna().unique().tolist()
)

selected_states = st.sidebar.multiselect(
    "Select states",
    available_states,
    default=available_states,
    help="Choose one or more states. Leave all selected to compare Malaysia."
)

state_filtered = df[
    (df["year"] == selected_year) &
    (df["state"].isin(selected_states))
].copy()

available_districts = sorted(
    state_filtered["district"].dropna().unique().tolist()
)

selected_districts = st.sidebar.multiselect(
    "Select districts",
    available_districts,
    default=[],
    help="Leave empty to include every district in the selected states."
)

if selected_districts:
    data = state_filtered[
        state_filtered["district"].isin(selected_districts)
    ].copy()
else:
    data = state_filtered.copy()

top_n_option = st.sidebar.selectbox(
    "District ranking",
    ["All districts", "Top 10", "Top 20", "Top 30"],
    index=1
)

if top_n_option == "All districts":
    top_n = None
else:
    top_n = int(top_n_option.split()[1])

if st.sidebar.button("↻ Reset all filters", use_container_width=True):
    st.rerun()

st.sidebar.divider()
st.sidebar.caption(
    "Tip: Use the chart hover information, zoom controls and legend "
    "to explore individual districts."
)

if data.empty:
    st.warning("No data matches your selected filters.")
    st.stop()

# =====================================================
# 5. HELPER FUNCTIONS
# =====================================================

def ranking_data(data, column):
    result = (
        data.groupby(["district", "state"], as_index=False)[column]
        .mean()
        .sort_values(column, ascending=False)
    )

    if top_n is not None:
        result = result.head(top_n)

    return result


def summary_box(data, column, title, prefix="", suffix="", decimals=0):
    valid = data.dropna(subset=[column])

    if valid.empty:
        st.warning("No valid values available for this summary.")
        return

    highest = valid.loc[valid[column].idxmax()]
    lowest = valid.loc[valid[column].idxmin()]

    average = valid[column].mean()
    difference = highest[column] - lowest[column]

    st.subheader(f"📌 {title} Summary")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Highest",
        f"{prefix}{highest[column]:,.{decimals}f}{suffix}",
        help=f"District: {highest['district']}, {highest['state']}"
    )

    c2.metric(
        "Lowest",
        f"{prefix}{lowest[column]:,.{decimals}f}{suffix}",
        help=f"District: {lowest['district']}, {lowest['state']}"
    )

    c3.metric(
        "Average",
        f"{prefix}{average:,.{decimals}f}{suffix}"
    )

    c4.metric(
        "Districts",
        f"{valid['district'].nunique():,}"
    )

    st.info(
        f"**Key finding:** {highest['district']} records the highest "
        f"{title.lower()} at {prefix}{highest[column]:,.{decimals}f}{suffix}, "
        f"while {lowest['district']} records the lowest at "
        f"{prefix}{lowest[column]:,.{decimals}f}{suffix}. "
        f"The difference is {prefix}{difference:,.{decimals}f}{suffix}."
    )


def chart_layout(fig, height=480):
    fig.update_layout(
        height=height,
        margin=dict(l=15, r=15, t=65, b=20),
        hovermode="closest",
        legend_title_text="State",
        font=dict(size=12)
    )
    return fig


def show_download(data, key, filename):
    """Display a CSV download button with a unique Streamlit key."""
    csv = data.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="⬇ Download filtered data (CSV)",
        data=csv,
        file_name=filename,
        mime="text/csv",
        key=key
    )


# =====================================================
# 6. OVERVIEW METRICS
# =====================================================

st.subheader("📊 Dataset Overview")

m1, m2, m3 = st.columns(3)

m1.metric(
    "Districts Covered",
    data["district"].nunique()
)

m2.metric(
    "Average District Median Income",
    f"RM {data['income_median'].mean():,.0f}"
)

m3.metric(
    "Total Population",
    f"{data['population'].sum():,.1f} K"
)

st.caption(
    f"Showing {len(data):,} records for {int(selected_year)} "
    f"across {data['state'].nunique()} selected states."
)

st.divider()

# =====================================================
# 7. OBJECTIVE TABS
# =====================================================

income_tab, population_tab, school_tab = st.tabs([
    "💰 Income Analysis",
    "👥 Population Analysis",
    "🏫 School Distribution"
])

# =====================================================
# TAB 1: INCOME
# =====================================================

with income_tab:

    st.header("Household Income")

    st.write(
        "To analyze the distribution of median household income "
        "across Malaysian districts and identify differences between districts."
    )

    summary_box(
        data, "income_median",
        "Median Household Income",
        prefix="RM ", decimals=0
    )

    st.divider()

    income = data.dropna(
        subset=["district", "state", "income_median"]
    )

    st.subheader("1. Median Household Income by District")

    income_rank = ranking_data(income, "income_median")

    bar_orientation = st.radio(
        "Choose chart orientation",
        ["Horizontal", "Vertical"],
        horizontal=True,
        key="income_orientation"
    )

    if bar_orientation == "Horizontal":
        fig = px.bar(
            income_rank.sort_values("income_median"),
            x="income_median",
            y="district",
            color="state",
            orientation="h",
            hover_data=["state"],
            labels={
                "income_median": "Median Income (RM)",
                "district": "District"
            }
        )
    else:
        fig = px.bar(
            income_rank,
            x="district",
            y="income_median",
            color="state",
            hover_data=["state"],
            labels={
                "income_median": "Median Income (RM)",
                "district": "District"
            }
        )

    st.plotly_chart(chart_layout(fig, 600), use_container_width=True)

    st.caption(
        "Use the orientation control to change the chart layout. "
        "Hover over a bar to inspect its exact value."
    )

    st.divider()

    left, right = st.columns(2)

    with left:
        st.subheader("2. Income Distribution")

        bins = st.slider(
            "Number of income intervals",
            5, 40, 20,
            key="income_bins"
        )

        fig = px.histogram(
            income,
            x="income_median",
            nbins=bins,
            color_discrete_sequence=["#3182CE"],
            labels={"income_median": "Median Income (RM)"}
        )

        fig.update_layout(
            xaxis_title="Median Household Income (RM)",
            yaxis_title="Number of Districts"
        )

        st.plotly_chart(chart_layout(fig, 420), use_container_width=True)

    with right:
        st.subheader("3. Income Variation by State")

        fig = px.box(
            income,
            x="state",
            y="income_median",
            color="state",
            points="outliers",
            labels={
                "state": "State",
                "income_median": "Median Income (RM)"
            }
        )

        fig.update_layout(showlegend=False)

        st.plotly_chart(chart_layout(fig, 420), use_container_width=True)

    with st.expander("📖 Read income interpretation"):
        st.write(
            "The bar chart identifies differences in median household "
            "income between districts. The histogram shows the overall "
            "distribution of district income values, while the box plot "
            "compares the spread of district incomes across states and "
            "highlights potential outliers."
        )

    with st.expander("View income data"):
        st.dataframe(
            income[
                ["state", "district", "income_median"]
            ],
            use_container_width=True,
            hide_index=True
        )

    show_download(
        income,
        key="download_income_csv",
        filename=f"income_data_{int(selected_year)}.csv"
    )


# =====================================================
# TAB 2: POPULATION
# =====================================================

with population_tab:

    st.header("Population Distribution")

    st.write(
        "To examine population distribution across Malaysian districts "
        "and identify districts with the largest and smallest populations."
    )

    summary_box(
        data, "population",
        "Population",
        suffix=" K", decimals=1
    )

    st.divider()

    population = data.dropna(
        subset=["district", "state", "population"]
    )

    st.subheader("1. Population by District")

    population_rank = ranking_data(population, "population")

    fig = px.bar(
        population_rank.sort_values("population"),
        x="population",
        y="district",
        color="state",
        orientation="h",
        hover_data=["state"],
        labels={
            "population": "Population (K)",
            "district": "District"
        }
    )

    st.plotly_chart(chart_layout(fig, 600), use_container_width=True)

    st.caption(
        "Districts are ranked by population. Hover over the bars "
        "to see the population value and state."
    )

    st.divider()

    left, right = st.columns(2)

    with left:
        st.subheader("2. Population Distribution")

        bins = st.slider(
            "Number of population intervals",
            5, 40, 20,
            key="population_bins"
        )

        fig = px.histogram(
            population,
            x="population",
            nbins=bins,
            color_discrete_sequence=["#16A085"],
            labels={"population": "Population (K)"}
        )

        fig.update_layout(
            xaxis_title="Population (K)",
            yaxis_title="Number of Districts"
        )

        st.plotly_chart(chart_layout(fig, 420), use_container_width=True)

    with right:
        st.subheader("3. Population Treemap")

        fig = px.treemap(
            population,
            path=["state", "district"],
            values="population",
            color="population",
            color_continuous_scale="Blues",
            hover_data=["population"],
            labels={"population": "Population (K)"}
        )

        st.plotly_chart(chart_layout(fig, 420), use_container_width=True)

    with st.expander("📖 Read population interpretation"):
        st.write(
            "The bar chart identifies the most and least populated "
            "districts. The histogram reveals the distribution of "
            "population sizes, while the treemap compares the relative "
            "population sizes of districts grouped by state."
        )

    with st.expander("View population data"):
        st.dataframe(
            population[
                ["state", "district", "population"]
            ],
            use_container_width=True,
            hide_index=True
        )

    show_download(
        population,
        key="download_population_csv",
        filename=f"population_data_{int(selected_year)}.csv"
    )


# =====================================================
# TAB 3: SCHOOLS
# =====================================================

with school_tab:

    st.header("School Distribution")

    st.write(
        "To visualize the distribution of schools across Malaysian "
        "districts and identify differences in school infrastructure."
    )

    summary_box(
        data, "schools",
        "Number of Schools",
        decimals=0
    )

    st.divider()

    schools = data.dropna(
        subset=["district", "state", "schools"]
    )

    st.subheader("1. Number of Schools by District")

    school_rank = ranking_data(schools, "schools")

    fig = px.bar(
        school_rank.sort_values("schools"),
        x="schools",
        y="district",
        color="state",
        orientation="h",
        hover_data=["state"],
        labels={
            "schools": "Number of Schools",
            "district": "District"
        }
    )

    st.plotly_chart(chart_layout(fig, 600), use_container_width=True)

    st.caption(
        "Compare the number of schools between districts. "
        "Hover over a bar to see its exact value."
    )

    st.divider()

    left, right = st.columns(2)

    with left:
        st.subheader("2. Distribution of Schools")

        bins = st.slider(
            "Number of school-count intervals",
            5, 40, 20,
            key="school_bins"
        )

        fig = px.histogram(
            schools,
            x="schools",
            nbins=bins,
            color_discrete_sequence=["#E67E22"],
            labels={"schools": "Number of Schools"}
        )

        fig.update_layout(
            xaxis_title="Number of Schools",
            yaxis_title="Number of Districts"
        )

        st.plotly_chart(chart_layout(fig, 420), use_container_width=True)

    with right:
        st.subheader("3. Population versus Schools")

        scatter = data.dropna(
            subset=["district", "state", "population", "schools"]
        )

        fig = px.scatter(
            scatter,
            x="population",
            y="schools",
            color="state",
            hover_name="district",
            hover_data=["population", "schools"],
            labels={
                "population": "Population (K)",
                "schools": "Number of Schools"
            }
        )

        fig.update_traces(
            marker=dict(size=10, opacity=0.75)
        )

        st.plotly_chart(chart_layout(fig, 420), use_container_width=True)

    with st.expander("📖 Read school interpretation"):
        st.write(
            "The bar chart identifies districts with the highest "
            "and lowest school counts. The histogram shows how school "
            "numbers are distributed across districts. The scatter plot "
            "explores whether districts with larger populations also "
            "tend to have more schools. A larger school count does not "
            "necessarily mean that educational access is sufficient."
        )

    with st.expander("View school data"):
        st.dataframe(
            schools[
                ["state", "district", "schools"]
            ],
            use_container_width=True,
            hide_index=True
        )

    show_download(
        schools,
        key="download_schools_csv",
        filename=f"schools_data_{int(selected_year)}.csv"
    )


# =====================================================
# 8. FOOTER
# =====================================================

st.divider()

st.caption(
    "Data sources: OpenDOSM and the education dataset used in this project. "
    "Population values are expressed in thousands. School counts represent "
    "the institutions included in the selected education dataset."
)
