# ============================================================
# FINAL T-SQL METADATA PARSER
# SQLGlot + T-SQL metadata extraction + Nested CASE support
#
# Install:
# pip install sqlglot
# ============================================================

from pathlib import Path
import json
import re

import sqlglot
from sqlglot import exp
from sqlglot.errors import ParseError


# ============================================================
# 1. CONFIGURATION
# ============================================================

INPUT_FOLDER = Path(
    r"C:\Users\GaneshSriKumarMarimu\legacy-code-agentic-rag\source\sql"
)
OUTPUT_FOLDER = Path(
    r"C:\Users\GaneshSriKumarMarimu\legacy-code-agentic-rag\output\sql"
)
OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)


# ============================================================
# 2. HELPERS
# ============================================================

def clean(text):
    if not text:
        return None

    return " ".join(str(text).split())


def clean_identifier(name):
    if not name:
        return None

    name = re.sub(
        r"\s*\.\s*",
        ".",
        name
    )

    return (
        name
        .replace("[", "")
        .replace("]", "")
        .strip()
    )


def line_number(sql, position):
    return sql.count(
        "\n",
        0,
        position
    ) + 1


# ============================================================
# 3. REMOVE COMMENTS
# ============================================================

def remove_comments(sql):

    sql = re.sub(
        r"/\*.*?\*/",
        " ",
        sql,
        flags=re.DOTALL
    )

    sql = re.sub(
        r"--.*?$",
        "",
        sql,
        flags=re.MULTILINE
    )

    return sql


# ============================================================
# 4. PREPARE SQL FOR SQLGLOT
#
# SQLGlot understands T-SQL, but DECLARE / SET statements
# are not needed for SELECT AST metadata extraction.
#
# Original SQL is still used for variable extraction.
# ============================================================

def prepare_for_sqlglot(sql):

    processed = sql

    # --------------------------------------------------------
    # Remove DECLARE
    # --------------------------------------------------------

    processed = re.sub(
        r"""
        (?im)
        ^\s*
        DECLARE\s+
        @[A-Za-z_][A-Za-z0-9_]*
        \s+
        (?:AS\s+)?
        [A-Za-z0-9_]+
        (?:\s*\([^)]*\))?
        (?:\s*=\s*[^\n;]+)?
        ;?
        \s*$
        """,
        "",
        processed,
        flags=re.VERBOSE
    )

    # --------------------------------------------------------
    # Remove SET @variable
    # --------------------------------------------------------

    processed = re.sub(
        r"""
        (?im)
        ^\s*
        SET\s+
        @[A-Za-z_][A-Za-z0-9_]*
        \s*=
        [^\n;]+
        ;?
        \s*$
        """,
        "",
        processed,
        flags=re.VERBOSE
    )

    # --------------------------------------------------------
    # Remove SQL Server table hints
    #
    # table (nolock)
    # table WITH (NOLOCK)
    # --------------------------------------------------------

    processed = re.sub(
        r"\s+WITH\s*\(\s*NOLOCK\s*\)",
        "",
        processed,
        flags=re.IGNORECASE
    )

    processed = re.sub(
        r"\s*\(\s*NOLOCK\s*\)",
        "",
        processed,
        flags=re.IGNORECASE
    )

    # --------------------------------------------------------
    # Remove GO
    # --------------------------------------------------------

    processed = re.sub(
        r"(?im)^\s*GO\s*$",
        "",
        processed
    )

    return processed


# ============================================================
# 5. SQLGLOT PARSE
# ============================================================

def parse_with_sqlglot(sql):

    errors = []
    expressions = []

    try:

        expressions = sqlglot.parse(
            sql,
            read="tsql"
        )

    except ParseError as error:

        errors.append({
            "type": "ParseError",
            "message": str(error)
        })

    except Exception as error:

        errors.append({
            "type": type(error).__name__,
            "message": str(error)
        })

    return expressions, errors


# ============================================================
# 6. SQLGLOT AST NODES
# ============================================================

def get_ast_nodes(expressions):

    nodes = []

    for statement_number, expression in enumerate(
        expressions,
        start=1
    ):

        if expression is None:
            continue

        for node in expression.walk():

            nodes.append({
                "statement":
                    statement_number,

                "type":
                    type(node).__name__,

                "sql":
                    clean(
                        node.sql(
                            dialect="tsql"
                        )
                    )
            })

    return nodes


