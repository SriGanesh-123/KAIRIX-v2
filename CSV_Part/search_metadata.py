import json

# Load metadata created by Polars
with open("metadata.json", "r", encoding="utf-8") as f:
    metadata = json.load(f)

# Ask user what they want to find
search_term = input("What do you want to find? ").lower()

print("\nSearching...\n")

found = False

for file_info in metadata:

    for column in file_info["columns"]:

        column_name = column["name"].lower()

        # Allow spaces in question, e.g. "earned premium"
        normalized_search = search_term.replace(" ", "_")

        if normalized_search in column_name:

            print("FOUND!")
            print("File       :", file_info["file_name"])
            print("Column     :", column["name"])
            print("Data Type  :", column["datatype"])
            print("Rows       :", file_info["row_count"])
            print("-" * 40)

            found = True

if not found:
    print("No matching column found.")