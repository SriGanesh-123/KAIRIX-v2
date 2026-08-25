# Source Code Summary: EARNPREM

**Business Domain:** Insurance Premium Accounting (Earned Premium Calculation)

## Purpose
Calculate earned and unearned premium amounts for each premium record by matching it to a policy, validating dates, applying the earned‑premium formula, and writing the results or error records.

## High-Level Narrative
The program opens four sequential files (policy input, premium input, premium output, error output). It reads the first policy record, then enters a loop reading premium records until end‑of‑file or a fatal error occurs. For each premium record it searches forward through the policy file until the policy number matches (or EOF). If a matching policy is found, the program validates the policy effective date, expiry date, and the premium calculation date using calendar rules (including leap‑year handling). It also checks that the expiry date is not earlier than the effective date. Once dates are valid, it converts the dates to integer values, computes the inclusive term days, determines earned days based on the calculation date, calculates earned premium as (written premium * earned‑days / term‑days) rounded, caps earned premium at the written amount, derives unearned premium as written minus earned (floored at zero), and writes the premium output record. If any validation or lookup fails, an appropriate error code and message are written to the error file. After processing all records the files are closed and the program terminates.

## Inputs
- POLICY-IN (PI-REC: PI-POLICY-NO, PI-EFFECTIVE-DATE, PI-EXPIRY-DATE)
- PREMIUM-IN (PRI-REC: PRI-PREMIUM-ID, PRI-POLICY-NO, PRI-WRITTEN-PREMIUM, PRI-CALCULATION-DATE)

## Outputs
- PREMIUM-OUT (PRO-REC: PRO-PREMIUM-ID, PRO-POLICY-NO, PRO-WRITTEN-PREMIUM, PRO-EARNED-PREMIUM, PRO-UNEARNED-PREMIUM, PRO-CALCULATION-DATE)
- ERROR-OUT (ER-REC: ER-POLICY-NO, ER-CODE, ER-MESSAGE)

## Key Transformations
- Validate calendar dates for effective, expiry, and calculation dates (including month length and leap‑year rules).
- Convert dates to integer representation using FUNCTION INTEGER-OF-DATE.
- Compute TERM‑DAYS = (ExpiryDateInt - EffectiveDateInt + 1) (inclusive).
- Determine EARNED‑DAYS based on calculation date relative to effective and expiry dates.
- Calculate EARNED = WRITTEN * EARNED‑DAYS / TERM‑DAYS (rounded).
- Cap EARNED at WRITTEN premium.
- Calculate UNEARNED = WRITTEN - EARNED, floor at zero.
- Write result or error records to respective output files.

## Key Dependencies
- COBOL intrinsic FUNCTION INTEGER-OF-DATE
- COBOL intrinsic FUNCTION MOD (used in leap‑year check)
- Sequential file handling (OPEN, READ, WRITE, CLOSE)
- File status variables WS-PI-ST, WS-PR-ST, WS-PO-ST, WS-ER-ST
- Working‑storage fields for date components, calculations, and flags

## Business Rules
- EARNED = WRITTEN * EARNED‑DAYS / TERM‑DAYS (rounded).
- TERM‑DAYS = (ExpiryDate – EffectiveDate) + 1 (inclusive).
- If calculation date < effective date, EARNED‑DAYS = 0.
- If calculation date > expiry date, EARNED‑DAYS = TERM‑DAYS.
- Otherwise, EARNED‑DAYS = (CalculationDate – EffectiveDate) + 1.
- EARNED must not exceed WRITTEN premium; if it does, set EARNED = WRITTEN.
- UNEARNED = WRITTEN – EARNED; if negative, set UNEARNED = 0.
- Policy must exist for each premium record; otherwise error E001.
- All dates must be valid calendar dates; otherwise errors E002 (effective), E003 (expiry), E006 (calculation).
- Expiry date must not be earlier than effective date; otherwise error E004.
- TERM‑DAYS must be greater than zero; otherwise error E005.
