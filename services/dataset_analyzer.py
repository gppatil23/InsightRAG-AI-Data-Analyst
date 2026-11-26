
import pandas as pd
import numpy as np


def analyze_dataset(df: pd.DataFrame) -> dict:
    """
    Analyze any uploaded dataset and generate
    a structured profile of its columns.
    """

    profile = {
        "row_count": int(df.shape[0]),
        "column_count": int(df.shape[1]),
        "columns": {},
        "missing_values": {},
        "duplicate_rows": int(df.duplicated().sum()),
    }

    for column in df.columns:
        series = df[column]

        column_info = {
            "data_type": str(series.dtype),
            "missing_count": int(series.isna().sum()),
            "missing_percentage": round(
                float(series.isna().mean() * 100), 2
            ),
            "unique_values": int(series.nunique()),
            "sample_values": series.dropna().head(5).tolist(),
        }

        # Detect numeric columns
        if pd.api.types.is_numeric_dtype(series):
            column_info["column_type"] = "numeric"

            column_info["statistics"] = {
                "mean": safe_value(series.mean()),
                "median": safe_value(series.median()),
                "min": safe_value(series.min()),
                "max": safe_value(series.max()),
                "std": safe_value(series.std()),
            }

        # Detect datetime columns
        elif pd.api.types.is_datetime64_any_dtype(series):
            column_info["column_type"] = "datetime"

            column_info["statistics"] = {
                "earliest": safe_value(series.min()),
                "latest": safe_value(series.max()),
            }

        # Detect categorical/text columns
        else:
            column_info["column_type"] = "categorical"

            column_info["top_values"] = (
                series.astype("string")
                .value_counts(dropna=True)
                .head(5)
                .to_dict()
            )

        profile["columns"][str(column)] = column_info

        if series.isna().any():
            profile["missing_values"][str(column)] = int(
                series.isna().sum()
            )

    return profile


def safe_value(value):
    """Convert NumPy and Pandas values to JSON-safe values."""

    if pd.isna(value):
        return None

    if isinstance(value, (np.integer,)):
        return int(value)

    if isinstance(value, (np.floating,)):
        return float(value)

    if isinstance(value, (pd.Timestamp,)):
        return value.isoformat()

    return value