# ============================================================
# 7. VARIABLES / DECLARE
# ============================================================

def get_variables(sql):

    pattern = re.compile(
        r"""
        \bDECLARE\s+
        (@[A-Za-z_][A-Za-z0-9_]*)

        \s+
        (?:AS\s+)?

        ([A-Za-z0-9_]+
            (?:\s*\([^)]*\))?
        )

        (?:\s*=\s*([^\n;]+))?
        """,

        re.IGNORECASE |
        re.VERBOSE
    )

    variables = []

    for match in pattern.finditer(sql):

        variables.append({
            "name":
                match.group(1),

            "datatype":
                clean(
                    match.group(2)
                ),

            "default_value":
                clean(
                    match.group(3)
                ),

            "line":
                line_number(
                    sql,
                    match.start()
                )
        })

    return variables


# ============================================================
# 8. SET STATEMENTS
# ============================================================

def get_set_statements(sql):

    pattern = re.compile(
        r"""
        \bSET\s+

        (@[A-Za-z_][A-Za-z0-9_]*)

        \s*=\s*

        ([^\n;]+)
        """,

        re.IGNORECASE |
        re.VERBOSE
    )

    results = []

    for match in pattern.finditer(sql):

        results.append({
            "variable":
                match.group(1),

            "value":
                clean(
                    match.group(2)
                ),

            "line":
                line_number(
                    sql,
                    match.start()
                )
        })

    return results


# ============================================================
# 9. TABLE NAME PATTERN
# ============================================================

TABLE_NAME = r"""
(?:\[[^\]]+\]|[#A-Za-z_][A-Za-z0-9_$#]*)
(?:
    \s*\.\s*
    (?:\[[^\]]+\]|[A-Za-z_][A-Za-z0-9_$#]*)
)*
"""


# ============================================================
# 10. TABLES
#
# Kept from your validated extraction because it already
# produces correct source/extract counts for the 4 files.
# ============================================================

def get_tables(sql):

    pattern = re.compile(
        rf"""
        \b(FROM|JOIN)\s+

        ({TABLE_NAME})

        (?:
            \s+
            (?:AS\s+)?
            ([A-Za-z_][A-Za-z0-9_]*)
        )?
        """,

        re.IGNORECASE |
        re.VERBOSE
    )

    reserved = {
        "where",
        "join",
        "inner",
        "left",
        "right",
        "full",
        "cross",
        "outer",
        "on",
        "group",
        "order",
        "having",
        "union",
        "with",
        "nolock"
    }

    tables = []

    for match in pattern.finditer(sql):

        table = clean_identifier(
            match.group(2)
        )

        alias = match.group(3)

        if (
            alias
            and alias.lower() in reserved
        ):
            alias = None

        tables.append({
            "source":
                match.group(1).upper(),

            "table":
                table,

            "alias":
                alias,

            "line":
                line_number(
                    sql,
                    match.start()
                )
        })

    return tables


# ============================================================
# 11. UNIQUE TABLES
# ============================================================

def get_unique_tables(tables):

    unique_tables = []
    seen = set()

    for item in tables:

        table = item["table"]
        key = table.lower()

        if key not in seen:

            seen.add(key)
            unique_tables.append(table)

    return unique_tables


# ============================================================
# 12. JOINS
# ============================================================

