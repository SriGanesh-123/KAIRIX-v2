import polars as pl
from pathlib import Path
import json

folder = Path(".")

metadata = []

for file in folder.glob("*.csv"):

    df = pl.read_csv(file)

    file_info = {
        "file_name": file.name,
        "file_type": "CSV",
        "row_count": df.height,
        "column_count": df.width,
        "columns": [
            {
                "name": column,
                "datatype": str(datatype)
            }
            for column, datatype in df.schema.items()
        ]
    }

    metadata.append(file_info)

with open("metadata.json", "w", encoding="utf-8") as f:
    json.dump(metadata, f, indent=4)

print("Metadata extraction completed.")
print(f"Files processed: {len(metadata)}")
print("Output: metadata.json")