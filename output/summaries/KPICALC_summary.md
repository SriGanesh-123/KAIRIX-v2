# Source Code Summary: KPICALC

**Business Domain:** Insurance Policy & Premium KPI Reporting

## Purpose
Generate Key Performance Indicator (KPI) statistics for insurance policies by merging a status‑updated policy extract with an earned‑premium extract, validating data quality, reconciling written premiums against earned and unearned components, and producing a KPI summary report and an error file.

## High-Level Narrative
The program opens four sequential files (policy input, premium input, KPI output, error output). It reads the first record from each input file. It then enters a loop that continues until both input files reach end‑of‑file or a fatal error occurs. Inside the loop the program compares the current policy numbers: if they match, it processes the matched pair (increments total policy count, classifies policy status, aggregates premium amounts, aggregates product‑specific totals, checks the reconciliation rule, and writes any data‑quality errors). If the policy number from the policy file is less than the premium file, the policy has no matching premium (missing premium) and an error record is written. If the premium number is less than the policy number, the premium is orphaned (no matching policy) and an error record is written. After handling a case the appropriate next record is read. Out‑of‑order records in either input cause a fatal error. When the loop ends, the program writes a formatted KPI report to KPI‑OUT, closes all files, displays summary counters (total policies, reconciliation errors, data‑quality errors, I/O errors), sets an appropriate RETURN‑CODE based on error severity, and terminates.

## Inputs
- POLICY-IN – status‑updated policy extract (sorted by POLICY‑NO)
- PREMIUM-IN – earned premium extract (sorted by POLICY‑NO)

## Outputs
- KPI-OUT – KPI summary report file
- ERROR-OUT – data‑quality and processing error file

## Key Transformations
- Count total policies and categorize by status codes (AC, PN, EX, CN) and unknown status.
- Count policies by product type (HO, AU) and track unknown product types.
- Aggregate written, earned, and unearned premium amounts across all policies.
- Aggregate written, earned, and unearned premium amounts separately for HO and AU products.
- Compute reconciliation difference: WRITTEN – (EARNED + UNEARNED) and flag when absolute difference exceeds tolerance of 0.01.
- Detect and count out‑of‑order records in both input streams.
- Identify missing premium records (policy without premium) and orphan premium records (premium without policy).
- Generate formatted KPI lines for the KPI‑OUT file (counts and monetary totals).
- Create error records with specific error codes and messages for data‑quality violations.

## Key Dependencies
- File definitions for POLICY-IN, PREMIUM-IN, KPI-OUT, and ERROR-OUT (SELECT statements).
- Working‑storage variables for status flags, counters, totals, and formatting edits.
- COBOL intrinsic FUNCTION ABS for absolute difference calculation.
- Standard COBOL I/O operations (OPEN, READ, WRITE, CLOSE, DISPLAY).

## Business Rules
- Policy status must be one of: AC (active), PN (pending), EX (expired), CN (cancelled). Unknown status triggers error K003.
- Product type must be HO (home) or AU (auto). Unknown product triggers error K004.
- Every policy record must have a matching premium record; otherwise error K001 (missing premium).
- Every premium record must have a matching policy record; otherwise error K002 (orphan premium).
- Reconciliation rule: WRITTEN premium must equal EARNED + UNEARNED within a tolerance of 0.01; violations trigger error K005.
- Input files must be sorted by POLICY‑NO; detection of a decreasing POLICY‑NO sets a fatal error.
- Data‑quality errors increment WS-DQ-ERRORS; I/O errors increment WS-IO-ERRORS; reconciliation errors increment WS-RECON-ERRORS.
- Return‑code 12 for fatal I/O or ordering errors, return‑code 4 when any data‑quality errors are present, otherwise normal return.