def get_joins(sql):

    pattern = re.compile(
        rf"""
        \b
        (
            INNER\s+JOIN |
            LEFT\s+(?:OUTER\s+)?JOIN |
            RIGHT\s+(?:OUTER\s+)?JOIN |
            FULL\s+(?:OUTER\s+)?JOIN |
            CROSS\s+JOIN |
            JOIN
        )

        \s+

        ({TABLE_NAME})

        (?:
            \s+
            (?:AS\s+)?
            ([A-Za-z_][A-Za-z0-9_]*)
        )?

        (?:
            \s+WITH\s*\([^)]*\)

            |

            \s*\(
                [^)]*
                (?:NOLOCK|READUNCOMMITTED)
                [^)]*
            \)
        )?

        \s+ON\s+

        (.*?)

        (?=

            \bINNER\s+JOIN\b |

            \bLEFT\s+
            (?:OUTER\s+)?
            JOIN\b |

            \bRIGHT\s+
            (?:OUTER\s+)?
            JOIN\b |

            \bFULL\s+
            (?:OUTER\s+)?
            JOIN\b |

            \bCROSS\s+JOIN\b |

            \bJOIN\b |

            \bWHERE\b |

            \bGROUP\s+BY\b |

            \bHAVING\b |

            \bORDER\s+BY\b |

            \bUNION\b |

            ; |

            $
        )
        """,

        re.IGNORECASE |
        re.DOTALL |
        re.VERBOSE
    )

    joins = []

    for match in pattern.finditer(sql):

        joins.append({
            "join_type":
                clean(
                    match.group(1)
                ).upper(),

            "table":
                clean_identifier(
                    match.group(2)
                ),

            "alias":
                match.group(3),

            "condition":
                clean(
                    match.group(4)
                ),

            "line":
                line_number(
                    sql,
                    match.start()
                )
        })

    return joins


# ============================================================
# 13. CASE EXPRESSIONS
#
# Stack based because it correctly handles your nested CASE.
# ============================================================

def get_case_expressions(sql):

    token_pattern = re.compile(
        r"\bCASE\b|\bEND\b",
        re.IGNORECASE
    )

    stack = []
    cases = []

    reserved_aliases = {
        "when",
        "then",
        "else",
        "end",
        "from",
        "where",
        "group",
        "order",
        "having",
        "union",
        "join",
        "left",
        "right",
        "inner",
        "full",
        "cross",
        "on"
    }

    for token in token_pattern.finditer(sql):

        word = token.group().upper()

        if word == "CASE":

            stack.append({
                "start": token.start(),
                "depth": len(stack)
            })

        elif word == "END" and stack:

            case_info = stack.pop()

            start = case_info["start"]
            end = token.end()

            expression = sql[start:end]

            after_end = sql[
                end:end + 150
            ]

            alias_match = re.match(
                r"""
                \s+
                (?:AS\s+)?
                (\[?[A-Za-z_][A-Za-z0-9_]*\]?)
                """,

                after_end,

                re.IGNORECASE |
                re.VERBOSE
            )

            target = None

            if alias_match:

                candidate = clean_identifier(
                    alias_match.group(1)
                )

                if (
                    candidate
                    and candidate.lower()
                    not in reserved_aliases
                ):
                    target = candidate

            cases.append({
                "target_column":
                    target,

                "expression":
                    clean(expression),

                "line":
                    line_number(
                        sql,
                        start
                    ),

                "nested":
                    case_info["depth"] > 0,

                "nesting_level":
                    case_info["depth"]
            })

    cases.sort(
        key=lambda item: (
            item["line"],
            item["nesting_level"]
        )
    )

    return cases


# ============================================================
# 14. BUSINESS RULES
# ============================================================

def get_business_rules(sql, cases=None):

    if cases is None:
        cases = get_case_expressions(sql)

    rules = []

    when_pattern = re.compile(
        r"""
        \bWHEN\s+

        (.*?)

        \s+THEN\s+

        (.*?)

        (?=
            \bWHEN\b |
            \bELSE\b |
            \bEND\b |
            $
        )
        """,

        re.IGNORECASE |
        re.DOTALL |
        re.VERBOSE
    )

    for case in cases:

        # Nested CASE remains preserved separately.
        if case["nested"]:
            continue

        expression = case["expression"]
        target = case["target_column"]

        for match in when_pattern.finditer(
            expression
        ):

            condition = clean(
                match.group(1)
            )

            result = clean(
                match.group(2)
            )

            rules.append({
                "target_column":
                    target,

                "condition":
                    condition,

                "result":
                    result,

                "rule":
                    (
                        f"IF {condition} "
                        f"THEN "
                        f"{target or 'CASE_RESULT'} "
                        f"= {result}"
                    ),

                "line":
                    case["line"]
            })

    return rules


# ============================================================
# 15. WHERE CONDITIONS
# ============================================================

