
import pandas as pd
import plotly.express as px
import streamlit as st


AGGREGATIONS = ["sum", "mean", "median", "min", "max", "count"]


def get_column_types(df):
    """Return numeric, categorical, and datetime columns."""
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    datetime_cols = df.select_dtypes(
        include=["datetime", "datetimetz"]
    ).columns.tolist()

    categorical_cols = [
        col for col in df.columns
        if col not in numeric_cols and col not in datetime_cols
    ]

    return numeric_cols, categorical_cols, datetime_cols


def render_visualization_tab(df):
    """Render interactive chart controls and the selected Plotly chart."""

    if df is None or df.empty:
        st.info("Upload a dataset first to create visualizations.")
        return

    numeric_cols, categorical_cols, datetime_cols = get_column_types(df)
    all_cols = df.columns.tolist()

    st.subheader("Visualization Studio")
    st.caption(
        "Explore your dataset using interactive charts. "
        "Chart options adapt to the columns available in your data."
    )

    chart_type = st.selectbox(
        "Choose visualization",
        [
            "Bar Chart",
            "Line Chart",
            "Scatter Plot",
            "Histogram",
            "Box Plot",
            "Pie / Donut Chart",
            "Correlation Heatmap",
        ],
        key="viz_chart_type",
    )

    # ---------------- BAR CHART ----------------
    if chart_type == "Bar Chart":
        if not numeric_cols:
            st.warning("A bar chart requires at least one numeric column.")
            return

        col1, col2 = st.columns(2)

        with col1:
            x_col = st.selectbox(
                "Category / X-axis",
                categorical_cols or all_cols,
                key="bar_x",
            )

        with col2:
            y_col = st.selectbox(
                "Numeric metric / Y-axis",
                numeric_cols,
                key="bar_y",
            )

        agg = st.selectbox(
            "Aggregation",
            AGGREGATIONS,
            index=0,
            key="bar_agg",
        )

        top_n = st.slider(
            "Show top categories",
            min_value=5,
            max_value=50,
            value=15,
            step=5,
            key="bar_top_n",
        )

        grouped = (
            df.groupby(x_col, dropna=False)[y_col]
            .agg(agg)
            .reset_index()
            .sort_values(y_col, ascending=False)
            .head(top_n)
        )

        fig = px.bar(
            grouped,
            x=x_col,
            y=y_col,
            title=f"{agg.title()} of {y_col} by {x_col}",
            text_auto=".2s",
        )

        fig.update_layout(xaxis_title=x_col, yaxis_title=f"{agg}({y_col})")

    # ---------------- LINE CHART ----------------
    elif chart_type == "Line Chart":
        if not numeric_cols:
            st.warning("A line chart requires at least one numeric column.")
            return

        x_options = list(dict.fromkeys(
            datetime_cols + numeric_cols + categorical_cols
        ))

        col1, col2 = st.columns(2)

        with col1:
            x_col = st.selectbox(
                "X-axis",
                x_options,
                key="line_x",
            )

        with col2:
            y_col = st.selectbox(
                "Y-axis metric",
                numeric_cols,
                key="line_y",
            )

        agg = st.selectbox(
            "Aggregation",
            AGGREGATIONS,
            index=1,
            key="line_agg",
        )

        line_df = (
            df.groupby(x_col, dropna=False)[y_col]
            .agg(agg)
            .reset_index()
        )

        if x_col in datetime_cols or pd.api.types.is_numeric_dtype(df[x_col]):
            line_df = line_df.sort_values(x_col)

        fig = px.line(
            line_df,
            x=x_col,
            y=y_col,
            markers=True,
            title=f"{y_col} by {x_col}",
        )

        fig.update_layout(xaxis_title=x_col, yaxis_title=y_col)

    # ---------------- SCATTER PLOT ----------------
    elif chart_type == "Scatter Plot":
        if len(numeric_cols) < 2:
            st.warning("A scatter plot requires at least two numeric columns.")
            return

        col1, col2 = st.columns(2)

        with col1:
            x_col = st.selectbox(
                "X-axis",
                numeric_cols,
                key="scatter_x",
            )

        with col2:
            y_options = [col for col in numeric_cols if col != x_col]
            y_col = st.selectbox(
                "Y-axis",
                y_options,
                key="scatter_y",
            )

        color_options = ["None"] + categorical_cols + [
            col for col in numeric_cols if col not in [x_col, y_col]
        ]

        color_col = st.selectbox(
            "Color points by (optional)",
            color_options,
            key="scatter_color",
        )

        fig = px.scatter(
            df,
            x=x_col,
            y=y_col,
            color=None if color_col == "None" else color_col,
            title=f"{y_col} vs {x_col}",
            hover_data=all_cols[:8],
        )

    # ---------------- HISTOGRAM ----------------
    elif chart_type == "Histogram":
        if not numeric_cols:
            st.warning("A histogram requires a numeric column.")
            return

        col1, col2 = st.columns(2)

        with col1:
            x_col = st.selectbox(
                "Numeric column",
                numeric_cols,
                key="hist_x",
            )

        with col2:
            bins = st.slider(
                "Number of bins",
                min_value=5,
                max_value=100,
                value=30,
                key="hist_bins",
            )

        color_col = st.selectbox(
            "Group by (optional)",
            ["None"] + categorical_cols,
            key="hist_color",
        )

        fig = px.histogram(
            df,
            x=x_col,
            nbins=bins,
            color=None if color_col == "None" else color_col,
            title=f"Distribution of {x_col}",
        )

    # ---------------- BOX PLOT ----------------
    elif chart_type == "Box Plot":
        if not numeric_cols:
            st.warning("A box plot requires a numeric column.")
            return

        col1, col2 = st.columns(2)

        with col1:
            y_col = st.selectbox(
                "Numeric metric",
                numeric_cols,
                key="box_y",
            )

        with col2:
            x_col = st.selectbox(
                "Group by (optional)",
                ["None"] + categorical_cols,
                key="box_x",
            )

        fig = px.box(
            df,
            x=None if x_col == "None" else x_col,
            y=y_col,
            points="outliers",
            title=f"Distribution and outliers: {y_col}",
        )

    # ---------------- PIE / DONUT ----------------
    elif chart_type == "Pie / Donut Chart":
        if not categorical_cols:
            st.warning("A pie chart requires a categorical column.")
            return

        col1, col2 = st.columns(2)

        with col1:
            names_col = st.selectbox(
                "Category",
                categorical_cols,
                key="pie_names",
            )

        with col2:
            values_options = ["Count (frequency)"] + numeric_cols
            values_col = st.selectbox(
                "Values",
                values_options,
                key="pie_values",
            )

        hole = st.slider(
            "Donut hole size",
            min_value=0.0,
            max_value=0.7,
            value=0.35,
            step=0.05,
            key="pie_hole",
        )

        if values_col == "Count (frequency)":
            pie_df = (
                df.groupby(names_col, dropna=False)
                .size()
                .reset_index(name="Count")
            )
            value_col = "Count"
        else:
            value_col = values_col
            pie_df = (
                df.groupby(names_col, dropna=False)[value_col]
                .sum()
                .reset_index()
            )

        pie_df = pie_df.sort_values(value_col, ascending=False).head(15)

        fig = px.pie(
            pie_df,
            names=names_col,
            values=value_col,
            hole=hole,
            title=f"{value_col} by {names_col}",
        )

    # ---------------- CORRELATION HEATMAP ----------------
    elif chart_type == "Correlation Heatmap":
        if len(numeric_cols) < 2:
            st.warning(
                "A correlation heatmap requires at least two numeric columns."
            )
            return

        selected_cols = st.multiselect(
            "Select numeric metrics",
            numeric_cols,
            default=numeric_cols[:min(8, len(numeric_cols))],
            key="heatmap_cols",
        )

        if len(selected_cols) < 2:
            st.info("Select at least two numeric columns.")
            return

        corr = df[selected_cols].corr(numeric_only=True)

        fig = px.imshow(
            corr,
            text_auto=".2f",
            aspect="auto",
            color_continuous_scale="RdBu_r",
            zmin=-1,
            zmax=1,
            title="Correlation between numeric metrics",
        )

    # Display the chart
    fig.update_layout(
        template="plotly_white",
        height=550,
        margin=dict(l=20, r=20, t=60, b=20),
    )

    st.plotly_chart(fig, use_container_width=True)

    with st.expander("About this chart"):
        st.write(
            "This visualization is generated directly from your uploaded "
            "dataset. Use the chart controls above to change the selected "
            "columns, metrics, or aggregation."
        )
