import json
import re


# --------------------------------------------------
# 1. LOAD CLEAN COBOL DEPENDENCIES
# --------------------------------------------------

with open(
    "cobol_dependencies_clean.json",
    "r",
    encoding="utf-8"
) as f:
    programs = json.load(f)


# --------------------------------------------------
# 2. NORMALIZE FILE/DATASET NAMES
# --------------------------------------------------

def normalize_name(name):
    """
    PREMIUM-OUT -> PREMIUM
    PREMIUM-IN  -> PREMIUM
    POLICY-OUT  -> POLICY
    POLICY-IN   -> POLICY
    """

    name = name.upper()

    name = re.sub(r"-IN$", "", name)
    name = re.sub(r"-OUT$", "", name)

    return name


# --------------------------------------------------
# 3. FIND INPUTS AND OUTPUTS
# --------------------------------------------------

program_info = []

for program in programs:

    selects = program.get("select", [])
    reads = program.get("read", [])

    inputs = []
    outputs = []

    for item in selects:

        upper_item = item.upper()

        # Ignore error datasets for relationship building
        if "ERROR" in upper_item:
            continue

        if upper_item.endswith("-IN"):
            inputs.append(upper_item)

        elif upper_item.endswith("-OUT"):
            outputs.append(upper_item)

    program_info.append({
        "file": program["file"],
        "program": program["program"],
        "inputs": sorted(set(inputs)),
        "outputs": sorted(set(outputs)),
        "reads": reads
    })


# --------------------------------------------------
# 4. BUILD CANDIDATE RELATIONSHIPS
# --------------------------------------------------

relationships = []

for producer in program_info:

    for output_name in producer["outputs"]:

        output_base = normalize_name(output_name)

        for consumer in program_info:

            # Don't connect program to itself
            if producer["program"] == consumer["program"]:
                continue

            for input_name in consumer["inputs"]:

                input_base = normalize_name(input_name)

                # Example:
                # PREMIUM-OUT -> PREMIUM
                # PREMIUM-IN  -> PREMIUM
                if output_base == input_base:

                    relationships.append({
                        "from_program": producer["program"],
                        "from_file": producer["file"],
                        "output": output_name,

                        "to_program": consumer["program"],
                        "to_file": consumer["file"],
                        "input": input_name,

                        "matched_data": output_base,

                        "relationship_type":
                            "candidate_data_flow",

                        "confidence":
                            "inferred_from_logical_file_name"
                    })


# --------------------------------------------------
# 5. SAVE RESULTS
# --------------------------------------------------

result = {
    "programs": program_info,
    "candidate_relationships": relationships
}

with open(
    "cobol_relationships.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        result,
        f,
        indent=4
    )


# --------------------------------------------------
# 6. DISPLAY RESULTS
# --------------------------------------------------

print("\nCOBOL relationship analysis completed!")

print("Programs analyzed:", len(program_info))
print(
    "Candidate relationships found:",
    len(relationships)
)

print("\n" + "=" * 70)
print("CANDIDATE DATA FLOWS")
print("=" * 70)

for relation in relationships:

    print(
        f"\n{relation['from_program']} "
        f"({relation['output']})"
    )

    print("        ↓ possible data flow")

    print(
        f"{relation['to_program']} "
        f"({relation['input']})"
    )

    print(
        "Matched data:",
        relation["matched_data"]
    )

    print("-" * 70)


print("\nOutput: cobol_relationships.json")