def get_where_conditions(sql):

    pattern = re.compile(
        r"""
        \bWHERE\b

        (.*?)

        (?=
            \bGROUP\s+BY\b |
            \bHAVING\b |
            \bORDER\s+BY\b |
            \bUNION\b |
            ; |
            $
        )
        """,

        re.IGNORECASE |
        re.DOTALL |
        re.VERBOSE
    )

    results = []

    for match in pattern.finditer(sql):

        results.append({
            "condition":
                clean(
                    match.group(1)
                ),

            "line":
                line_number(
                    sql,
                    match.start()
                )
        })

    return results


# ============================================================
# 16. GROUP BY
# ============================================================

def get_group_by(sql):

    pattern = re.compile(
        r"""
        \bGROUP\s+BY\b

        (.*?)

        (?=
            \bHAVING\b |
            \bORDER\s+BY\b |
            \bUNION\b |
            ; |
            $
        )
        """,

        re.IGNORECASE |
        re.DOTALL |
        re.VERBOSE
    )

    results = []

    for match in pattern.finditer(sql):

        results.append({
            "columns":
                clean(
                    match.group(1)
                ),

            "line":
                line_number(
                    sql,
                    match.start()
                )
        })

    return results


# ============================================================
# 17. FUNCTIONS
# ============================================================

def get_functions(sql):

    functions = re.findall(
        r"""
        \b
        (
            SUM |
            COUNT |
            AVG |
            MIN |
            MAX |
            CONCAT |
            MONTH |
            YEAR |
            DAY |
            GETDATE |
            GETUTCDATE |
            DATEADD |
            DATEDIFF |
            CAST |
            CONVERT |
            COALESCE |
            ISNULL |
            ROW_NUMBER |
            ROUND |
            RTRIM |
            RIGHT
        )

        \s*\(
        """,

        sql,

        re.IGNORECASE |
        re.VERBOSE
    )

    return sorted(
        set(
            function.upper()
            for function in functions
        )
    )


# ============================================================
# 18. COLUMN REFERENCES
# ============================================================

def get_column_references(sql):

    pattern = re.compile(
        r"""
        \b
        ([A-Za-z_][A-Za-z0-9_]*)

        \s*\.\s*

        (\[?[A-Za-z_][A-Za-z0-9_]*\]?)
        """,

        re.IGNORECASE |
        re.VERBOSE
    )

    columns = []
    seen = set()

    for match in pattern.finditer(sql):

        alias = match.group(1)

        column = clean_identifier(
            match.group(2)
        )

        key = (
            alias.lower(),
            column.lower()
        )

        if key in seen:
            continue

        seen.add(key)

        columns.append({
            "alias":
                alias,

            "column":
                column,

            "reference":
                f"{alias}.{column}"
        })

    return columns


# ============================================================
# 19. SQLGLOT STRUCTURAL METADATA
#
# This gives us an independent AST-based view.
# ============================================================

def get_sqlglot_metadata(expressions):

    tables = []
    columns = []
    joins = []
    cases = []
    selects = []
    wheres = []

    table_seen = set()
    column_seen = set()

    for statement_number, expression in enumerate(
        expressions,
        start=1
    ):

        if expression is None:
            continue

        # ----------------------------------------------------
        # Tables
        # ----------------------------------------------------

        for table in expression.find_all(
            exp.Table
        ):

            name = table.sql(
                dialect="tsql"
            )

            if name.lower() not in table_seen:

                table_seen.add(
                    name.lower()
                )

                tables.append(
                    name
                )

        # ----------------------------------------------------
        # Columns
        # ----------------------------------------------------

        for column in expression.find_all(
            exp.Column
        ):

            name = column.sql(
                dialect="tsql"
            )

            if name.lower() not in column_seen:

                column_seen.add(
                    name.lower()
                )

                columns.append(
                    name
                )

        # ----------------------------------------------------
        # JOIN
        # ----------------------------------------------------

        for join in expression.find_all(
            exp.Join
        ):

            joins.append(
                clean(
                    join.sql(
                        dialect="tsql"
                    )
                )
            )

        # ----------------------------------------------------
        # CASE
        # ----------------------------------------------------

        for case in expression.find_all(
            exp.Case
        ):

            cases.append(
                clean(
                    case.sql(
                        dialect="tsql"
                    )
                )
            )

        # ----------------------------------------------------
        # SELECT
        # ----------------------------------------------------

        for select in expression.find_all(
            exp.Select
        ):

            selects.append(
                clean(
                    select.sql(
                        dialect="tsql"
                    )
                )
            )

        # ----------------------------------------------------
        # WHERE
        # ----------------------------------------------------

        for where in expression.find_all(
            exp.Where
        ):

            wheres.append(
                clean(
                    where.sql(
                        dialect="tsql"
                    )
                )
            )

    return {
        "tables":
            tables,

        "columns":
            columns,

        "joins":
            joins,

        "case_expressions":
            cases,

        "selects":
            selects,

        "where_expressions":
            wheres
    }


