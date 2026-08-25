# Source Code Summary: Extract_Policy

**Business Domain:** Policy (Insurance PolicyCenter)

## Purpose
Extracts policy records from the Guidewire PolicyCenter PostgreSQL source, validates foreign‑key relationships to ACCOUNT and PRODUCER, applies data cleansing and business rule checks, and loads the clean rows into the data‑warehouse staging table while quarantining rejected rows and logging audit information.

## High-Level Narrative
When the package runs it first inserts a start record into etl.etl_audit_log (SQL_LogStart). The main data flow (DFT_Main) reads all columns from public.policy via an ADO.NET source. Each row is passed through a Lookup that checks account_id against stg.account; non‑matching rows are redirected to an error stream. Matching rows continue to a second Lookup that validates producer_id against stg.producer, again redirecting non‑matches. Rows that pass both lookups are sent to a Derived Column component that trims whitespace from policy_number and upper‑cases product_code. A second Derived Column adds the ETL load timestamp (etl_load_date). The cleaned rows then flow to a Conditional Split that enforces business rules on dates, status, and cancellation logic; rows that satisfy all conditions are marked as valid, others are sent to the error path. All error streams (lookup failures, conditional‑split failures, and source‑error output) are merged by a Union All component and written to stg.error_quarantine. Valid rows are bulk‑loaded into stg.policy using fast load. After the data flow completes, a second Execute SQL task (SQL_LogEnd) updates the audit log with end time, status, and row counts (rows read, inserted, rejected). An OnError event handler logs any package‑level errors to etl.etl_error_log.

## Inputs
- public.policy (source PostgreSQL table)
- stg.account (staging table for account reference data)
- stg.producer (staging table for producer reference data)

## Outputs
- stg.policy (staging table for validated policy records)
- stg.error_quarantine (table for rejected/invalid rows)
- etl.etl_audit_log (audit log updated with start/end timestamps and row counts)
- etl.etl_error_log (error log populated by OnError handler)

## Key Transformations
- SELECT policy_id, account_id, producer_id, policy_number, product_code, policy_status, effective_date, expiration_date, cancellation_date, cancellation_reason, updated_timestamp FROM public.policy
- Lookup join on account_id against stg.account (full cache, redirect no‑match)
- Lookup join on producer_id against stg.producer (full cache, redirect no‑match)
- TRIM(policy_number) to remove surrounding whitespace
- UPPER(product_code) to standardize code casing
- Add ETL metadata column etl_load_date with current timestamp
- Conditional split enforcing: expiration_date > effective_date; policy_status in ('ACTIVE','INACTIVE','LAPSED','CANCELLED'); cancellation_date is NULL or falls between effective_date and expiration_date
- Union All to combine all error/no‑match streams
- Fast bulk insert into stg.policy with commit size 10,000

## Key Dependencies
- Connection manager CM_Guidewire_PG_Source (Npgsql provider, source DB)
- Connection manager CM_DW_PG_Target (Npgsql provider, target DW)
- SQL Server Integration Services (SSIS) components: ADO.NET Source, Lookup, Derived Column, Conditional Split, Union All, OLE DB Destination
- Tables: public.policy, stg.account, stg.producer, stg.policy, stg.error_quarantine, etl.etl_audit_log, etl.etl_error_log

## Business Rules
- BR-01: account_id must exist in stg.account (referential integrity)
- BR-01/BR-05: producer_id must exist in stg.producer (referential integrity)
- Expiration date must be later than effective date
- Policy status must be one of: ACTIVE, INACTIVE, LAPSED, CANCELLED
- If cancellation_date is provided it must be after effective_date and before expiration_date; otherwise it may be NULL
