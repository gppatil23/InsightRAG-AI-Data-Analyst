import pandas as pd
import numpy as np


def group_by_analysis(
    df: pd.DataFrame,
    group_column: str,
    value_column: str,
    aggregation: str = "sum"
) -> dict:
    """Aggregate a numeric column by a categorical column."""

    if group_column not in df.columns or value_column not in df.columns:
        return {"error": "Invalid column name."}

    if not pd.api.types.is_numeric_dtype(df[value_column]):
        return {"error": "Value column must be numeric."}

    allowed = ["sum", "mean", "count", "min", "max"]

    if aggregation not in allowed:
        return {"error": f"Choose from {allowed}"}

    result = (
        df.groupby(group_column, dropna=False)[value_column]
        .agg(aggregation)
        .sort_values(ascending=False)
    )

    return {
        "operation": "group_by",
        "group_column": group_column,
        "value_column": value_column,
        "aggregation": aggregation,
        "results": [
            {"category": str(k), "value": safe_value(v)}
            for k, v in result.head(20).items()
        ]
    }


def filter_dataset(
    df: pd.DataFrame,
    column: str,
    operator: str,
    value
) -> dict:
    """Filter dataset using supported comparison operators."""

    if column not in df.columns:
        return {"error": "Column not found."}

    operators = {
        "equals": lambda s, v: s == v,
        "not_equals": lambda s, v: s != v,
        "greater_than": lambda s, v: s > v,
        "less_than": lambda s, v: s < v,
        "contains": lambda s, v: s.astype(str).str.contains(
            str(v), case=False, na=False, regex=False
        )
    }

    if operator not in operators:
        return {"error": "Unsupported operator."}

    try:
        filtered = df[operators[operator](df[column], value)]

        return {
            "operation": "filter",
            "matched_rows": len(filtered),
            "total_rows": len(df),
            "results": filtered.head(20).to_dict(orient="records")
        }

    except (TypeError, ValueError) as error:
        return {"error": str(error)}


def sort_dataset(
    df: pd.DataFrame,
    column: str,
    descending: bool = True
) -> dict:
    """Sort dataset by any available column."""

    if column not in df.columns:
        return {"error": "Column not found."}

    result = df.sort_values(
        by=column,
        ascending=not descending,
        na_position="last"
    )

    return {
        "operation": "sort",
        "column": column,
        "results": result.head(20).to_dict(orient="records")
    }


def get_correlation(df: pd.DataFrame) -> dict:
    """Calculate correlations between numeric columns."""

    numeric = df.select_dtypes(include=np.number)

    if numeric.shape[1] < 2:
        return {"error": "At least two numeric columns are required."}

    return {
        "operation": "correlation",
        "results": numeric.corr().round(3).to_dict()
    }


def get_column_summary(
    df: pd.DataFrame,
    column: str
) -> dict:
    """Get summary statistics for any column."""

    if column not in df.columns:
        return {"error": "Column not found."}

    series = df[column]

    return {
        "column": column,
        "data_type": str(series.dtype),
        "count": int(series.count()),
        "missing": int(series.isna().sum()),
        "unique": int(series.nunique()),
        "top_values": series.value_counts().head(10).to_dict()
    }


def safe_value(value):
    """Convert Pandas/NumPy values into JSON-compatible values."""

    if pd.isna(value):
        return None

    if isinstance(value, np.integer):
        return int(value)

    if isinstance(value, np.floating):
        return float(value)

    if isinstance(value, pd.Timestamp):
        return value.isoformat()

    return value
