# Source Code Summary: Extract_Location

**Business Domain:** Insurance Policy – Location data extraction and loading

## Purpose
Extracts LOCATION records from the Guidewire PolicyCenter PostgreSQL source, validates the foreign key to POLICY_PERIOD, cleanses address and code fields, applies business rule checks, and loads the valid rows into the data warehouse while quarantining invalid rows and logging audit information.

## High-Level Narrative
When the package runs, it first logs a start entry in etl.etl_audit_log. The main Data Flow task reads all columns from public.location using a PostgreSQL source component. Each row is passed to a Lookup component that checks whether the policy_period_id exists in the staging table stg.policy_period; matching rows continue, non‑matching rows are sent to an error stream. Matching rows undergo a Derived Column transformation that trims whitespace, upper‑cases state and country codes, substitutes empty strings for null address_line2, and adds an ETL load timestamp (GETDATE()). A second Derived Column adds any additional calculated columns (currently only etl_load_date). The rows then flow to a Conditional Split that enforces business rules: building_value and contents_value must be >= 0 and occupancy_type must be one of the allowed codes. Valid rows are bulk‑loaded (fast load) into stg.location. All error streams (lookup no‑match, conditional split invalid rows, and source component errors) are combined with a Union All component and written to stg.error_quarantine for review. After the data flow completes, an end‑log SQL task updates etl.etl_audit_log with end time, status, and row counts. Any package‑level errors trigger an OnError handler that inserts details into etl.etl_error_log.

## Inputs
- public.location (Guidewire PolicyCenter source database)
- stg.policy_period (staging table in the data warehouse for policy period reference)
- etl.etl_audit_log (used for logging start/end of the package)
- etl.etl_error_log (used for logging runtime errors)

## Outputs
- stg.location (staging table for cleaned location records)
- stg.error_quarantine (table capturing rejected/invalid rows)
- etl.etl_audit_log (audit record updated with row counts and status)
- etl.etl_error_log (error record inserted on package failure)

## Key Transformations
- SQL SELECT extracting location_id, policy_period_id, location_number, address_line1, address_line2, city, state_code, zip_code, country_code, occupancy_type, building_value, contents_value from public.location
- Lookup validation of policy_period_id against stg.policy_period (full cache, redirect no‑match rows)
- Derived Column cleansing: TRIM(address_line1), TRIM(city), UPPER(TRIM(state_code)), UPPER(TRIM(country_code)), ISNULL(address_line2, '')
- Derived Column adding ETL metadata: GETDATE() -> etl_load_date
- Conditional Split enforcing business rules on building_value, contents_value, and occupancy_type
- Union All merging all error/no‑match streams into a single error flow
- Fast load bulk insert into stg.location with commit size of 10,000 rows
- Insert into stg.error_quarantine for rejected rows

## Key Dependencies
- Connection Manager CM_Guidewire_PG_Source (PostgreSQL source)
- Connection Manager CM_DW_PG_Target (PostgreSQL target)
- SQL Execute Task for audit start log
- SQL Execute Task for audit end log and row count update
- SQL Execute Task for error logging (etl.etl_error_log)
- ADO.NET PostgreSQL Source component
- Lookup component (policy_period_id validation)
- Derived Column components (data cleansing and metadata)
- Conditional Split component (business rule validation)
- Union All component (error stream consolidation)
- OLE DB Destination components for stg.location and stg.error_quarantine

## Business Rules
- BR-05: policy_period_id in location must exist in stg.policy_period (referential integrity)
- Building value must be greater than or equal to 0.00
- Contents value must be greater than or equal to 0.00
- Occupancy_type must be one of: OWNER_OCCUPIED, TENANT_OCCUPIED, VACANT, UNDER_CONSTRUCTION, OTHER
- Address fields are trimmed of leading/trailing whitespace
- State_code and country_code are stored in upper case
- Null address_line2 values are replaced with an empty string