# ============================================================
# 20. VALIDATION
# ============================================================

def validate_metadata(
    sql,
    tables,
    joins,
    cases,
    variables,
    sqlglot_errors,
    sqlglot_metadata
):

    source_join_count = len(
        re.findall(
            r"""
            \b
            (?:
                INNER |
                LEFT |
                RIGHT |
                FULL |
                CROSS
            )?
            \s*
            (?:OUTER\s+)?
            JOIN\b
            """,

            sql,

            re.IGNORECASE |
            re.VERBOSE
        )
    )

    source_case_count = len(
        re.findall(
            r"\bCASE\b",
            sql,
            re.IGNORECASE
        )
    )

    source_declare_count = len(
        re.findall(
            r"""
            \bDECLARE\s+
            @[A-Za-z_][A-Za-z0-9_]*
            """,

            sql,

            re.IGNORECASE |
            re.VERBOSE
        )
    )

    critical_errors = []
    warnings = []

    # --------------------------------------------------------
    # Our extraction validation
    # --------------------------------------------------------

    if source_join_count != len(joins):

        critical_errors.append(
            f"JOIN mismatch: "
            f"source={source_join_count}, "
            f"extracted={len(joins)}"
        )

    if source_case_count != len(cases):

        critical_errors.append(
            f"CASE mismatch: "
            f"source={source_case_count}, "
            f"extracted={len(cases)}"
        )

    if source_declare_count != len(variables):

        critical_errors.append(
            f"DECLARE mismatch: "
            f"source={source_declare_count}, "
            f"extracted={len(variables)}"
        )

    if not tables:

        critical_errors.append(
            "No tables extracted"
        )

    # --------------------------------------------------------
    # SQLGlot parser validation
    # --------------------------------------------------------

    if sqlglot_errors:

        warnings.append(
            f"SQLGlot reported "
            f"{len(sqlglot_errors)} parsing issue(s)."
        )

    # --------------------------------------------------------
    # Compare SQLGlot CASE/JOIN counts
    # --------------------------------------------------------

    if not sqlglot_errors:

        sqlglot_join_count = len(
            sqlglot_metadata["joins"]
        )

        sqlglot_case_count = len(
            sqlglot_metadata[
                "case_expressions"
            ]
        )

        if (
            sqlglot_join_count
            != source_join_count
        ):

            warnings.append(
                f"SQLGlot JOIN count differs: "
                f"source={source_join_count}, "
                f"sqlglot={sqlglot_join_count}"
            )

        if (
            sqlglot_case_count
            != source_case_count
        ):

            warnings.append(
                f"SQLGlot CASE count differs: "
                f"source={source_case_count}, "
                f"sqlglot={sqlglot_case_count}"
            )

    # --------------------------------------------------------
    # Final status
    # --------------------------------------------------------

    if critical_errors:

        status = "REVIEW"

    elif sqlglot_errors:

        status = "PASS_WITH_SQLGLOT_WARNINGS"

    elif warnings:

        status = "PASS_WITH_VALIDATION_WARNINGS"

    else:

        status = "PASS"

    return {
        "status":
            status,

        "source_join_count":
            source_join_count,

        "extracted_join_count":
            len(joins),

        "sqlglot_join_count":
            len(
                sqlglot_metadata["joins"]
            ),

        "source_case_count":
            source_case_count,

        "extracted_case_count":
            len(cases),

        "sqlglot_case_count":
            len(
                sqlglot_metadata[
                    "case_expressions"
                ]
            ),

        "source_declare_count":
            source_declare_count,

        "extracted_variable_count":
            len(variables),

        "sqlglot_error_count":
            len(sqlglot_errors),

        "critical_errors":
            critical_errors,

        "warnings":
            warnings
    }


