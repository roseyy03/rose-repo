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
                "population": "Population (Thousands)",
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
