# Source Code Summary: POLSTATUS

**Business Domain:** Policy Management

## Purpose
Derive and update the status of insurance policies based on effective, expiry and current dates while preserving existing cancelled statuses, and write the updated policy records and any validation errors to output files.

## High-Level Narrative
The program starts by obtaining the system current date and validating it. It opens three sequential files: POLICY-IN (input master policy records), POLICY-OUT (output updated records) and ERROR-OUT (error log). It then reads each input record in a loop. For each record it validates the effective and expiry dates, checks that expiry is not earlier than effective, and logs specific error records (S001, S002, S003) when validation fails. If dates are valid, the program copies the input record to the output layout, determines the new policy status using the rule: preserve 'CN', otherwise if current date < effective date set 'PN', else if current date <= expiry date set 'AC', else set 'EX'. When the status changes, the update date is set to the current date and a change counter is incremented. The updated record is written to POLICY-OUT. After all records are processed, the program closes all files, displays processing counters (read, written, changed, pending, active, expired, cancelled, rejected, I/O errors) and returns an appropriate return code.

## Inputs
- POLICY-IN sequential file (fields: PI-POLICY-NO, PI-CUSTOMER-ID, PI-AGENT-ID, PI-PRODUCT-TYPE, PI-POLICY-STATUS, PI-EFFECTIVE-DATE, PI-EXPIRY-DATE, PI-WRITTEN-PREMIUM, PI-CREATE-DT, PI-UPDATE-DT)
- System current date (FUNCTION CURRENT-DATE)

## Outputs
- POLICY-OUT sequential file (fields: PO-POLICY-NO, PO-CUSTOMER-ID, PO-AGENT-ID, PO-PRODUCT-TYPE, PO-POLICY-STATUS, PO-EFFECTIVE-DATE, PO-EXPIRY-DATE, PO-WRITTEN-PREMIUM, PO-CREATE-DT, PO-UPDATE-DT)
- ERROR-OUT sequential file (fields: ER-POLICY-NO, ER-CODE, ER-MESSAGE)
- Display of processing counters
- RETURN-CODE (0 for success, 12 for fatal error)

## Key Transformations
- Validation of calendar dates (numeric check, month range, day range, leap‑year handling)
- Comparison of current date with effective and expiry dates to derive status
- Preservation of existing 'CN' (cancelled) status
- Copy of input record to output record with possible status change
- Update of PO-UPDATE-DT when status changes
- Aggregation of counters for read, written, changed, pending, active, expired, cancelled, rejected, and I/O errors

## Key Dependencies
- POLICY-IN, POLICY-OUT and ERROR-OUT file definitions (SELECT statements)
- COBOL intrinsic FUNCTION CURRENT-DATE
- COBOL intrinsic FUNCTION MOD for leap‑year calculation
- Standard COBOL file I/O verbs (OPEN, READ, WRITE, CLOSE)
- Task 5 POLLOAD (provides valid policy master data) – mentioned as a logical dependency

## Business Rules
- If existing PI-POLICY-STATUS = 'CN' then retain 'CN' and count as cancelled.
- If current date < PI-EFFECTIVE-DATE then set status to 'PN' (pending) and count pending.
- If current date <= PI-EXPIRY-DATE then set status to 'AC' (active) and count active.
- Otherwise set status to 'EX' (expired) and count expired.
- Do not derive cancellation status because no cancellation date is available.
- Effective date must be a valid calendar date; otherwise write error record with code S001.
- Expiry date must be a valid calendar date; otherwise write error record with code S002.
- Expiry date must not be earlier than effective date; otherwise write error record with code S003.
- When status changes, PO-UPDATE-DT is set to the current processing date.
- All file status codes must be '00' for successful open, read, write, or close; otherwise a fatal error is raised.