# ============================================================
# 21. PARSE ONE FILE
# ============================================================

def parse_file(file_path):

    original_sql = file_path.read_text(
        encoding="utf-8-sig",
        errors="ignore"
    )

    clean_sql = remove_comments(
        original_sql
    )

    # ========================================================
    # SQLGLOT AST PATH
    # ========================================================

    sqlglot_sql = prepare_for_sqlglot(
        clean_sql
    )

    expressions, sqlglot_errors = (
        parse_with_sqlglot(
            sqlglot_sql
        )
    )

    ast_nodes = get_ast_nodes(
        expressions
    )

    sqlglot_metadata = (
        get_sqlglot_metadata(
            expressions
        )
    )

    # ========================================================
    # ORIGINAL T-SQL METADATA
    # ========================================================

    variables = get_variables(
        clean_sql
    )

    set_statements = get_set_statements(
        clean_sql
    )

    tables = get_tables(
        clean_sql
    )

    unique_tables = get_unique_tables(
        tables
    )

    joins = get_joins(
        clean_sql
    )

    cases = get_case_expressions(
        clean_sql
    )

    business_rules = get_business_rules(
        clean_sql,
        cases
    )

    where_conditions = (
        get_where_conditions(
            clean_sql
        )
    )

    group_by = get_group_by(
        clean_sql
    )

    functions = get_functions(
        clean_sql
    )

    column_references = (
        get_column_references(
            clean_sql
        )
    )

    # ========================================================
    # VALIDATION
    # ========================================================

    validation = validate_metadata(
        clean_sql,
        tables,
        joins,
        cases,
        variables,
        sqlglot_errors,
        sqlglot_metadata
    )

    # ========================================================
    # FINAL JSON
    # ========================================================

    metadata = {

        "file_metadata": {
            "file_name":
                file_path.name,

            "language":
                "T-SQL",

            "parser":
                "SQLGlot (T-SQL dialect) + metadata extraction",

            "total_lines":
                len(
                    original_sql.splitlines()
                ),

            "sqlglot_parse_success":
                len(sqlglot_errors) == 0
        },

        "summary": {
            "unique_tables":
                len(unique_tables),

            "table_occurrences":
                len(tables),

            "joins":
                len(joins),

            "variables":
                len(variables),

            "set_statements":
                len(set_statements),

            "case_expressions":
                len(cases),

            "nested_case_expressions":
                sum(
                    1
                    for case in cases
                    if case["nested"]
                ),

            "business_rules":
                len(business_rules),

            "where_conditions":
                len(where_conditions),

            "group_by":
                len(group_by),

            "functions":
                len(functions),

            "column_references":
                len(column_references),

            "sqlglot_ast_nodes":
                len(ast_nodes)
        },

        # ====================================================
        # METADATA
        # ====================================================

        "variables":
            variables,

        "set_statements":
            set_statements,

        "tables":
            tables,

        "unique_tables":
            unique_tables,

        "joins":
            joins,

        "column_references":
            column_references,

        "case_expressions":
            cases,

        "business_rules":
            business_rules,

        "where_conditions":
            where_conditions,

        "group_by":
            group_by,

        "functions":
            functions,

        # ====================================================
        # SQLGLOT STRUCTURAL DATA
        # ====================================================

        "sqlglot": {
            "parse_success":
                len(sqlglot_errors) == 0,

            "errors":
                sqlglot_errors,

            "structural_metadata":
                sqlglot_metadata,

            "ast_nodes":
                ast_nodes
        },

        # ====================================================
        # VALIDATION
        # ====================================================

        "validation":
            validation
    }

    return metadata


# ============================================================
# 22. SAVE JSON
# ============================================================

def save_metadata(metadata, sql_file):

    output_file = (
        OUTPUT_FOLDER /
        f"{sql_file.stem}_metadata.json"
    )

    with output_file.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            metadata,
            file,
            indent=2,
            ensure_ascii=False
        )

    return output_file


