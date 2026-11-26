
import streamlit as st
import pandas as pd
import json
import hashlib

from services.data_loader import load_dataset
from services.dataset_analyzer import analyze_dataset
from services.llm_analyst import ask_data_analyst


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="InsightRAG | AI Data Analyst",
    page_icon="📊",
    layout="wide"
)


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "dataset_hash" not in st.session_state:
    st.session_state.dataset_hash = None

if "df" not in st.session_state:
    st.session_state.df = None

if "profile" not in st.session_state:
    st.session_state.profile = None


# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.title("InsightRAG")
st.caption(
    "AI-powered Data Analysis Using LangChain, RAG, and Pandas"
)

st.markdown(
    """
    Upload a dataset, explore its structure, and ask questions
    in natural language. InsightRAG uses analytical tools to
    calculate answers from your actual data.
    """
)


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:

    st.header("Dataset")

    uploaded_file = st.file_uploader(
        "Upload CSV or Excel file",
        type=["csv", "xlsx", "xls"]
    )

    st.divider()

    st.markdown("### Supported formats")
    st.write("CSV")
    st.write("Excel (.xlsx, .xls)")

    st.divider()

    st.markdown("### Example questions")

    st.markdown(
        """
        - Which category has the highest average value?
        - Show the top 10 records by a numeric column.
        - How many missing values are present?
        - Which numeric columns are correlated?
        - What are the most frequent values in a column?
        """
    )


# --------------------------------------------------
# LOAD DATASET
# --------------------------------------------------

if uploaded_file is not None:

    file_bytes = uploaded_file.getvalue()

    current_hash = hashlib.sha256(
        file_bytes
    ).hexdigest()

    # Load only when a new file is uploaded
    if current_hash != st.session_state.dataset_hash:

        try:
            df = load_dataset(
                uploaded_file.name,
                file_bytes
            )

            profile = analyze_dataset(df)

            st.session_state.df = df
            st.session_state.profile = profile
            st.session_state.dataset_hash = current_hash

            # Clear previous conversation for a new dataset
            st.session_state.messages = []

        except Exception as error:
            st.error(f"Unable to load dataset: {error}")
            st.stop()


# --------------------------------------------------
# DATASET DISPLAY
# --------------------------------------------------

df = st.session_state.df
profile = st.session_state.profile


if df is not None:

    st.success(
        f"Dataset loaded successfully: {uploaded_file.name}"
    )

    # Dataset metrics
    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Rows",
        f"{df.shape[0]:,}"
    )

    col2.metric(
        "Columns",
        f"{df.shape[1]:,}"
    )

    col3.metric(
        "Missing Values",
        f"{int(df.isna().sum().sum()):,}"
    )

    col4.metric(
        "Duplicate Rows",
        f"{int(df.duplicated().sum()):,}"
    )

    st.divider()

    # Dataset tabs
    tab1, tab2, tab3 = st.tabs(
        ["Data Preview", "Dataset Profile", "Statistics"]
    )

    with tab1:

        st.subheader("Dataset Preview")

        st.dataframe(
            df.head(100),
            use_container_width=True,
            height=400
        )

    with tab2:

        st.subheader("Column Information")

        column_data = []

        for column, info in profile["columns"].items():

            column_data.append({
                "Column": column,
                "Type": info["column_type"],
                "Data Type": info["data_type"],
                "Missing": info["missing_count"],
                "Missing %": info["missing_percentage"],
                "Unique Values": info["unique_values"],
            })

        st.dataframe(
            pd.DataFrame(column_data),
            use_container_width=True
        )

        with st.expander("View complete dataset profile"):

            st.json(profile)

    with tab3:

        st.subheader("Numeric Statistics")

        numeric_df = df.select_dtypes(
            include="number"
        )

        if not numeric_df.empty:

            st.dataframe(
                numeric_df.describe().T,
                use_container_width=True
            )

            st.subheader("Correlation Matrix")

            if numeric_df.shape[1] >= 2:

                correlation = numeric_df.corr()

                st.dataframe(
                    correlation,
                    use_container_width=True
                )

                st.caption(
                    "Correlation measures relationships between "
                    "numeric columns. It does not establish causation."
                )

            else:
                st.info(
                    "At least two numeric columns are required "
                    "for correlation analysis."
                )

        else:
            st.info(
                "No numeric columns were detected in this dataset."
            )

    st.divider()

    # --------------------------------------------------
    # AI DATA ANALYST CHAT
    # --------------------------------------------------

    st.subheader("Ask InsightRAG")

    st.caption(
        "Ask questions about your uploaded dataset. "
        "Numerical questions are answered using analytical tools."
    )

    # Display previous messages
    for message in st.session_state.messages:

        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    question = st.chat_input(
        "Ask a question about your dataset..."
    )

    if question:

        # Display user question
        st.session_state.messages.append({
            "role": "user",
            "content": question
        })

        with st.chat_message("user"):
            st.markdown(question)

        # Generate answer
        with st.chat_message("assistant"):

            with st.spinner(
                "Analyzing your dataset..."
            ):

                try:

                    answer = ask_data_analyst(
                        df=df,
                        dataset_profile=profile,
                        question=question
                    )

                    st.markdown(answer)

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer
                    })

                except Exception as error:

                    error_message = (
                        f"An error occurred during analysis: {error}"
                    )

                    st.error(error_message)

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_message
                    })

    # Clear chat
    if st.button("Clear conversation"):

        st.session_state.messages = []
        st.rerun()


# --------------------------------------------------
# EMPTY STATE
# --------------------------------------------------

else:

    st.info(
        "Upload a CSV or Excel dataset from the sidebar "
        "to start analyzing your data."
    )

    st.markdown("### What you can do with InsightRAG")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("#### Explore Data")
        st.write(
            "Understand columns, data types, missing values, "
            "and dataset statistics."
        )

    with col2:
        st.markdown("#### Ask Questions")
        st.write(
            "Use natural language to ask questions "
            "about your dataset."
        )

    with col3:
        st.markdown("#### Get Insights")
        st.write(
            "Receive calculated results using "
            "Pandas analytical tools."
        )


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "InsightRAG | Built with Python, Streamlit, "
    "LangChain, Gemini, and Pandas"
)
