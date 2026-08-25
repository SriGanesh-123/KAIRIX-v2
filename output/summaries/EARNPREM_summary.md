# Source Code Summary: EARNPREM

**Business Domain:** Premium (Earned Premium) Calculation

## Purpose
Calculate the earned and unearned premium amounts for each premium record by applying the formula Earned = Written * Earned‑Days / Term‑Days, after validating policy and calculation dates, and write the results to an output file while logging any errors.

## High-Level Narrative
The program opens four sequential files: POLICY‑IN (policy master), PREMIUM‑IN (premium input), PREMIUM‑OUT (calculated premium output) and ERROR‑OUT (error log). It reads the first policy record to establish ordering, then enters a loop reading each premium record. For each premium record it attempts to locate the matching policy by sequentially reading the policy file until the policy numbers match or the end of the policy file is reached. If the policy is found, the program validates the policy effective date, expiry date and the premium calculation date using calendar rules (including leap‑year handling). Once dates are confirmed, it converts the three dates to integer day counts, computes the total term days (inclusive), determines earned days based on where the calculation date falls relative to the effective and expiry dates, and finally calculates Earned Premium = Written Premium * Earned‑Days / Term‑Days and Unearned Premium = Written Premium – Earned Premium. The calculated values together with identifiers are written to PREMIUM‑OUT. If any validation or lookup fails, an appropriate error code and message are written to ERROR‑OUT. Counters for records read, calculated, and errors are displayed at the end of execution. Fatal I/O errors abort processing and set a non‑zero return code.

## Inputs
- POLICY‑IN (sequential file containing policy master records: PI‑POLICY‑NO, PI‑EFFECTIVE‑DATE, PI‑EXPIRY‑DATE, etc.)
- PREMIUM‑IN (sequential file containing premium input records: PRI‑PREMIUM‑ID, PRI‑POLICY‑NO, PRI‑WRITTEN‑PREMIUM, PRI‑CALCULATION‑DATE)
- File status variables WS‑PI‑ST, WS‑PR‑ST, WS‑PO‑ST, WS‑ER‑ST (used to detect I/O errors)

## Outputs
- PREMIUM‑OUT (sequential file with calculated premium records: PRO‑PREMIUM‑ID, PRO‑POLICY‑NO, PRO‑WRITTEN‑PREMIUM, PRO‑EARNED‑PREMIUM, PRO‑UNEARNED‑PREMIUM, PRO‑CALCULATION‑DATE)
- ERROR‑OUT (sequential file with error records: ER‑POLICY‑NO, ER‑CODE, ER‑MESSAGE)
- Console display of processing counters (READ, CALCULATED, ERRORS, I/O ERRORS)
- RETURN‑CODE set to 12 on fatal error

## Key Transformations
- Calendar validation of effective, expiry and calculation dates (numeric check, month/day range, leap‑year handling).
- Conversion of dates to integer day numbers using FUNCTION INTEGER‑OF‑DATE.
- Term‑Days calculation: TERM‑DAYS = EXPIRY‑INT – EFFECTIVE‑INT + 1 (inclusive).
- Earned‑Days determination: 0 if calculation date < effective date; TERM‑DAYS if calculation date > expiry date; otherwise (CALC‑INT – EFFECTIVE‑INT + 1).
- Earned Premium calculation: WS‑EARNED = WRITTEN‑PREMIUM * WS‑EARNED‑DAYS / WS‑TERM‑DAYS.
- Unearned Premium calculation: WS‑UNEARNED = WRITTEN‑PREMIUM – WS‑EARNED.
- Population of output record fields with calculated amounts and identifiers.

## Key Dependencies
- COBOL intrinsic functions: FUNCTION INTEGER‑OF‑DATE, FUNCTION MOD.
- Sequential file definitions for POLICY‑IN, PREMIUM‑IN, PREMIUM‑OUT, ERROR‑OUT.
- Task‑5 POLLOAD and Task‑6 PREMCALC (mentioned in comments as upstream data providers).
- Standard COBOL runtime environment for file handling and arithmetic.

## Business Rules
- EARNED = WRITTEN * EARNED‑DAYS / TERM‑DAYS (term and earned days are inclusive).
- Policy effective date must be a valid calendar date; same for expiry and calculation dates.
- Expiry date must not be earlier than effective date (error E004).
- Term days must be greater than zero; otherwise error E005.
- If calculation date is before effective date, earned days = 0.
- If calculation date is after expiry date, earned days = term days.
- If calculation date falls within the policy period, earned days = (calc‑date – effective‑date + 1).
- Error handling codes: E001 – policy not found; E002 – invalid effective date; E003 – invalid expiry date; E004 – expiry before effective; E005 – invalid term days; E006 – invalid calculation date.
- Input files must be sorted by policy number; out‑of‑order detection raises a fatal error.
- All I/O status codes must be '00' for successful operations; any other status triggers a fatal error.
