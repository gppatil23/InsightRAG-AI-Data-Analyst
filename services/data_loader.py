import pandas as pd
from io import BytesIO


def load_dataset(file_name: str, file_bytes: bytes) -> pd.DataFrame:
    """
    Load CSV or Excel data from uploaded file bytes.
    """

    file_name = file_name.lower()

    try:
        if file_name.endswith(".csv"):
            df = pd.read_csv(BytesIO(file_bytes))

        elif file_name.endswith((".xlsx", ".xls")):
            df = pd.read_excel(BytesIO(file_bytes))

        else:
            raise ValueError(
                "Unsupported file format. Upload CSV or Excel."
            )

        if df.empty:
            raise ValueError("The uploaded file contains no data.")

        # Clean column names
        df.columns = [
            str(column).strip()
            for column in df.columns
        ]

        # Remove completely empty rows
        df = df.dropna(how="all")

        return df

    except Exception as error:
        raise ValueError(
            f"Could not load dataset: {error}"
        ) from error