# ============================================================
# 23. PRINT RESULT
# ============================================================

def print_result(
    metadata,
    output_file
):

    summary = metadata["summary"]
    validation = metadata["validation"]

    print(
        f"  Unique tables          : "
        f"{summary['unique_tables']}"
    )

    print(
        f"  Table occurrences      : "
        f"{summary['table_occurrences']}"
    )

    print(
        f"  JOIN source/extract    : "
        f"{validation['source_join_count']} / "
        f"{validation['extracted_join_count']}"
    )

    print(
        f"  JOIN SQLGlot AST       : "
        f"{validation['sqlglot_join_count']}"
    )

    print(
        f"  CASE source/extract    : "
        f"{validation['source_case_count']} / "
        f"{validation['extracted_case_count']}"
    )

    print(
        f"  CASE SQLGlot AST       : "
        f"{validation['sqlglot_case_count']}"
    )

    print(
        f"  DECLARE source/extract : "
        f"{validation['source_declare_count']} / "
        f"{validation['extracted_variable_count']}"
    )

    print(
        f"  Nested CASE            : "
        f"{summary['nested_case_expressions']}"
    )

    print(
        f"  Business rules         : "
        f"{summary['business_rules']}"
    )

    print(
        f"  WHERE conditions       : "
        f"{summary['where_conditions']}"
    )

    print(
        f"  GROUP BY               : "
        f"{summary['group_by']}"
    )

    print(
        f"  Functions              : "
        f"{summary['functions']}"
    )

    print(
        f"  Column references      : "
        f"{summary['column_references']}"
    )

    print(
        f"  SQLGlot AST nodes      : "
        f"{summary['sqlglot_ast_nodes']}"
    )

    print(
        f"  SQLGlot parse errors   : "
        f"{validation['sqlglot_error_count']}"
    )

    print(
        f"  Metadata validation    : "
        f"{validation['status']}"
    )

    print(
        f"  Output                 : "
        f"{output_file}"
    )

    if validation["critical_errors"]:

        print(
            "  Metadata errors:"
        )

        for error in validation[
            "critical_errors"
        ]:

            print(
                f"    - {error}"
            )

    if validation["warnings"]:

        print(
            "  Validation warnings:"
        )

        for warning in validation[
            "warnings"
        ]:

            print(
                f"    - {warning}"
            )

    sqlglot_errors = metadata[
        "sqlglot"
    ]["errors"]

    if sqlglot_errors:

        print(
            "  SQLGlot error:"
        )

        for error in sqlglot_errors[:2]:

            message = clean(
                error["message"]
            )

            print(
                f"    {message[:250]}"
            )


# ============================================================
# 24. MAIN
# ============================================================

def main():

    sql_files = sorted(
        INPUT_FOLDER.glob("*.sql")
    )

    print("=" * 72)
    print(" FINAL SQLGLOT + T-SQL METADATA PARSER")
    print("=" * 72)

    print(
        f"\nFound {len(sql_files)} SQL files.\n"
    )

    if not sql_files:

        print(
            f"No SQL files found in:\n"
            f"{INPUT_FOLDER}"
        )

        return

    passed = 0
    review = 0

    for sql_file in sql_files:

        try:

            print(
                f"Parsing: {sql_file.name}"
            )

            metadata = parse_file(
                sql_file
            )

            output_file = save_metadata(
                metadata,
                sql_file
            )

            print_result(
                metadata,
                output_file
            )

            status = metadata[
                "validation"
            ]["status"]

            if status.startswith("PASS"):
                passed += 1
            else:
                review += 1

            print()

        except Exception as error:

            review += 1

            print(
                f"ERROR parsing "
                f"{sql_file.name}: "
                f"{error}"
            )

            print()

    print("=" * 72)
    print(" PARSING COMPLETE")
    print("=" * 72)

    print(
        f"Files processed : {len(sql_files)}"
    )

    print(
        f"Metadata passed : {passed}"
    )

    print(
        f"Need review     : {review}"
    )

    print(
        f"Output folder   : {OUTPUT_FOLDER}"
    )


# ============================================================
# 25. RUN
# ============================================================

if __name__ == "__main__":
    main()