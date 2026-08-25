# Source Code Summary: PolicyCenter_CPP_Breakdown

**Business Domain:** PolicyCenter

## Purpose
Extract a detailed, filtered list of Commercial Package policies for the Agribusiness profit center, including transaction type indicators and premium amounts, for a specified policy period and job close date range.

## High-Level Narrative
The script declares four date variables and sets a policy start, end, and change start date. It then runs a UNION ALL of two SELECT statements that pull policy period records from the PolicyCenter database. Each SELECT joins many reference tables (policy, term, job, account, producer, organization, profit center, UW company, job description, etc.) to enrich the data. For Commercial Package policies the script calculates the written premium by summing amounts from the appropriate transaction table based on the line‑of‑business pattern code; otherwise it uses the pre‑calculated TransactionCostRPT field. Additional CASE expressions create columns that expose values only for specific transaction types (Renewal, Submission, Cancellation, Reinstatement, PolicyChange). After the UNION, an outer SELECT filters rows where the policy period start or the job close date falls between the supplied start and end dates, excludes the generic C.P.P. line, and limits results to the Agribusiness profit center. The final result set is ordered by policy number and is intended for reporting or downstream analysis.

## Inputs
- pc_policyperiod (alias pp)
- pc_policy (alias pol)
- pc_policyTerm (alias polt)
- pc_policyline (alias polline)
- pc_job (alias j)
- pc_account (alias act)
- pc_producercode (alias prod)
- pc_organization (alias org)
- pctl_job (alias jt)
- pctl_policyperiodstatus (alias ppst)
- pctl_bindoption (alias bopt)
- pctl_uwcompanycode (alias uwc)
- pctl_jobdescription_ext (alias jdt)
- pctl_policyperiodsourcetype (alias ppstype)
- pctl_profitcentertype (alias profit)
- pctl_orgfarmuwterritory (alias farmterr)
- pcx_cp7transaction
- pcx_gl7transaction_gle
- pcx_ca7transaction
- pcx_cr7transaction
- pc_imtransaction
- pcx_wc7transaction
- SQL variables @POLSTARTDATE, @POLENDDATE, @CHANGESTARTDATE, @curmthyr

## Outputs
- Result set with columns: ProfitCenter, ProductCode, LineOfBusiness, PolicyNumber, OriginalEffectiveDate, PeriodStart, PeriodEnd, AccountNumber, Company, PrimaryInsuredName, AgentCode, AgentName, FarmUWTerritory, MostRecentTran, SubWritten_Premium, SubWritten_Date, CancelledDate, CancelledEffDate, CancelledPremium, ReinstatedPremium, ReinstatedDate, ReinstatedEffDate, ChangePremium, ChangeDate

## Key Transformations
- Mapping of PatternCode values to human‑readable LineOfBusiness strings.
- Deriving Company code (LRM, WRM, SON) from UWCompany name.
- Calculating Written_Premium for CommercialPackage policies by summing the Amount field from the appropriate transaction table based on PatternCode.
- Conditional CASE columns that expose premium, dates, and effective dates only for specific transaction types (Renewal, Submission, Cancellation, Reinstatement, PolicyChange).
- Union of two queries: first with detailed line‑of‑business mapping, second providing a fallback for C.P.P. line.
- Filtering rows where PeriodStart or JobCloseDate falls within @POLSTARTDATE‑@POLENDDATE, ProductCode = 'CommercialPackage', LineOfBusiness not equal to 'C.P.P.', and ProfitCenter = 'Agribusiness'.
- Ordering final output by PolicyNumber.

## Key Dependencies
- SQL Server (T‑SQL) engine
- PolicyCenter database schema (tables and views listed in inputs)
- Transaction tables for each line of business (pcx_*transaction)
- Reference tables for profit center, UW company, job types, bind options, etc.

## Business Rules
- Include only policies where the policy period status is 'Bound' or 'AuditComplete'.
- Job.CloseDate must be non‑null and earlier than @POLENDDATE.
- Policy IssueDate and PolicyNumber must be present.
- For CommercialPackage policies, use the sum of transaction amounts as the written premium; otherwise use TransactionCostRPT.
- Map UWCompany names to short codes: 'Lightning Rod Mutual' → LRM, 'Western Reserve Mutual' → WRM, 'Sonnenberg Mutual' → SON; default to UNK.
- Expose premium and date fields only for the relevant transaction type (e.g., Cancellation fields only when TranType = 'Cancellation').
- Restrict output to the Agribusiness profit center.
- Exclude rows where LineOfBusiness equals the placeholder 'C.P.P.' when ProductCode = 'CommercialPackage'.
- Date range filter applies to either the policy period start or the job close date.
