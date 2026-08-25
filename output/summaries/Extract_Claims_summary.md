# Source Code Summary: Extract_Claims

**Business Domain:** Claims

## Purpose
Extract claim records from the Guidewire PolicyCenter PostgreSQL replica, validate the policy foreign key, cleanse and enrich the data, enforce claim business rules, pre‑aggregate incurred amounts per policy (BR‑09), and load the results into the data‑warehouse staging tables while logging audit information and quarantining rejected rows.

## High-Level Narrative
When the package runs it first logs a start entry in etl.etl_audit_log. An ADO.NET PostgreSQL source reads all columns from public.claims. Each row is passed to a Lookup that checks that the policy_id exists in stg.policy; non‑matches are sent to an error stream. Matching rows flow to a Derived Column that trims whitespace and upper‑cases claim_type. A second Derived Column adds ETL metadata (etl_load_date) and computes calculated_incurred_amount = paid_amount + reserve_amount - recovery_amount. The rows then enter a Conditional Split that applies four business rule checks: non‑negative monetary fields, tolerance between reported incurred_amount and calculated_incurred_amount (≤ 1.00), chronological order of loss_date ≤ reported_date ≤ claim_date, and claim_status belonging to an allowed list. Valid rows are aggregated by policy_id, summing paid, reserve, recovery, incurred amounts and counting claims (BR‑09 pre‑aggregation). The aggregated rows are fast‑loaded into stg.claims. All error streams (lookup no‑match, conditional‑split invalid rows, source error output) are combined with a Union All component and written to stg.error_quarantine for review. Finally, an Execute SQL task updates etl.etl_audit_log with end time and row counts (rows read, inserted, rejected). An OnError event handler logs unexpected errors to etl.etl_error_log.

## Inputs
- public.claims (source PostgreSQL table via CM_Guidewire_PG_Source)
- stg.policy (target PostgreSQL table used for policy_id lookup)
- Package variables RowsRead, RowsInserted, RowsRejected

## Outputs
- stg.claims (staging table for validated/aggregated claim data)
- stg.error_quarantine (table for rejected or invalid claim rows)
- etl.etl_audit_log (package execution audit record)
- etl.etl_error_log (error handler log entries)

## Key Transformations
- SQL SELECT of claim columns from public.claims
- Lookup join on policy_id to enforce referential integrity (BR‑01, BR‑05)
- Derived Column: TRIM(claim_number) and UPPER(claim_type)
- Derived Column: GETDATE() → etl_load_date; calculated_incurred_amount = paid_amount + reserve_amount - recovery_amount
- Conditional Split enforcing: non‑negative amounts, incurred reconciliation tolerance (|incurred‑calculated| ≤ 1.00), date chronology (loss ≤ reported ≤ claim), allowed claim_status values
- Aggregation by policy_id: SUM(paid_amount), SUM(reserve_amount), SUM(recovery_amount), SUM(incurred_amount), COUNT(claim_id) AS claim_count (BR‑09)
- Union All of all error streams
- FastLoad insert into stg.claims with commit size 10,000

## Key Dependencies
- Connection Manager CM_Guidewire_PG_Source (Npgsql provider)
- Connection Manager CM_DW_PG_Target (Npgsql provider)
- SSIS components: ADO.NET PostgreSQL Source, Lookup, Derived Column, Conditional Split, Aggregation, Union All, OLE DB Destination
- Source table public.claims
- Reference table stg.policy
- Target tables stg.claims, stg.error_quarantine, etl.etl_audit_log, etl.etl_error_log

## Business Rules
- BR‑01/BR‑05: policy_id must exist in stg.policy (referential integrity)
- Monetary fields paid_amount, reserve_amount, recovery_amount must be >= 0.00
- Incurred amount reconciliation: ABS(incurred_amount - (paid_amount + reserve_amount - recovery_amount)) <= 1.00
- BR‑12 lifecycle chronology: loss_date <= reported_date <= claim_date
- claim_status must be one of ('OPEN','IN_PROGRESS','ON_HOLD','CLOSED','REJECTED')
- Pre‑aggregation (BR‑09) of claim financials per policy to avoid duplicate premium totals downstream
