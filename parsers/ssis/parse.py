import os
import json
import xml.etree.ElementTree as ET


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Project root:
# <project>/parsers/ssis/parse.py -> <project>
PROJECT_ROOT = os.path.abspath(
    os.path.join(BASE_DIR, "..", "..")
)

DTSX_DIR = os.path.join(
    PROJECT_ROOT,
    "source",
    "ssis",
    "packages"
)

OUTPUT_DIR = os.path.join(
    PROJECT_ROOT,
    "output",
    "ssis"
)


# ============================================================
# HELPERS
# ============================================================

def get_namespace(root):
    """
    Extract namespace from root tag.

    Example:
    {www.microsoft.com/SqlServer/Dts}Executable

    returns:
    www.microsoft.com/SqlServer/Dts
    """

    if root.tag.startswith("{"):
        return root.tag.split("}")[0][1:]

    return ""


def qname(namespace, tag):
    """
    Build a namespaced XML tag.
    """

    if namespace:
        return f"{{{namespace}}}{tag}"

    return tag


def clean_text(element):
    """
    Safely return element text.
    """

    if element is None:
        return ""

    return (element.text or "").strip()


def get_attr(element, name):
    """
    Read an attribute regardless of whether
    it is namespaced or not.
    """

    if element is None:
        return ""

    # Normal attribute
    if name in element.attrib:
        return element.attrib[name]

    # Search namespaced attributes
    for key, value in element.attrib.items():

        if key.endswith("}" + name):
            return value

    return ""


def find_child(parent, namespace, name):
    """
    Find direct child.
    """

    if parent is None:
        return None

    return parent.find(qname(namespace, name))


def find_children(parent, namespace, name):
    """
    Find direct children.
    """

    if parent is None:
        return []

    return parent.findall(qname(namespace, name))


# ============================================================
# PACKAGE METADATA
# ============================================================

def parse_package(root, namespace, file_name):

    package = {
        "package_name": get_attr(root, "ObjectName"),
        "package_id": get_attr(root, "DTSID"),
        "executable_type": get_attr(root, "ExecutableType"),
        "creation_name": get_attr(root, "CreationName"),
        "package_type": get_attr(root, "PackageType"),
        "version_major": get_attr(root, "VersionMajor"),
        "version_minor": get_attr(root, "VersionMinor"),
        "version_build": get_attr(root, "VersionBuild"),
        "version_guid": get_attr(root, "VersionGUID"),
        "description": get_attr(root, "Description"),
        "logging_mode": get_attr(root, "LoggingMode"),
        "source_file": file_name
    }

    return package


# ============================================================
# TASKS
# ============================================================

def parse_tasks(root, namespace, package_name):

    tasks = []

    executables = find_child(root, namespace, "Executables")

    if executables is None:
        return tasks

    for executable in find_children(executables, namespace, "Executable"):

        task = {
            "package_name": package_name,
            "task_id": get_attr(executable, "DTSID"),
            "task_name": get_attr(executable, "ObjectName"),
            "task_type": get_attr(executable, "ExecutableType"),
            "creation_name": get_attr(executable, "CreationName"),
            "ref_id": get_attr(executable, "refId")
        }

        tasks.append(task)

    return tasks


# ============================================================
# COMPONENTS
# ============================================================

def find_pipeline_components(executable, namespace):

    object_data = find_child(
        executable,
        namespace,
        "ObjectData"
    )

    if object_data is None:
        return None, []

    pipeline = object_data.find("pipeline")

    if pipeline is None:
        return None, []

    components_element = pipeline.find("components")

    if components_element is None:
        return pipeline, []

    components = components_element.findall("component")

    return pipeline, components


