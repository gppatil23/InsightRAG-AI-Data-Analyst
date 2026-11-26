
import json
import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage

from services.analysis_tools import (
    group_by_analysis,
    filter_dataset,
    sort_dataset,
    get_correlation,
    get_column_summary,
)

load_dotenv()


def create_dataset_tools(df):
    """
    Create LangChain tools connected to the current DataFrame.
    """

    @tool
    def group_data(
        group_column: str,
        value_column: str,
        aggregation: str = "sum"
    ) -> str:
        """Group a dataset column and calculate sum, mean, count, min, or max
        for a numeric value column. Use this for questions about averages,
        totals, counts, highest or lowest groups."""
        result = group_by_analysis(
            df, group_column, value_column, aggregation
        )
        return json.dumps(result, default=str)

    @tool
    def filter_data(
        column: str,
        operator: str,
        value: str
    ) -> str:
        """Filter dataset rows. Operators: equals, not_equals,
        greater_than, less_than, contains. Use for questions asking
        to find or count records matching a condition."""
        result = filter_dataset(df, column, operator, value)
        return json.dumps(result, default=str)

    @tool
    def sort_data(
        column: str,
        descending: bool = True
    ) -> str:
        """Sort the dataset by any column and return the top rows.
        Use to find highest, lowest, largest, smallest, newest,
        or oldest records."""
        result = sort_dataset(df, column, descending)
        return json.dumps(result, default=str)

    @tool
    def calculate_correlation() -> str:
        """Calculate correlations between numeric columns.
        Use when the user asks whether variables are related."""
        result = get_correlation(df)
        return json.dumps(result, default=str)

    @tool
    def summarize_column(column: str) -> str:
        """Get statistics, missing values, unique values, and
        frequent values for a specific dataset column."""
        result = get_column_summary(df, column)
        return json.dumps(result, default=str)

    return [
        group_data,
        filter_data,
        sort_data,
        calculate_correlation,
        summarize_column,
    ]

def extract_text(content) -> str:
    """Extract plain text from LangChain message content."""

    if isinstance(content, str):
        return content

    if isinstance(content, list):
        text_parts = []

        for block in content:
            if isinstance(block, dict):
                if block.get("type") == "text":
                    text_parts.append(block.get("text", ""))

            elif isinstance(block, str):
                text_parts.append(block)

        return "\n\n".join(text_parts).strip()

    return str(content)

def ask_data_analyst(df, dataset_profile: dict, question: str) -> str:
    """
    Ask Gemini a question about the dataset using controlled tools.
    """

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return "GEMINI_API_KEY is missing from your .env file."

    model = ChatGoogleGenerativeAI(
        model=os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite"),
        api_key=api_key
    )

    tools = create_dataset_tools(df)
    tools_by_name = {item.name: item for item in tools}

    model_with_tools = model.bind_tools(tools)

    system_prompt = f"""
You are InsightRAG, a careful AI data analyst.

The user has uploaded a dataset. Analyze only this dataset.

Dataset profile:
{json.dumps(dataset_profile, indent=2, default=str)}

Rules:
- Use the exact column names from the dataset profile.
- Never assume the dataset is about sales or any particular domain.
- For numerical questions, use the available analysis tools.
- Do not invent values or claim calculations you did not perform.
- If a question cannot be answered with the available tools,
  explain the limitation honestly.
- Do not generate or execute Python or SQL code.
- Explain the result clearly and mention the relevant columns.
- If a tool returns an error, explain it or try a valid alternative.
"""

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=question),
    ]

    # Allow up to 4 tool-calling rounds.
    for _ in range(4):
        response = model_with_tools.invoke(messages)
        messages.append(response)

        if not response.tool_calls:
            return extract_text(response.content)

        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            tool_id = tool_call["id"]

            selected_tool = tools_by_name.get(tool_name)

            if selected_tool is None:
                tool_result = "Error: Unknown tool requested."
            else:
                try:
                    tool_result = selected_tool.invoke(tool_args)
                except Exception as error:
                    tool_result = f"Tool execution error: {error}"

            messages.append(
                ToolMessage(
                    content=str(tool_result),
                    tool_call_id=tool_id,
                )
            )

    return (
        "I reached the analysis step limit. "
        "Please try asking a more specific question."
    )
