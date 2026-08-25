# Source Code Summary: Extract_Coverage

**Business Domain:** PolicyCenter – Coverage data extraction and loading

## Purpose
Extracts rows from the Guidewire PolicyCenter coverage table, validates the foreign key to POLICY_PERIOD, applies data cleansing and business rule checks, and loads the clean rows into the data warehouse staging schema while quarantining invalid rows and logging audit information.

## High-Level Narrative
The package starts by inserting a RUNNING record into etl.etl_audit_log (SQL_LogStart). The main Data Flow (DFT_Main) reads all columns from public.coverage via an ADO.NET PostgreSQL source. Each row is sent to a Lookup component that checks whether the policy_period_id exists in the staging table stg.policy_period; matching rows continue, non‑matching rows are redirected to an error stream. Matching rows flow to a Derived Column component that trims whitespace from coverage_name and converts coverage_code to upper case. A second Derived Column adds the ETL load timestamp (etl_load_date). The enriched rows then pass through a Conditional Split that enforces business rules (non‑negative limit and deductible amounts, end date after start date, and allowed coverage_status values). Valid rows are bulk‑loaded into stg.coverage using fast load. All error streams (lookup no‑match, conditional split invalid rows, and source error output) are combined with a Union All component and written to stg.error_quarantine for review. After the data flow completes, a second Execute SQL task updates the audit log with end time, status COMPLETED, and row counts (SQL_LogEnd). An OnError event handler logs any package‑level errors to etl.etl_error_log.

## Inputs
- public.coverage (Guidewire PolicyCenter PostgreSQL source)
- stg.policy_period (Data Warehouse staging table for policy periods)
- OLE DB Source Error Output (source component error stream)

## Outputs
- stg.coverage (Data Warehouse staging table for coverage)
- stg.error_quarantine (table for rejected/invalid rows)
- etl.etl_audit_log (audit log for package start/end and row counts)
- etl.etl_error_log (error log for package‑level failures)

## Key Transformations
- SELECT coverage_id, policy_period_id, coverage_code, coverage_name, limit_amount, deductible_amount, coverage_start_date, coverage_end_date, coverage_status FROM public.coverage
- Lookup validation of policy_period_id against stg.policy_period
- Derived Column: TRIM(coverage_name) and UPPER(coverage_code)
- Derived Column: GETDATE() -> etl_load_date
- Conditional Split enforcing: limit_amount >= 0, deductible_amount >= 0, coverage_end_date > coverage_start_date, coverage_status IN ('ACTIVE','EXPIRED','CANCELLED','SUSPENDED')
- Union All to consolidate all error/no‑match streams
- Fast bulk load into stg.coverage with commit size 10,000

## Key Dependencies
- Connection Manager CM_Guidewire_PG_Source (PostgreSQL source)
- Connection Manager CM_DW_PG_Target (PostgreSQL target)
- SQL Execute Task for audit start (INSERT into etl.etl_audit_log)
- SQL Execute Task for audit end (UPDATE etl.etl_audit_log)
- SQL Execute Task for error logging (INSERT into etl.etl_error_log)
- ADO.NET PostgreSQL Source component
- Lookup component (policy_period_id validation)
- Derived Column components (cleansing and metadata)
- Conditional Split component (business rule validation)
- Union All component (error stream consolidation)
- OLE DB Destination components for stg.coverage and stg.error_quarantine

## Business Rules
- BR‑01/BR‑05: policy_period_id must exist in stg.policy_period (referential integrity).
- Coverage limit_amount must be greater than or equal to 0.00.
- Coverage deductible_amount must be greater than or equal to 0.00.
- coverage_end_date must be later than coverage_start_date.
- coverage_status must be one of: ACTIVE, EXPIRED, CANCELLED, SUSPENDED.
- coverage_name is trimmed of leading/trailing whitespace.
- coverage_code is converted to upper case.