def parse_components(
    root,
    namespace,
    package_name,
    components_output,
    component_properties_output,
    relationships_output
):

    executables = find_child(root, namespace, "Executables")

    if executables is None:
        return []

    component_counter = 1

    for executable in find_children(
        executables,
        namespace,
        "Executable"
    ):

        task_name = get_attr(
            executable,
            "ObjectName"
        )

        pipeline, components = find_pipeline_components(
            executable,
            namespace
        )

        if pipeline is None:
            continue

        # ----------------------------------------------------
        # COMPONENTS
        # ----------------------------------------------------

        component_objects = []

        for component in components:

            component_name = get_attr(
                component,
                "name"
            )

            component_type = get_attr(
                component,
                "componentClassID"
            )

            description = get_attr(
                component,
                "description"
            )

            component_id = component_counter

            component_counter += 1

            component_data = {
                "component_id": component_id,
                "package_name": package_name,
                "task_name": task_name,
                "component_name": component_name,
                "component_type": component_type,
                "description": description,
                "properties": {}
            }

            # ------------------------------------------------
            # PROPERTIES
            # ------------------------------------------------

            properties_element = component.find("properties")

            if properties_element is not None:

                for prop in properties_element.findall("property"):

                    property_name = get_attr(
                        prop,
                        "name"
                    )

                    property_value = clean_text(prop)

                    if property_name:

                        component_data[
                            "properties"
                        ][property_name] = property_value

                        component_properties_output.append({

                            "package_name": package_name,

                            "task_name": task_name,

                            "component_id": component_id,

                            "component_name": component_name,

                            "property_name": property_name,

                            "property_value": property_value
                        })

            components_output.append(
                component_data
            )

            component_objects.append(
                component
            )

        # ----------------------------------------------------
        # RELATIONSHIPS
        # ----------------------------------------------------

        for component in component_objects:

            source_component_name = get_attr(
                component,
                "name"
            )

            outputs = component.find("outputs")

            if outputs is None:
                continue

            for output in outputs.findall("output"):

                output_name = get_attr(
                    output,
                    "name"
                )

                # SSIS metadata stores connected target
                # information inside output/input elements.
                #
                # We therefore inspect all components for
                # matching input names.

                for target_component in component_objects:

                    target_component_name = get_attr(
                        target_component,
                        "name"
                    )

                    if (
                        target_component_name
                        == source_component_name
                    ):
                        continue

                    inputs = target_component.find(
                        "inputs"
                    )

                    if inputs is None:
                        continue

                    for input_element in inputs.findall(
                        "input"
                    ):

                        input_name = get_attr(
                            input_element,
                            "name"
                        )

                        if input_name == output_name:

                            relationships_output.append({

                                "package_name": package_name,

                                "task_name": task_name,

                                "source_component":
                                    source_component_name,

                                "source_output":
                                    output_name,

                                "target_component":
                                    target_component_name,

                                "target_input":
                                    input_name
                            })

    return components_output


# ============================================================
# CONNECTION MANAGERS
# ============================================================

def parse_connections(
    root,
    namespace,
    package_name
):

    connections = []

    connection_managers = find_child(
        root,
        namespace,
        "ConnectionManagers"
    )

    if connection_managers is None:
        return connections

    for connection in find_children(
        connection_managers,
        namespace,
        "ConnectionManager"
    ):

        connection_data = {

            "package_name": package_name,

            "connection_name":
                get_attr(
                    connection,
                    "ObjectName"
                ),

            "connection_id":
                get_attr(
                    connection,
                    "DTSID"
                ),

            "creation_name":
                get_attr(
                    connection,
                    "CreationName"
                ),

            "ref_id":
                get_attr(
                    connection,
                    "refId"
                )
        }

        # ----------------------------------------------------
        # CONNECTION PROPERTIES
        # ----------------------------------------------------

        object_data = find_child(
            connection,
            namespace,
            "ObjectData"
        )

        if object_data is not None:

            connection_data[
                "object_data"
            ] = {}

            for element in object_data.iter():

                if element is object_data:
                    continue

                text = clean_text(element)

                if text:

                    connection_data[
                        "object_data"
                    ][element.tag.split("}")[-1]] = text

        connections.append(
            connection_data
        )

    return connections


# ============================================================
# SQL EXTRACTION
# ============================================================

def parse_sql(
    root,
    namespace,
    package_name
):

    sql_objects = []

    for element in root.iter():

        tag_name = element.tag.split("}")[-1]

        if tag_name != "property":
            continue

        property_name = get_attr(
            element,
            "name"
        )

        if property_name is None:
            continue

        property_name_lower = property_name.lower()

        if (
            "sql" in property_name_lower
            or "command" in property_name_lower
        ):

            sql_text = clean_text(element)

            if sql_text:

                sql_objects.append({

                    "package_name":
                        package_name,

                    "property_name":
                        property_name,

                    "sql":
                        sql_text
                })

    return sql_objects


# ============================================================
# VARIABLES
# ============================================================

