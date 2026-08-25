# Source Code Summary: ClaimCenter_Monoline

**Business Domain:** Claims – loss incurred calculation for underwriting and financial reporting.

## Purpose
Generate a claim‑level loss summary (incurred amount) filtered primarily by year‑to‑date, suitable for profit‑and‑loss reporting, by aggregating transaction amounts from ClaimCenter and enriching them with policy and underwriting information.

## High-Level Narrative
The script declares two unused date parameters, then executes a SELECT that aggregates claim transaction data. A deep sub‑query pulls rows from many ClaimCenter view objects (transaction line items, transactions, sets, claims, policies, coverages, exposures, users, etc.) and joins lookup tables for LOB, policy type, transaction codes, cost types, recovery categories, underwriting companies, etc. Within the inner SELECT, numerous CASE expressions derive business fields such as PolSource, TFGTran, Company, CostType, DedStatAmount and a signed TransAmount based on transaction type (Reserve, Payment, Recovery) and the DoesNotErodeReserves flag. Row numbers are generated for reserve lines to distinguish first vs subsequent entries. Dates are normalized to YYYYMMDD strings. The outer SELECT groups by PolSource, LOBCode and PolicyNumber, applies DISTINCT, and sums the calculated TransAmount to produce IncurredAmount per policy/LOB. The final result set contains PolSource, LOBCode, PolicyNumber and the aggregated IncurredAmount.

## Inputs
- vw_curr_cc_transactionlineitem (tl)
- vw_curr_cc_transaction (t)
- vw_curr_cc_transactionset (tset)
- vw_curr_cc_claim (cl)
- vw_curr_cc_policy (po)
- vw_curr_cc_check (ck)
- vw_curr_cc_reserveline (rl)
- vw_curr_cc_exposure (ex)
- vw_curr_cc_coverage (cv)
- vw_curr_cc_contact (clmcont)
- vw_curr_cc_user (u1, u2)
- vw_curr_cc_riskunit (ru)
- vw_curr_cc_classcode (cls)
- vw_curr_cctl_lobcode (lob)
- vw_curr_cctl_policytype (polt)
- vw_curr_cctl_transaction (tt)
- vw_curr_cctl_losscause (tlc)
- vw_curr_cctl_transactionstatus (ts)
- vw_curr_cctl_costtype (CST)
- vw_curr_cctl_costcategory (ccat)
- vw_curr_cctl_linecategory (lc)
- vw_curr_cctl_transactionlifecyclestate (tls)
- vw_curr_cctl_recoverycategory (rv)
- vw_curr_cctl_underwritingcompanytype (uw)
- vw_curr_cctl_coveragesubtype (st)
- @PV_STARTDATE (unused)
- @PV_ENDDATE (unused)

## Outputs
- Result set with columns: PolSource, LOBCode, PolicyNumber, IncurredAmount (sum of TransAmount)

## Key Transformations
- Derive PolSource as 'Legacy' or 'Guidewire' based on PolicyPrefix_Ext.
- Generate row_number partitioned by ClaimNumber, exposure, typecode and cost name for reserve lines.
- Map underwriting company IDs to short codes (LRM, WRM, SON, UNK).
- Convert dates to CHAR(8) YYYYMMDD format for policy effective dates and accounting dates.
- Calculate TFGTran code using complex CASE logic that considers transaction type, cost type, rownum and other flags.
- Determine signed TransAmount: Payments are negative unless DoesNotErodeReserves=1, Recoveries are always negative, others retain sign.
- Format Amount field with leading zeros and sign handling for reporting.
- Compute DedStatAmount for specific coverage types with a ceiling of 99999.
- Aggregate (SUM) TransAmount per PolSource, LOBCode and PolicyNumber, applying DISTINCT to eliminate duplicates.
- Select only required columns for the final output.

## Key Dependencies
- All ClaimCenter view objects prefixed with vw_curr_cc_ (transactionlineitem, transaction, transactionset, claim, policy, check, reserveline, exposure, coverage, contact, user, riskunit, classcode).
- Lookup tables prefixed with vw_curr_cctl_ (lobcode, policytype, transaction, losscause, transactionstatus, costtype, costcategory, linecategory, transactionlifecyclestate, recoverycategory, underwritingcompanytype, coveragesubtype).
- SQL Server window function ROW_NUMBER for reserve line sequencing.
- Standard SQL functions (CASE, ISNULL, CAST, CONVERT, RIGHT, LEFT, UPPER, REPLACE).

## Business Rules
- If PolicyPrefix_Ext is null, the claim source is classified as 'Legacy'; otherwise 'Guidewire'.
- For reserve transactions, assign rownum = ROW_NUMBER partitioned by claim and exposure; non‑reserve rows get rownum = 0.
- TFGTran mapping rules: e.g., Reserve + Indemnity first row => '421', subsequent rows => '431'; Reserve + non‑Indemnity first row => '422', subsequent => '432'; Payment + Indemnity with DoesNotErodeReserves=1 => '321', otherwise '331'; Payment + non‑Indemnity with DoesNotErodeReserves=1 => '322', otherwise '332'; Recovery categories map to specific codes (e.g., Credit_loss + Indemnity => '321', salvage + Indemnity => '341', etc.).
- TransAmount sign rule: Payments are stored as negative amounts unless DoesNotErodeReserves=1 (then positive); Recoveries are always stored as negative; all other transaction types retain their original sign.
- DedStatAmount is populated only for specific coverage types (BP7EmploymentPracticesLiabilityInsurance, BP7SupplementalExtendReportingPeriodEPLI) and capped at 99999; otherwise blank.
- Company code mapping based on underwriting company name: Lightning Rod Mutual => 'LRM', Western Reserve Mutual => 'WRM', Sonnenberg Mutual => 'SON', else 'UNK'.
- CostType determines TFGASL and GWASL codes using predefined mappings (e.g., CPEquipBrkCov => '270', CPINCCCov => '010', certain claim coverages => '010', else '021').
- Only distinct combinations of PolSource, LOBCode and PolicyNumber are retained before summing incurred amounts.
