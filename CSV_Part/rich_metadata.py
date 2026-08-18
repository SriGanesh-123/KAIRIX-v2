import polars as pl
from pathlib import Path
import json

folder = Path(".")
rich_metadata = []

# Automatically find every CSV
csv_files = list(folder.glob("*.csv"))

for file in csv_files:

    df = pl.read_csv(file)

    # Example: COVERAGE_2000.csv -> COVERAGE
    dataset_name = file.stem.replace("_2000", "")

    all_columns = df.columns

    # Process every column
    for column in all_columns:

        datatype = str(df.schema[column])

        # Automatically collect 5 sample values
        samples = (
            df[column]
            .drop_nulls()
            .unique()
            .head(5)
            .to_list()
        )

        column_info = {
            "file_name": file.name,
            "dataset": dataset_name,
            "column_name": column,
            "datatype": datatype,
            "related_columns": all_columns,
            "sample_values": samples
        }

        rich_metadata.append(column_info)


# Save everything
with open("rich_metadata.json", "w", encoding="utf-8") as f:
    json.dump(rich_metadata, f, indent=4, default=str)


print("Rich metadata generated successfully!")
print("CSV files processed:", len(csv_files))
print("Columns processed:", len(rich_metadata))
print("Output: rich_metadata.json")