def parse_variables(
    root,
    namespace,
    package_name
):

    variables = []

    variables_element = find_child(
        root,
        namespace,
        "Variables"
    )

    if variables_element is None:
        return variables

    for variable in find_children(
        variables_element,
        namespace,
        "Variable"
    ):

        variable_data = {

            "package_name":
                package_name,

            "name":
                get_attr(
                    variable,
                    "ObjectName"
                ),

            "id":
                get_attr(
                    variable,
                    "DTSID"
                ),

            "data_type":
                get_attr(
                    variable,
                    "DataType"
                ),

            "description":
                get_attr(
                    variable,
                    "Description"
                )
        }

        # Capture text values inside variable
        values = []

        for child in variable.iter():

            text = clean_text(child)

            if text:
                values.append(text)

        if values:

            variable_data[
                "values"
            ] = values

        variables.append(
            variable_data
        )

    return variables


# ============================================================
# PRECEDENCE CONSTRAINTS
# ============================================================

def parse_precedence(
    root,
    namespace,
    package_name
):

    precedence = []

    precedence_element = find_child(
        root,
        namespace,
        "PrecedenceConstraints"
    )

    if precedence_element is None:
        return precedence

    for constraint in find_children(
        precedence_element,
        namespace,
        "PrecedenceConstraint"
    ):

        precedence.append({

            "package_name":
                package_name,

            "id":
                get_attr(
                    constraint,
                    "DTSID"
                ),

            "from":
                get_attr(
                    constraint,
                    "From"),

            "to":
                get_attr(
                    constraint,
                    "To"),

            "evaluation_operation":
                get_attr(
                    constraint,
                    "EvaluationOperation"
                ),

            "value":
                get_attr(
                    constraint,
                    "Value"
                )
        })

    return precedence


# ============================================================
# PACKAGE LINKS
# ============================================================

def parse_package_links(
    root,
    namespace,
    package_name
):

    links = []

    for element in root.iter():

        tag_name = element.tag.split("}")[-1]

        if tag_name != "Executable":
            continue

        executable_type = get_attr(
            element,
            "ExecutableType"
        )

        creation_name = get_attr(
            element,
            "CreationName"
        )

        object_name = get_attr(
            element,
            "ObjectName"
        )

        # Detect Execute Package Tasks
        if (
            "ExecutePackage" in executable_type
            or "ExecutePackage" in creation_name
        ):

            link = {

                "parent_package":
                    package_name,

                "task_name":
                    object_name,

                "executable_type":
                    executable_type,

                "creation_name":
                    creation_name
            }

            # Look for package name properties
            for child in element.iter():

                if child.tag.split("}")[-1] == "property":

                    property_name = get_attr(
                        child,
                        "name"
                    )

                    if (
                        property_name
                        and "package" in
                        property_name.lower()
                    ):

                        value = clean_text(
                            child
                        )

                        if value:

                            link[
                                "child_package"
                            ] = value

            links.append(link)

    return links


# ============================================================
# PARSE ONE DTSX PACKAGE
# ============================================================

def parse_dtsx(
    file_path,
    metadata
):

    file_name = os.path.basename(
        file_path
    )

    print(
        f"Parsing: {file_name}"
    )

    try:

        tree = ET.parse(
            file_path
        )

        root = tree.getroot()

        namespace = get_namespace(
            root
        )

        # ----------------------------------------------------
        # PACKAGE
        # ----------------------------------------------------

        package = parse_package(
            root,
            namespace,
            file_name
        )

        package_name = package[
            "package_name"
        ]

        metadata[
            "packages"
        ].append(package)

        # ----------------------------------------------------
        # TASKS
        # ----------------------------------------------------

        tasks = parse_tasks(
            root,
            namespace,
            package_name
        )

        metadata[
            "tasks"
        ].extend(tasks)

        # ----------------------------------------------------
        # COMPONENTS
        # ----------------------------------------------------

        parse_components(

            root,

            namespace,

            package_name,

            metadata[
                "components"
            ],

            metadata[
                "component_properties"
            ],

            metadata[
                "relationships"
            ]
        )

        # ----------------------------------------------------
        # CONNECTIONS
        # ----------------------------------------------------

        connections = parse_connections(

            root,

            namespace,

            package_name
        )

        metadata[
            "connections"
        ].extend(
            connections
        )

        # ----------------------------------------------------
        # SQL
        # ----------------------------------------------------

        sql_objects = parse_sql(

            root,

            namespace,

            package_name
        )

        metadata[
            "sql"
        ].extend(
            sql_objects
        )

        # ----------------------------------------------------
        # VARIABLES
        # ----------------------------------------------------

        variables = parse_variables(

            root,

            namespace,

            package_name
        )

        metadata[
            "variables"
        ].extend(
            variables
        )

        # ----------------------------------------------------
        # PRECEDENCE
        # ----------------------------------------------------

        precedence = parse_precedence(

            root,

            namespace,

            package_name
        )

        metadata[
            "precedence"
        ].extend(
            precedence
        )

        # ----------------------------------------------------
        # PACKAGE LINKS
        # ----------------------------------------------------

        links = parse_package_links(

            root,

            namespace,

            package_name
        )

        metadata[
            "package_links"
        ].extend(
            links
        )

        print(
            f"  SUCCESS: {package_name}"
        )

        return True

    except Exception as e:

        print(
            f"  FAILED: {file_name}"
        )

        print(
            f"  Error: {e}"
        )

        return False


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("SSIS COMPLETE METADATA PARSER")
    print("=" * 70)

    # --------------------------------------------------------
    # CHECK INPUT DIRECTORY
    # --------------------------------------------------------

    if not os.path.exists(DTSX_DIR):

        print(
            f"SSIS package directory not found: {DTSX_DIR}"
        )

        return

    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True
    )

    # --------------------------------------------------------
    # FIND DTSX FILES
    # --------------------------------------------------------

    dtsx_files = sorted(

        file_name

        for file_name in os.listdir(
            DTSX_DIR
        )

        if file_name.lower().endswith(
            ".dtsx"
        )
    )

    print()
    print(
        f"DTSX files found: {len(dtsx_files)}"
    )

    for file_name in dtsx_files:

        print(
            f"  - {file_name}"
        )

    # --------------------------------------------------------
    # PARSE EACH PACKAGE SEPARATELY
    # --------------------------------------------------------

    successful = 0
    failed = 0

    total_counts = {
        "packages": 0,
        "tasks": 0,
        "components": 0,
        "component_properties": 0,
        "connections": 0,
        "sql": 0,
        "variables": 0,
        "precedence": 0,
        "package_links": 0,
        "relationships": 0,
    }

    print()
    print("=" * 70)
    print("PARSING ALL PACKAGES")
    print("=" * 70)

    for file_name in dtsx_files:

        file_path = os.path.join(
            DTSX_DIR,
            file_name
        )

        # One metadata object per DTSX package.
        metadata = {
            "metadata_version": "1.0",
            "source_type": "SSIS DTSX",
            "source_directory": DTSX_DIR,
            "packages": [],
            "tasks": [],
            "components": [],
            "component_properties": [],
            "connections": [],
            "sql": [],
            "variables": [],
            "precedence": [],
            "package_links": [],
            "relationships": []
        }

        success = parse_dtsx(
            file_path,
            metadata
        )

        if success:

            successful += 1

            # ------------------------------------------------
            # WRITE ONE METADATA FILE FOR THIS PACKAGE
            # ------------------------------------------------

            package_output_file = os.path.join(
                OUTPUT_DIR,
                f"{os.path.splitext(file_name)[0]}_metadata.json"
            )

            with open(
                package_output_file,
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    metadata,
                    file,
                    indent=2,
                    ensure_ascii=False
                )

            print(
                f"  OUTPUT: {package_output_file}"
            )

            # Console summary only; no aggregate metadata file.
            for key in total_counts:
                total_counts[key] += len(
                    metadata.get(key, [])
                )

        else:

            failed += 1

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("PARSING COMPLETE")
    print("=" * 70)

    print(
        f"DTSX files found       : {len(dtsx_files)}"
    )

    print(
        f"Successfully parsed    : {successful}"
    )

    print(
        f"Failed                 : {failed}"
    )

    print()
    print("METADATA COUNTS")
    print("-" * 70)

    print(
        f"Packages               : "
        f"{total_counts['packages']}"
    )

    print(
        f"Tasks                  : "
        f"{total_counts['tasks']}"
    )

    print(
        f"Components             : "
        f"{total_counts['components']}"
    )

    print(
        f"Component properties   : "
        f"{total_counts['component_properties']}"
    )

    print(
        f"Connections            : "
        f"{total_counts['connections']}"
    )

    print(
        f"SQL                    : "
        f"{total_counts['sql']}"
    )

    print(
        f"Variables              : "
        f"{total_counts['variables']}"
    )

    print(
        f"Precedence constraints : "
        f"{total_counts['precedence']}"
    )

    print(
        f"Package links          : "
        f"{total_counts['package_links']}"
    )

    print(
        f"Relationships          : "
        f"{total_counts['relationships']}"
    )

    print()
    print("OUTPUT DIRECTORY:")
    print(OUTPUT_DIR)
    print(f"Metadata files         : {successful}")

    print()
    print("=" * 70)


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()