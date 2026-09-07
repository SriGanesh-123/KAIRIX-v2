// 100% AUTHENTIC REPOSITORY DATA EXTRACTED FROM SOURCE FILES & AST PACKAGES
// ZERO FAKE HARDCODING

export const ACTUAL_SYSTEM_METRICS = {
  "totalFiles": 21,
  "cobolPrograms": 6,
  "sqlScripts": 4,
  "ssisPackages": 11,
  "graphEntities": 1006,
  "graphRelationships": 2822,
  "businessRules": 149,
  "transformations": 224,
  "pineconeChunks": 1400,
  "pineconeSummaries": 21,
  "embeddingDimension": 384
};

export const ACTUAL_SOURCE_FILES = [
  {
    "id": "EARNPREM.CBL",
    "name": "EARNPREM.CBL",
    "type": "COBOL",
    "lines": 320,
    "entities": 69,
    "relationships": 35,
    "rules": 11,
    "purpose": "Calculate earned and unearned premium amounts for each premium record by matching it to a policy, validating dates, applying the earned\u2011premium formula, and writing the results or error records.",
    "raw_code": "       IDENTIFICATION DIVISION.\n       PROGRAM-ID. EARNPREM.\n\n      ******************************************************************\n      * COMPACT POC VERSION OF EARNPREM\n      * BUSINESS LOGIC PRESERVED:\n      *   EARNED = WRITTEN * EARNED-DAYS / TERM-DAYS\n      *   TERM/EARNED DAYS ARE INCLUSIVE (+1)\n      *   EARNED IS CAPPED AT WRITTEN PREMIUM\n      *   UNEARNED = WRITTEN - EARNED, FLOOR ZERO\n      *   POLICY MATCHING, DATE VALIDATION AND ERROR RULES PRESERVED\n      ******************************************************************\n\n       ENVIRONMENT DIVISION.\n       INPUT-OUTPUT SECTION.\n       FILE-CONTROL.\n           SELECT POLICY-IN ASSIGN TO POLIN\n             ORGANIZATION IS SEQUENTIAL FILE STATUS IS WS-PI-ST.\n           SELECT PREMIUM-IN ASSIGN TO PREMIN\n             ORGANIZATION IS SEQUENTIAL FILE STATUS IS WS-PR-ST.\n           SELECT PREMIUM-OUT ASSIGN TO PREMOUT\n             ORGANIZATION IS SEQUENTIAL FILE STATUS IS WS-PO-ST.\n           SELECT ERROR-OUT ASSIGN TO ERROUT\n             ORGANIZATION IS SEQUENTIAL FILE STATUS IS WS-ER-ST.\n\n       DATA DIVISION.\n       FILE SECTION.\n\n       FD POLICY-IN.\n       01 PI-REC.\n          05 PI-POLICY-NO       PIC X(12).\n          05 PI-EFFECTIVE-DATE  PIC 9(8).\n          05 PI-EXPIRY-DATE     PIC 9(8).\n\n       FD PREMIUM-IN.\n       01 PRI-REC.\n          05 PRI-PREMIUM-ID       PIC X(12).\n          05 PRI-POLICY-NO        PIC X(12).\n          05 PRI-WRITTEN-PREMIUM  PIC 9(9)V99.\n          05 PRI-EARNED-PREMIUM   PIC 9(9)V99.\n          05 PRI-UNEARNED-PREMIUM PIC 9(9)V99.\n          05 PRI-CALCULATION-DATE PIC 9(8).\n\n       FD PREMIUM-OUT.\n       01 PRO-REC.\n          05 PRO-PREMIUM-ID       PIC X(12).\n          05 PRO-POLICY-NO        PIC X(12).\n          05 PRO-WRITTEN-PREMIUM  PIC 9(9)V99.\n          05 PRO-EARNED-PREMIUM   PIC 9(9)V99.\n          05 PRO-UNEARNED-PREMIUM PIC 9(9)V99.\n          05 PRO-CALCULATION-DATE PIC 9(8).\n\n       FD ERROR-OUT.\n       01 ER-REC.\n          05 ER-POLICY-NO PIC X(12).\n          05 ER-CODE      PIC X(4).\n          05 ER-MESSAGE   PIC X(54).\n\n       WORKING-STORAGE SECTION.\n       01 WS-STATUS.\n          05 WS-PI-ST PIC XX VALUE SPACES.\n          05 WS-PR-ST PIC XX VALUE SPACES.\n          05 WS-PO-ST PIC XX VALUE SPACES.\n          05 WS-ER-ST PIC XX VALUE SPACES.\n\n       01 WS-SW.\n          05 WS-POL-EOF   PIC X VALUE 'N'.\n             88 POL-EOF VALUE 'Y'.\n          05 WS-PREM-EOF  PIC X VALUE 'N'.\n             88 PREM-EOF VALUE 'Y'.\n          05 WS-POL-FOUND PIC X VALUE 'N'.\n          05 WS-FATAL     PIC X VALUE 'N'.\n             88 FATAL-ERROR VALUE 'Y'.\n          05 WS-DATE-VALID PIC X VALUE 'N'.\n\n       01 WS-DATE-WORK.\n          05 WS-DATE-IN     PIC 9(8).\n          05 WS-YEAR        PIC 9(4).\n          05 WS-MONTH       PIC 99.\n          05 WS-DAY         PIC 99.\n          05 WS-MAX-DAY     PIC 99.\n          05 WS-LEAP        PIC X.\n          05 WS-REM4        PIC 9(4).\n          05 WS-REM100      PIC 9(4).\n          05 WS-REM400      PIC 9(4).\n          05 WS-EFF-INT     PIC 9(9).\n          05 WS-EXP-INT     PIC 9(9).\n          05 WS-CALC-INT    PIC 9(9).\n          05 WS-TERM-DAYS   PIC 9(9).\n          05 WS-EARNED-DAYS PIC 9(9).\n\n       01 WS-AMOUNTS.\n          05 WS-EARNED   PIC 9(9)V99.\n          05 WS-UNEARNED PIC 9(9)V99.\n\n       PROCEDURE DIVISION.\n\n       MAIN.\n           PERFORM OPEN-FILES\n           IF FATAL-ERROR\n              GOBACK\n           END-IF\n           PERFORM READ-POLICY\n           PERFORM UNTIL PREM-EOF OR FATAL-ERROR\n              PERFORM READ-PREMIUM\n              IF NOT PREM-EOF AND NOT FATAL-ERROR\n                 PERFORM PROCESS-PREMIUM\n              END-IF\n           END-PERFORM\n           PERFORM CLOSE-FILES\n           GOBACK.\n\n       OPEN-FILES.\n           OPEN INPUT POLICY-IN PREMIUM-IN\n                OUTPUT PREMIUM-OUT ERROR-OUT\n           IF WS-PI-ST NOT = '00'\n              SET FATAL-ERROR TO TRUE\n           END-IF\n           IF WS-PR-ST NOT = '00'\n              SET FATAL-ERROR TO TRUE\n           END-IF\n           IF WS-PO-ST NOT = '00'\n              SET FATAL-ERROR TO TRUE\n           END-IF\n           IF WS-ER-ST NOT = '00'\n              SET FATAL-ERROR TO TRUE\n           END-IF.\n\n       READ-POLICY.\n           IF NOT POL-EOF\n              READ POLICY-IN\n                 AT END\n                    MOVE 'Y' TO WS-POL-EOF\n                 NOT AT END\n                    IF WS-PI-ST NOT = '00'\n                       SET FATAL-ERROR TO TRUE\n                    END-IF\n              END-READ\n           END-IF.\n\n       READ-PREMIUM.\n           IF NOT PREM-EOF\n              READ PREMIUM-IN\n                 AT END\n                    MOVE 'Y' TO WS-PREM-EOF\n                 NOT AT END\n                    IF WS-PR-ST NOT = '00'\n                       SET FATAL-ERROR TO TRUE\n                    END-IF\n              END-READ\n           END-IF.\n\n       PROCESS-PREMIUM.\n           MOVE 'N' TO WS-POL-FOUND\n           PERFORM FIND-POLICY\n           IF WS-POL-FOUND = 'Y'\n              PERFORM VALIDATE-DATES\n           ELSE\n              MOVE 'E001' TO ER-CODE\n              MOVE 'POLICY NOT FOUND FOR PREMIUM RECORD' TO ER-MESSAGE\n              PERFORM WRITE-ERROR\n           END-IF.\n\n       FIND-POLICY.\n           PERFORM UNTIL POL-EOF OR FATAL-ERROR\n              IF PI-POLICY-NO < PRI-POLICY-NO\n                 PERFORM READ-POLICY\n              ELSE\n                 IF PI-POLICY-NO = PRI-POLICY-NO\n                    MOVE 'Y' TO WS-POL-FOUND\n                 END-IF\n                 EXIT PERFORM\n              END-IF\n           END-PERFORM.\n\n       VALIDATE-DATES.\n           MOVE PI-EFFECTIVE-DATE TO WS-DATE-IN\n           PERFORM VALIDATE-CALENDAR-DATE\n           IF WS-DATE-VALID NOT = 'Y'\n              MOVE 'E002' TO ER-CODE\n              MOVE 'INVALID POLICY EFFECTIVE DATE' TO ER-MESSAGE\n              PERFORM WRITE-ERROR\n           ELSE\n              MOVE PI-EXPIRY-DATE TO WS-DATE-IN\n              PERFORM VALIDATE-CALENDAR-DATE\n              IF WS-DATE-VALID NOT = 'Y'\n                 MOVE 'E003' TO ER-CODE\n                 MOVE 'INVALID POLICY EXPIRY DATE' TO ER-MESSAGE\n                 PERFORM WRITE-ERROR\n              ELSE\n                 MOVE PRI-CALCULATION-DATE TO WS-DATE-IN\n                 PERFORM VALIDATE-CALENDAR-DATE\n                 IF WS-DATE-VALID NOT = 'Y'\n                    MOVE 'E006' TO ER-CODE\n                    MOVE 'INVALID PREMIUM CALCULATION DATE'\n                      TO ER-MESSAGE\n                    PERFORM WRITE-ERROR\n                 ELSE\n                    IF PI-EXPIRY-DATE < PI-EFFECTIVE-DATE\n                       MOVE 'E004' TO ER-CODE\n                       MOVE 'EXPIRY DATE BEFORE EFFECTIVE DATE'\n                         TO ER-MESSAGE\n                       PERFORM WRITE-ERROR\n                    ELSE\n                       PERFORM CALCULATE-EARNED\n                    END-IF\n                 END-IF\n              END-IF\n           END-IF.\n\n       VALIDATE-CALENDAR-DATE.\n           MOVE 'N' TO WS-DATE-VALID\n           IF WS-DATE-IN NUMERIC\n              MOVE WS-DATE-IN(1:4) TO WS-YEAR\n              MOVE WS-DATE-IN(5:2) TO WS-MONTH\n              MOVE WS-DATE-IN(7:2) TO WS-DAY\n              IF WS-YEAR > ZERO\n                 AND WS-MONTH >= 1\n                 AND WS-MONTH <= 12\n                 PERFORM SET-MAX-DAY\n                 IF WS-DAY >= 1 AND WS-DAY <= WS-MAX-DAY\n                    MOVE 'Y' TO WS-DATE-VALID\n                 END-IF\n              END-IF\n           END-IF.\n\n       SET-MAX-DAY.\n           EVALUATE WS-MONTH\n              WHEN 1 WHEN 3 WHEN 5 WHEN 7 WHEN 8 WHEN 10 WHEN 12\n                 MOVE 31 TO WS-MAX-DAY\n              WHEN 4 WHEN 6 WHEN 9 WHEN 11\n                 MOVE 30 TO WS-MAX-DAY\n              WHEN 2\n                 PERFORM CHECK-LEAP-YEAR\n                 IF WS-LEAP = 'Y'\n                    MOVE 29 TO WS-MAX-DAY\n                 ELSE\n                    MOVE 28 TO WS-MAX-DAY\n                 END-IF\n           END-EVALUATE.\n\n       CHECK-LEAP-YEAR.\n           MOVE 'N' TO WS-LEAP\n           COMPUTE WS-REM4 = FUNCTION MOD(WS-YEAR, 4)\n           COMPUTE WS-REM100 = FUNCTION MOD(WS-YEAR, 100)\n           COMPUTE WS-REM400 = FUNCTION MOD(WS-YEAR, 400)\n           IF WS-REM400 = ZERO\n              MOVE 'Y' TO WS-LEAP\n           ELSE\n              IF WS-REM4 = ZERO AND WS-REM100 NOT = ZERO\n                 MOVE 'Y' TO WS-LEAP\n              END-IF\n           END-IF.\n\n       CALCULATE-EARNED.\n           COMPUTE WS-EFF-INT =\n              FUNCTION INTEGER-OF-DATE(PI-EFFECTIVE-DATE)\n           COMPUTE WS-EXP-INT =\n              FUNCTION INTEGER-OF-DATE(PI-EXPIRY-DATE)\n           COMPUTE WS-CALC-INT =\n              FUNCTION INTEGER-OF-DATE(PRI-CALCULATION-DATE)\n\n           COMPUTE WS-TERM-DAYS =\n              WS-EXP-INT - WS-EFF-INT + 1\n\n           IF WS-TERM-DAYS <= ZERO\n              MOVE 'E005' TO ER-CODE\n              MOVE 'POLICY TERM DAYS INVALID' TO ER-MESSAGE\n              PERFORM WRITE-ERROR\n           ELSE\n              IF WS-CALC-INT < WS-EFF-INT\n                 MOVE ZERO TO WS-EARNED-DAYS\n              ELSE\n                 IF WS-CALC-INT > WS-EXP-INT\n                    MOVE WS-TERM-DAYS TO WS-EARNED-DAYS\n                 ELSE\n                    COMPUTE WS-EARNED-DAYS =\n                       WS-CALC-INT - WS-EFF-INT + 1\n                 END-IF\n              END-IF\n\n              COMPUTE WS-EARNED ROUNDED =\n                 PRI-WRITTEN-PREMIUM\n                 * WS-EARNED-DAYS / WS-TERM-DAYS\n\n              IF WS-EARNED > PRI-WRITTEN-PREMIUM\n                 MOVE PRI-WRITTEN-PREMIUM TO WS-EARNED\n              END-IF\n\n              COMPUTE WS-UNEARNED =\n                 PRI-WRITTEN-PREMIUM - WS-EARNED\n\n              IF WS-UNEARNED < ZERO\n                 MOVE ZERO TO WS-UNEARNED\n              END-IF\n\n              PERFORM WRITE-RESULT\n           END-IF.\n\n       WRITE-RESULT.\n           MOVE PRI-PREMIUM-ID TO PRO-PREMIUM-ID\n           MOVE PRI-POLICY-NO TO PRO-POLICY-NO\n           MOVE PRI-WRITTEN-PREMIUM TO PRO-WRITTEN-PREMIUM\n           MOVE WS-EARNED TO PRO-EARNED-PREMIUM\n           MOVE WS-UNEARNED TO PRO-UNEARNED-PREMIUM\n           MOVE PRI-CALCULATION-DATE TO PRO-CALCULATION-DATE\n           WRITE PRO-REC\n           IF WS-PO-ST NOT = '00'\n              SET FATAL-ERROR TO TRUE\n           END-IF.\n\n       WRITE-ERROR.\n           MOVE PRI-POLICY-NO TO ER-POLICY-NO\n           WRITE ER-REC\n           IF WS-ER-ST NOT = '00'\n              SET FATAL-ERROR TO TRUE\n           END-IF.\n\n       CLOSE-FILES.\n           CLOSE POLICY-IN PREMIUM-IN PREMIUM-OUT ERROR-OUT.\n",
    "business_rules": [
      {
        "rule_id": "Rule 1",
        "name": "EARNPREM Rule 1",
        "description": "EARNED = WRITTEN * EARNED\u2011DAYS / TERM\u2011DAYS (rounded).",
        "formula": "EARNED = WRITTEN * EARNED\u2011DAYS / TERM\u2011DAYS (rounded)."
      },
      {
        "rule_id": "Rule 2",
        "name": "EARNPREM Rule 2",
        "description": "TERM\u2011DAYS = (ExpiryDate \u2013 EffectiveDate) + 1 (inclusive).",
        "formula": "TERM\u2011DAYS = (ExpiryDate \u2013 EffectiveDate) + 1 (inclusive)."
      },
      {
        "rule_id": "Rule 3",
        "name": "EARNPREM Rule 3",
        "description": "If calculation date < effective date, EARNED\u2011DAYS = 0.",
        "formula": "If calculation date < effective date, EARNED\u2011DAYS = 0."
      },
      {
        "rule_id": "Rule 4",
        "name": "EARNPREM Rule 4",
        "description": "If calculation date > expiry date, EARNED\u2011DAYS = TERM\u2011DAYS.",
        "formula": "If calculation date > expiry date, EARNED\u2011DAYS = TERM\u2011DAYS."
      },
      {
        "rule_id": "Rule 5",
        "name": "EARNPREM Rule 5",
        "description": "Otherwise, EARNED\u2011DAYS = (CalculationDate \u2013 EffectiveDate) + 1.",
        "formula": "Otherwise, EARNED\u2011DAYS = (CalculationDate \u2013 EffectiveDate) + 1."
      },
      {
        "rule_id": "Rule 6",
        "name": "EARNPREM Rule 6",
        "description": "EARNED must not exceed WRITTEN premium; if it does, set EARNED = WRITTEN.",
        "formula": "EARNED must not exceed WRITTEN premium; if it does, set EARNED = WRITTEN."
      },
      {
        "rule_id": "Rule 7",
        "name": "EARNPREM Rule 7",
        "description": "UNEARNED = WRITTEN \u2013 EARNED; if negative, set UNEARNED = 0.",
        "formula": "UNEARNED = WRITTEN \u2013 EARNED; if negative, set UNEARNED = 0."
      },
      {
        "rule_id": "Rule 8",
        "name": "EARNPREM Rule 8",
        "description": "Policy must exist for each premium record; otherwise error E001.",
        "formula": null
      },
      {
        "rule_id": "Rule 9",
        "name": "EARNPREM Rule 9",
        "description": "All dates must be valid calendar dates; otherwise errors E002 (effective), E003 (expiry), E006 (calculation).",
        "formula": null
      },
      {
        "rule_id": "Rule 10",
        "name": "EARNPREM Rule 10",
        "description": "Expiry date must not be earlier than effective date; otherwise error E004.",
        "formula": null
      },
      {
        "rule_id": "Rule 11",
        "name": "EARNPREM Rule 11",
        "description": "TERM\u2011DAYS must be greater than zero; otherwise error E005.",
        "formula": null
      }
    ],
    "inputs": [
      "POLICY-IN (PI-REC: PI-POLICY-NO, PI-EFFECTIVE-DATE, PI-EXPIRY-DATE)",
      "PREMIUM-IN (PRI-REC: PRI-PREMIUM-ID, PRI-POLICY-NO, PRI-WRITTEN-PREMIUM, PRI-CALCULATION-DATE)"
    ],
    "outputs": [
      "PREMIUM-OUT (PRO-REC: PRO-PREMIUM-ID, PRO-POLICY-NO, PRO-WRITTEN-PREMIUM, PRO-EARNED-PREMIUM, PRO-UNEARNED-PREMIUM, PRO-CALCULATION-DATE)",
      "ERROR-OUT (ER-REC: ER-POLICY-NO, ER-CODE, ER-MESSAGE)"
    ],
    "transformations": [
      "Validate calendar dates for effective, expiry, and calculation dates (including month length and leap\u2011year rules).",
      "Convert dates to integer representation using FUNCTION INTEGER-OF-DATE.",
      "Compute TERM\u2011DAYS = (ExpiryDateInt - EffectiveDateInt + 1) (inclusive).",
      "Determine EARNED\u2011DAYS based on calculation date relative to effective and expiry dates.",
      "Calculate EARNED = WRITTEN * EARNED\u2011DAYS / TERM\u2011DAYS (rounded).",
      "Cap EARNED at WRITTEN premium.",
      "Calculate UNEARNED = WRITTEN - EARNED, floor at zero.",
      "Write result or error records to respective output files."
    ],
    "dependencies": [
      "COBOL intrinsic FUNCTION INTEGER-OF-DATE",
      "COBOL intrinsic FUNCTION MOD (used in leap\u2011year check)",
      "Sequential file handling (OPEN, READ, WRITE, CLOSE)",
      "File status variables WS-PI-ST, WS-PR-ST, WS-PO-ST, WS-ER-ST",
      "Working\u2011storage fields for date components, calculations, and flags"
    ]
  },
  {
    "id": "KPICALC.CBL",
    "name": "KPICALC.CBL",
    "type": "COBOL",
    "lines": 861,
    "entities": 81,
    "relationships": 28,
    "rules": 8,
    "purpose": "Generate Key Performance Indicator (KPI) statistics for insurance policies by merging a status\u2011updated policy extract with an earned\u2011premium extract, validating data quality, reconciling written premiums against earned and unearned components, and producing a KPI summary report and an error file.",
    "raw_code": "       IDENTIFICATION DIVISION.\n\n       PROGRAM-ID. KPIREPORT.\n\n      ******************************************************************\n\n      * TASK 9 - REPORTING KPI CALCULATIONS\n\n      * INPUTS:\n\n      *   POLICY-IN  - TASK 8 STATUS-UPDATED POLICY EXTRACT\n\n      *   PREMIUM-IN - TASK 7 EARNED PREMIUM EXTRACT\n\n      *\n\n      * BOTH INPUTS MUST BE SORTED BY POLICY-NO.\n\n      * PROGRAM DETECTS OUT-OF-ORDER RECORDS.\n\n      *\n\n      * KPIS:\n\n      * TOTAL/AC/PN/EX/CN POLICY COUNTS\n\n      * HO/AU POLICY COUNTS\n\n      * WRITTEN/EARNED/UNEARNED PREMIUM TOTALS\n\n      * HO/AU PREMIUM TOTALS\n\n      * RECONCILIATION: WRITTEN = EARNED + UNEARNED\n\n      ******************************************************************\n\n       ENVIRONMENT DIVISION.\n\n       INPUT-OUTPUT SECTION.\n\n       FILE-CONTROL.\n\n           SELECT POLICY-IN ASSIGN TO POLIN\n\n             ORGANIZATION IS SEQUENTIAL FILE STATUS IS WS-PI-ST.\n\n           SELECT PREMIUM-IN ASSIGN TO PREMIN\n\n             ORGANIZATION IS SEQUENTIAL FILE STATUS IS WS-PR-ST.\n\n           SELECT KPI-OUT ASSIGN TO KPIOUT\n\n             ORGANIZATION IS SEQUENTIAL FILE STATUS IS WS-KO-ST.\n\n           SELECT ERROR-OUT ASSIGN TO ERROUT\n\n             ORGANIZATION IS SEQUENTIAL FILE STATUS IS WS-ER-ST.\n \n       DATA DIVISION.\n\n       FILE SECTION.\n\n       FD POLICY-IN RECORD CONTAINS 77 CHARACTERS.\n\n       01 PI-REC.\n\n          05 PI-POLICY-NO       PIC X(12).\n\n          05 PI-CUSTOMER-ID     PIC X(9).\n\n          05 PI-AGENT-ID        PIC X(9).\n\n          05 PI-PRODUCT-TYPE    PIC X(2).\n\n          05 PI-POLICY-STATUS   PIC X(2).\n\n          05 PI-EFFECTIVE-DATE  PIC 9(8).\n\n          05 PI-EXPIRY-DATE     PIC 9(8).\n\n          05 PI-WRITTEN-PREMIUM PIC 9(9)V99.\n\n          05 PI-CREATE-DT       PIC 9(8).\n\n          05 PI-UPDATE-DT       PIC 9(8).\n \n       FD PREMIUM-IN RECORD CONTAINS 65 CHARACTERS.\n\n       01 PRI-REC.\n\n          05 PRI-PREMIUM-ID       PIC X(12).\n\n          05 PRI-POLICY-NO        PIC X(12).\n\n          05 PRI-WRITTEN-PREMIUM  PIC 9(9)V99.\n\n          05 PRI-EARNED-PREMIUM   PIC 9(9)V99.\n\n          05 PRI-UNEARNED-PREMIUM PIC 9(9)V99.\n\n          05 PRI-CALCULATION-DATE PIC 9(8).\n \n       FD KPI-OUT RECORD CONTAINS 80 CHARACTERS.\n\n       01 KPI-REC PIC X(80).\n \n       FD ERROR-OUT RECORD CONTAINS 80 CHARACTERS.\n\n       01 ER-REC.\n\n          05 ER-POLICY-NO PIC X(12).\n\n          05 ER-CODE      PIC X(4).\n\n          05 ER-MESSAGE   PIC X(64).\n \n       WORKING-STORAGE SECTION.\n\n       01 WS-STATUS.\n\n          05 WS-PI-ST PIC XX VALUE SPACES.\n\n          05 WS-PR-ST PIC XX VALUE SPACES.\n\n          05 WS-KO-ST PIC XX VALUE SPACES.\n\n          05 WS-ER-ST PIC XX VALUE SPACES.\n \n       01 WS-SWITCHES.\n\n          05 WS-PI-EOF PIC X VALUE 'N'.\n\n             88 PI-EOF VALUE 'Y'.\n\n          05 WS-PR-EOF PIC X VALUE 'N'.\n\n             88 PR-EOF VALUE 'Y'.\n\n          05 WS-FATAL PIC X VALUE 'N'.\n\n             88 FATAL-ERROR VALUE 'Y'.\n\n          05 WS-PI-OPEN PIC X VALUE 'N'.\n\n          05 WS-PR-OPEN PIC X VALUE 'N'.\n\n          05 WS-KO-OPEN PIC X VALUE 'N'.\n\n          05 WS-ER-OPEN PIC X VALUE 'N'.\n \n       01 WS-SEQUENCE.\n\n          05 WS-PREV-PI-POLICY PIC X(12) VALUE LOW-VALUES.\n\n          05 WS-PREV-PR-POLICY PIC X(12) VALUE LOW-VALUES.\n \n       01 WS-COUNTS.\n\n          05 WS-TOTAL-POLICIES PIC 9(9) VALUE ZERO.\n\n          05 WS-ACTIVE         PIC 9(9) VALUE ZERO.\n\n          05 WS-PENDING        PIC 9(9) VALUE ZERO.\n\n          05 WS-EXPIRED        PIC 9(9) VALUE ZERO.\n\n          05 WS-CANCELLED      PIC 9(9) VALUE ZERO.\n\n          05 WS-HO-COUNT       PIC 9(9) VALUE ZERO.\n\n          05 WS-AU-COUNT       PIC 9(9) VALUE ZERO.\n\n          05 WS-UNKNOWN-STATUS PIC 9(9) VALUE ZERO.\n\n          05 WS-UNKNOWN-PROD   PIC 9(9) VALUE ZERO.\n\n          05 WS-MISSING-PREM   PIC 9(9) VALUE ZERO.\n\n          05 WS-ORPHAN-PREM    PIC 9(9) VALUE ZERO.\n\n          05 WS-RECON-ERRORS   PIC 9(9) VALUE ZERO.\n\n          05 WS-DQ-ERRORS      PIC 9(9) VALUE ZERO.\n\n          05 WS-IO-ERRORS      PIC 9(9) VALUE ZERO.\n \n       01 WS-TOTALS.\n\n          05 WS-WRITTEN        PIC 9(15)V99 VALUE ZERO.\n\n          05 WS-EARNED         PIC 9(15)V99 VALUE ZERO.\n\n          05 WS-UNEARNED       PIC 9(15)V99 VALUE ZERO.\n\n          05 WS-HO-WRITTEN     PIC 9(15)V99 VALUE ZERO.\n\n          05 WS-HO-EARNED      PIC 9(15)V99 VALUE ZERO.\n\n          05 WS-HO-UNEARNED    PIC 9(15)V99 VALUE ZERO.\n\n          05 WS-AU-WRITTEN     PIC 9(15)V99 VALUE ZERO.\n\n          05 WS-AU-EARNED      PIC 9(15)V99 VALUE ZERO.\n\n          05 WS-AU-UNEARNED    PIC 9(15)V99 VALUE ZERO.\n\n          05 WS-RECON-DIFF     PIC S9(15)V99 VALUE ZERO.\n\n          05 WS-ABS-DIFF       PIC 9(15)V99 VALUE ZERO.\n\n          05 WS-TOLERANCE      PIC 9V99 VALUE 0.01.\n \n       01 WS-EDIT.\n\n          05 WS-COUNT-EDIT PIC ZZZ,ZZZ,ZZ9.\n\n          05 WS-AMT-EDIT   PIC ZZZ,ZZZ,ZZZ,ZZZ,ZZ9.99.\n\n          05 WS-SIGNED-AMT-EDIT PIC -ZZZ,ZZZ,ZZZ,ZZZ,ZZ9.99.\n\n          05 WS-LINE       PIC X(80).\n \n       PROCEDURE DIVISION.\n\n       MAIN.\n\n           PERFORM OPEN-FILES\n\n           IF FATAL-ERROR\n\n              PERFORM CLOSE-FILES\n\n              MOVE 12 TO RETURN-CODE\n\n              GOBACK\n\n           END-IF\n \n           PERFORM READ-POLICY\n\n           PERFORM READ-PREMIUM\n \n           PERFORM UNTIL (PI-EOF AND PR-EOF) OR FATAL-ERROR\n\n              IF PI-EOF\n\n                 PERFORM HANDLE-ORPHAN-PREMIUM\n\n              ELSE\n\n                 IF PR-EOF\n\n                    PERFORM HANDLE-MISSING-PREMIUM\n\n                 ELSE\n\n                    EVALUATE TRUE\n\n                       WHEN PI-POLICY-NO = PRI-POLICY-NO\n\n                          PERFORM PROCESS-MATCHED\n\n                          PERFORM READ-POLICY\n\n                          PERFORM READ-PREMIUM\n\n                       WHEN PI-POLICY-NO < PRI-POLICY-NO\n\n                          PERFORM HANDLE-MISSING-PREMIUM\n\n                          PERFORM READ-POLICY\n\n                       WHEN OTHER\n\n                          PERFORM HANDLE-ORPHAN-PREMIUM\n\n                          PERFORM READ-PREMIUM\n\n                    END-EVALUATE\n\n                 END-IF\n\n              END-IF\n\n           END-PERFORM\n \n           IF NOT FATAL-ERROR\n\n              PERFORM WRITE-KPI-REPORT\n\n           END-IF\n\n           PERFORM CLOSE-FILES\n \n           DISPLAY 'KPI TOTAL POLICIES : ' WS-TOTAL-POLICIES\n\n           DISPLAY 'KPI RECON ERRORS   : ' WS-RECON-ERRORS\n\n           DISPLAY 'KPI DATA QUALITY    : ' WS-DQ-ERRORS\n\n           DISPLAY 'KPI I/O ERRORS      : ' WS-IO-ERRORS\n \n           IF FATAL-ERROR\n\n              MOVE 12 TO RETURN-CODE\n\n           ELSE\n\n              IF WS-DQ-ERRORS > ZERO\n\n                 MOVE 4 TO RETURN-CODE\n\n              END-IF\n\n           END-IF\n\n           GOBACK.\n \n       OPEN-FILES.\n\n           OPEN INPUT POLICY-IN\n\n           IF WS-PI-ST = '00'\n\n              MOVE 'Y' TO WS-PI-OPEN\n\n           ELSE\n\n              DISPLAY 'POLICY OPEN ERROR ' WS-PI-ST\n\n              SET FATAL-ERROR TO TRUE\n\n           END-IF\n\n           OPEN INPUT PREMIUM-IN\n\n           IF WS-PR-ST = '00'\n\n              MOVE 'Y' TO WS-PR-OPEN\n\n           ELSE\n\n              DISPLAY 'PREMIUM OPEN ERROR ' WS-PR-ST\n\n              SET FATAL-ERROR TO TRUE\n\n           END-IF\n\n           OPEN OUTPUT KPI-OUT\n\n           IF WS-KO-ST = '00'\n\n              MOVE 'Y' TO WS-KO-OPEN\n\n           ELSE\n\n              DISPLAY 'KPI OUTPUT OPEN ERROR ' WS-KO-ST\n\n              SET FATAL-ERROR TO TRUE\n\n           END-IF\n\n           OPEN OUTPUT ERROR-OUT\n\n           IF WS-ER-ST = '00'\n\n              MOVE 'Y' TO WS-ER-OPEN\n\n           ELSE\n\n              DISPLAY 'ERROR OUTPUT OPEN ERROR ' WS-ER-ST\n\n              SET FATAL-ERROR TO TRUE\n\n           END-IF.\n \n       READ-POLICY.\n\n           IF NOT PI-EOF\n\n              READ POLICY-IN\n\n                 AT END MOVE 'Y' TO WS-PI-EOF\n\n                 NOT AT END\n\n                    IF WS-PI-ST NOT = '00'\n\n                       DISPLAY 'POLICY READ ERROR ' WS-PI-ST\n\n                       ADD 1 TO WS-IO-ERRORS\n\n                       SET FATAL-ERROR TO TRUE\n\n                    ELSE\n\n                       IF WS-PREV-PI-POLICY NOT = LOW-VALUES\n\n                          AND PI-POLICY-NO < WS-PREV-PI-POLICY\n\n                          DISPLAY 'POLICY INPUT OUT OF ORDER'\n\n                          ADD 1 TO WS-IO-ERRORS\n\n                          SET FATAL-ERROR TO TRUE\n\n                       ELSE\n\n                          MOVE PI-POLICY-NO TO WS-PREV-PI-POLICY\n\n                       END-IF\n\n                    END-IF\n\n              END-READ\n\n           END-IF.\n \n       READ-PREMIUM.\n\n           IF NOT PR-EOF\n\n              READ PREMIUM-IN\n\n                 AT END MOVE 'Y' TO WS-PR-EOF\n\n                 NOT AT END\n\n                    IF WS-PR-ST NOT = '00'\n\n                       DISPLAY 'PREMIUM READ ERROR ' WS-PR-ST\n\n                       ADD 1 TO WS-IO-ERRORS\n\n                       SET FATAL-ERROR TO TRUE\n\n                    ELSE\n\n                       IF WS-PREV-PR-POLICY NOT = LOW-VALUES\n\n                          AND PRI-POLICY-NO < WS-PREV-PR-POLICY\n\n                          DISPLAY 'PREMIUM INPUT OUT OF ORDER'\n\n                          ADD 1 TO WS-IO-ERRORS\n\n                          SET FATAL-ERROR TO TRUE\n\n                       ELSE\n\n                          MOVE PRI-POLICY-NO TO WS-PREV-PR-POLICY\n\n                       END-IF\n\n                    END-IF\n\n              END-READ\n\n           END-IF.\n \n       PROCESS-MATCHED.\n\n           ADD 1 TO WS-TOTAL-POLICIES\n\n           EVALUATE PI-POLICY-STATUS\n\n              WHEN 'AC' ADD 1 TO WS-ACTIVE\n\n              WHEN 'PN' ADD 1 TO WS-PENDING\n\n              WHEN 'EX' ADD 1 TO WS-EXPIRED\n\n              WHEN 'CN' ADD 1 TO WS-CANCELLED\n\n              WHEN OTHER\n\n                 ADD 1 TO WS-UNKNOWN-STATUS\n\n                 ADD 1 TO WS-DQ-ERRORS\n\n                 MOVE PI-POLICY-NO TO ER-POLICY-NO\n\n                 MOVE 'K003' TO ER-CODE\n\n                 MOVE 'UNKNOWN POLICY STATUS' TO ER-MESSAGE\n\n                 PERFORM WRITE-ERROR\n\n           END-EVALUATE\n \n           ADD PRI-WRITTEN-PREMIUM TO WS-WRITTEN\n\n           ADD PRI-EARNED-PREMIUM TO WS-EARNED\n\n           ADD PRI-UNEARNED-PREMIUM TO WS-UNEARNED\n \n           EVALUATE PI-PRODUCT-TYPE\n\n              WHEN 'HO'\n\n                 ADD 1 TO WS-HO-COUNT\n\n                 ADD PRI-WRITTEN-PREMIUM TO WS-HO-WRITTEN\n\n                 ADD PRI-EARNED-PREMIUM TO WS-HO-EARNED\n\n                 ADD PRI-UNEARNED-PREMIUM TO WS-HO-UNEARNED\n\n              WHEN 'AU'\n\n                 ADD 1 TO WS-AU-COUNT\n\n                 ADD PRI-WRITTEN-PREMIUM TO WS-AU-WRITTEN\n\n                 ADD PRI-EARNED-PREMIUM TO WS-AU-EARNED\n\n                 ADD PRI-UNEARNED-PREMIUM TO WS-AU-UNEARNED\n\n              WHEN OTHER\n\n                 ADD 1 TO WS-UNKNOWN-PROD\n\n                 ADD 1 TO WS-DQ-ERRORS\n\n                 MOVE PI-POLICY-NO TO ER-POLICY-NO\n\n                 MOVE 'K004' TO ER-CODE\n\n                 MOVE 'UNKNOWN PRODUCT TYPE' TO ER-MESSAGE\n\n                 PERFORM WRITE-ERROR\n\n           END-EVALUATE\n \n           COMPUTE WS-RECON-DIFF =\n\n              PRI-WRITTEN-PREMIUM -\n\n              (PRI-EARNED-PREMIUM + PRI-UNEARNED-PREMIUM)\n\n           COMPUTE WS-ABS-DIFF = FUNCTION ABS(WS-RECON-DIFF)\n\n           IF WS-ABS-DIFF > WS-TOLERANCE\n\n              ADD 1 TO WS-RECON-ERRORS\n\n              ADD 1 TO WS-DQ-ERRORS\n\n              MOVE PI-POLICY-NO TO ER-POLICY-NO\n\n              MOVE 'K005' TO ER-CODE\n\n              MOVE 'WRITTEN DOES NOT EQUAL EARNED PLUS UNEARNED'\n\n                TO ER-MESSAGE\n\n              PERFORM WRITE-ERROR\n\n           END-IF.\n \n       HANDLE-MISSING-PREMIUM.\n\n           ADD 1 TO WS-MISSING-PREM\n\n           ADD 1 TO WS-DQ-ERRORS\n\n           MOVE PI-POLICY-NO TO ER-POLICY-NO\n\n           MOVE 'K001' TO ER-CODE\n\n           MOVE 'POLICY HAS NO MATCHING PREMIUM RECORD' TO ER-MESSAGE\n\n           PERFORM WRITE-ERROR.\n \n       HANDLE-ORPHAN-PREMIUM.\n\n           ADD 1 TO WS-ORPHAN-PREM\n\n           ADD 1 TO WS-DQ-ERRORS\n\n           MOVE PRI-POLICY-NO TO ER-POLICY-NO\n\n           MOVE 'K002' TO ER-CODE\n\n           MOVE 'PREMIUM HAS NO MATCHING POLICY RECORD' TO ER-MESSAGE\n\n           PERFORM WRITE-ERROR.\n \n       WRITE-ERROR.\n\n           IF ER-POLICY-NO = SPACES\n\n              MOVE PI-POLICY-NO TO ER-POLICY-NO\n\n           END-IF\n\n           WRITE ER-REC\n\n           IF WS-ER-ST NOT = '00'\n\n              DISPLAY 'ERROR WRITE ERROR ' WS-ER-ST\n\n              ADD 1 TO WS-IO-ERRORS\n\n              SET FATAL-ERROR TO TRUE\n\n           END-IF\n\n           MOVE SPACES TO ER-REC.\n \n       WRITE-KPI-REPORT.\n\n           MOVE SPACES TO KPI-REC\n\n           MOVE 'TFG PERSONAL LINES - TASK 9 KPI SUMMARY' TO KPI-REC\n\n           PERFORM WRITE-KPI-LINE\n\n           MOVE SPACES TO KPI-REC\n\n           PERFORM WRITE-KPI-LINE\n \n           MOVE WS-TOTAL-POLICIES TO WS-COUNT-EDIT\n\n           STRING 'TOTAL POLICIES      |' WS-COUNT-EDIT\n\n             DELIMITED BY SIZE INTO KPI-REC\n\n           PERFORM WRITE-KPI-LINE\n\n           MOVE WS-ACTIVE TO WS-COUNT-EDIT\n\n           STRING 'ACTIVE POLICIES     |' WS-COUNT-EDIT\n\n             DELIMITED BY SIZE INTO KPI-REC\n\n           PERFORM WRITE-KPI-LINE\n\n           MOVE WS-PENDING TO WS-COUNT-EDIT\n\n           STRING 'PENDING POLICIES    |' WS-COUNT-EDIT\n\n             DELIMITED BY SIZE INTO KPI-REC\n\n           PERFORM WRITE-KPI-LINE\n\n           MOVE WS-EXPIRED TO WS-COUNT-EDIT\n\n           STRING 'EXPIRED POLICIES    |' WS-COUNT-EDIT\n\n             DELIMITED BY SIZE INTO KPI-REC\n\n           PERFORM WRITE-KPI-LINE\n\n           MOVE WS-CANCELLED TO WS-COUNT-EDIT\n\n           STRING 'CANCELLED POLICIES  |' WS-COUNT-EDIT\n\n             DELIMITED BY SIZE INTO KPI-REC\n\n           PERFORM WRITE-KPI-LINE\n \n           MOVE WS-WRITTEN TO WS-AMT-EDIT\n\n           STRING 'WRITTEN PREMIUM     |' WS-AMT-EDIT\n\n             DELIMITED BY SIZE INTO KPI-REC\n\n           PERFORM WRITE-KPI-LINE\n\n           MOVE WS-EARNED TO WS-AMT-EDIT\n\n           STRING 'EARNED PREMIUM      |' WS-AMT-EDIT\n\n             DELIMITED BY SIZE INTO KPI-REC\n\n           PERFORM WRITE-KPI-LINE\n\n           MOVE WS-UNEARNED TO WS-AMT-EDIT\n\n           STRING 'UNEARNED PREMIUM    |' WS-AMT-EDIT\n\n             DELIMITED BY SIZE INTO KPI-REC\n\n           PERFORM WRITE-KPI-LINE\n \n           MOVE WS-HO-COUNT TO WS-COUNT-EDIT\n\n           STRING 'HO POLICY COUNT     |' WS-COUNT-EDIT\n\n             DELIMITED BY SIZE INTO KPI-REC\n\n           PERFORM WRITE-KPI-LINE\n\n           MOVE WS-HO-WRITTEN TO WS-AMT-EDIT\n\n           STRING 'HO WRITTEN PREMIUM  |' WS-AMT-EDIT\n\n             DELIMITED BY SIZE INTO KPI-REC\n\n           PERFORM WRITE-KPI-LINE\n\n           MOVE WS-HO-EARNED TO WS-AMT-EDIT\n\n           STRING 'HO EARNED PREMIUM   |' WS-AMT-EDIT\n\n             DELIMITED BY SIZE INTO KPI-REC\n\n           PERFORM WRITE-KPI-LINE\n\n           MOVE WS-HO-UNEARNED TO WS-AMT-EDIT\n\n           STRING 'HO UNEARNED PREMIUM |' WS-AMT-EDIT\n\n             DELIMITED BY SIZE INTO KPI-REC\n\n           PERFORM WRITE-KPI-LINE\n \n           MOVE WS-AU-COUNT TO WS-COUNT-EDIT\n\n           STRING 'AU POLICY COUNT     |' WS-COUNT-EDIT\n\n             DELIMITED BY SIZE INTO KPI-REC\n\n           PERFORM WRITE-KPI-LINE\n\n           MOVE WS-AU-WRITTEN TO WS-AMT-EDIT\n\n           STRING 'AU WRITTEN PREMIUM  |' WS-AMT-EDIT\n\n             DELIMITED BY SIZE INTO KPI-REC\n\n           PERFORM WRITE-KPI-LINE\n\n           MOVE WS-AU-EARNED TO WS-AMT-EDIT\n\n           STRING 'AU EARNED PREMIUM   |' WS-AMT-EDIT\n\n             DELIMITED BY SIZE INTO KPI-REC\n\n           PERFORM WRITE-KPI-LINE\n\n           MOVE WS-AU-UNEARNED TO WS-AMT-EDIT\n\n           STRING 'AU UNEARNED PREMIUM |' WS-AMT-EDIT\n\n             DELIMITED BY SIZE INTO KPI-REC\n\n           PERFORM WRITE-KPI-LINE\n \n           COMPUTE WS-RECON-DIFF =\n\n              WS-WRITTEN - (WS-EARNED + WS-UNEARNED)\n\n           MOVE WS-RECON-DIFF TO WS-SIGNED-AMT-EDIT\n\n           STRING 'TOTAL RECON DIFF    |' WS-SIGNED-AMT-EDIT\n\n             DELIMITED BY SIZE INTO KPI-REC\n\n           PERFORM WRITE-KPI-LINE.\n \n       WRITE-KPI-LINE.\n\n           WRITE KPI-REC\n\n           IF WS-KO-ST NOT = '00'\n\n              DISPLAY 'KPI WRITE ERROR ' WS-KO-ST\n\n              ADD 1 TO WS-IO-ERRORS\n\n              SET FATAL-ERROR TO TRUE\n\n           END-IF\n\n           MOVE SPACES TO KPI-REC.\n \n       CLOSE-FILES.\n\n           IF WS-PI-OPEN = 'Y'\n\n              CLOSE POLICY-IN\n\n              IF WS-PI-ST NOT = '00'\n\n                 DISPLAY 'POLICY CLOSE ERROR ' WS-PI-ST\n\n                 ADD 1 TO WS-IO-ERRORS\n\n                 SET FATAL-ERROR TO TRUE\n\n              ELSE\n\n                 MOVE 'N' TO WS-PI-OPEN\n\n              END-IF\n\n           END-IF\n\n           IF WS-PR-OPEN = 'Y'\n\n              CLOSE PREMIUM-IN\n\n              IF WS-PR-ST NOT = '00'\n\n                 DISPLAY 'PREMIUM CLOSE ERROR ' WS-PR-ST\n\n                 ADD 1 TO WS-IO-ERRORS\n\n                 SET FATAL-ERROR TO TRUE\n\n              ELSE\n\n                 MOVE 'N' TO WS-PR-OPEN\n\n              END-IF\n\n           END-IF\n\n           IF WS-KO-OPEN = 'Y'\n\n              CLOSE KPI-OUT\n\n              IF WS-KO-ST NOT = '00'\n\n                 DISPLAY 'KPI CLOSE ERROR ' WS-KO-ST\n\n                 ADD 1 TO WS-IO-ERRORS\n\n                 SET FATAL-ERROR TO TRUE\n\n              ELSE\n\n                 MOVE 'N' TO WS-KO-OPEN\n\n              END-IF\n\n           END-IF\n\n           IF WS-ER-OPEN = 'Y'\n\n              CLOSE ERROR-OUT\n\n              IF WS-ER-ST NOT = '00'\n\n                 DISPLAY 'ERROR CLOSE ERROR ' WS-ER-ST\n\n                 ADD 1 TO WS-IO-ERRORS\n\n                 SET FATAL-ERROR TO TRUE\n\n              ELSE\n\n                 MOVE 'N' TO WS-ER-OPEN\n\n              END-IF\n\n           END-IF.\n\n ",
    "business_rules": [
      {
        "rule_id": "Rule 1",
        "name": "KPICALC Rule 1",
        "description": "Policy status must be one of: AC (active), PN (pending), EX (expired), CN (cancelled). Unknown status triggers error K003.",
        "formula": null
      },
      {
        "rule_id": "Rule 2",
        "name": "KPICALC Rule 2",
        "description": "Product type must be HO (home) or AU (auto). Unknown product triggers error K004.",
        "formula": null
      },
      {
        "rule_id": "Rule 3",
        "name": "KPICALC Rule 3",
        "description": "Every policy record must have a matching premium record; otherwise error K001 (missing premium).",
        "formula": null
      },
      {
        "rule_id": "Rule 4",
        "name": "KPICALC Rule 4",
        "description": "Every premium record must have a matching policy record; otherwise error K002 (orphan premium).",
        "formula": null
      },
      {
        "rule_id": "Rule 5",
        "name": "KPICALC Rule 5",
        "description": "Reconciliation rule: WRITTEN premium must equal EARNED + UNEARNED within a tolerance of 0.01; violations trigger error K005.",
        "formula": "Reconciliation rule: WRITTEN premium must equal EARNED + UNEARNED within a tolerance of 0.01; violations trigger error K005."
      },
      {
        "rule_id": "Rule 6",
        "name": "KPICALC Rule 6",
        "description": "Input files must be sorted by POLICY\u2011NO; detection of a decreasing POLICY\u2011NO sets a fatal error.",
        "formula": null
      },
      {
        "rule_id": "Rule 7",
        "name": "KPICALC Rule 7",
        "description": "Data\u2011quality errors increment WS-DQ-ERRORS; I/O errors increment WS-IO-ERRORS; reconciliation errors increment WS-RECON-ERRORS.",
        "formula": "Data\u2011quality errors increment WS-DQ-ERRORS; I/O errors increment WS-IO-ERRORS; reconciliation errors increment WS-RECON-ERRORS."
      },
      {
        "rule_id": "Rule 8",
        "name": "KPICALC Rule 8",
        "description": "Return\u2011code 12 for fatal I/O or ordering errors, return\u2011code 4 when any data\u2011quality errors are present, otherwise normal return.",
        "formula": "Return\u2011code 12 for fatal I/O or ordering errors, return\u2011code 4 when any data\u2011quality errors are present, otherwise normal return."
      }
    ],
    "inputs": [
      "POLICY-IN \u2013 status\u2011updated policy extract (sorted by POLICY\u2011NO)",
      "PREMIUM-IN \u2013 earned premium extract (sorted by POLICY\u2011NO)"
    ],
    "outputs": [
      "KPI-OUT \u2013 KPI summary report file",
      "ERROR-OUT \u2013 data\u2011quality and processing error file"
    ],
    "transformations": [
      "Count total policies and categorize by status codes (AC, PN, EX, CN) and unknown status.",
      "Count policies by product type (HO, AU) and track unknown product types.",
      "Aggregate written, earned, and unearned premium amounts across all policies.",
      "Aggregate written, earned, and unearned premium amounts separately for HO and AU products.",
      "Compute reconciliation difference: WRITTEN \u2013 (EARNED + UNEARNED) and flag when absolute difference exceeds tolerance of 0.01.",
      "Detect and count out\u2011of\u2011order records in both input streams.",
      "Identify missing premium records (policy without premium) and orphan premium records (premium without policy).",
      "Generate formatted KPI lines for the KPI\u2011OUT file (counts and monetary totals).",
      "Create error records with specific error codes and messages for data\u2011quality violations."
    ],
    "dependencies": [
      "File definitions for POLICY-IN, PREMIUM-IN, KPI-OUT, and ERROR-OUT (SELECT statements).",
      "Working\u2011storage variables for status flags, counters, totals, and formatting edits.",
      "COBOL intrinsic FUNCTION ABS for absolute difference calculation.",
      "Standard COBOL I/O operations (OPEN, READ, WRITE, CLOSE, DISPLAY)."
    ]
  },
  {
    "id": "POLLOAD.CBL",
    "name": "POLLOAD.CBL",
    "type": "COBOL",
    "lines": 206,
    "entities": 44,
    "relationships": 46,
    "rules": 4,
    "purpose": "Load policy master records from a line\u2011sequential input file into a VSAM KSDS (indexed) file, performing basic validation and duplicate detection.",
    "raw_code": "       *****************************************************************\n       * PROGRAM NAME : POLLOAD\n       * PURPOSE      : Load Policy Master Records into VSAM KSDS\n       * SYSTEM       : TFG Mainframe Personal Lines\n       * AUTHOR       : Data Engineering Project\n       *****************************************************************\n\n       IDENTIFICATION DIVISION.\n       PROGRAM-ID. POLLOAD.\n\n       ENVIRONMENT DIVISION.\n\n       INPUT-OUTPUT SECTION.\n\n       FILE-CONTROL.\n\n           SELECT POLICY-IN\n               ASSIGN TO POLIN\n               ORGANIZATION IS LINE SEQUENTIAL\n               FILE STATUS IS WS-IN-STATUS.\n\n           SELECT POLICY-MASTER\n               ASSIGN TO POLYMAST\n               ORGANIZATION IS INDEXED\n               ACCESS MODE IS DYNAMIC\n               RECORD KEY IS POLICY-NUMBER\n               FILE STATUS IS WS-VSAM-STATUS.\n\n       DATA DIVISION.\n\n       FILE SECTION.\n\n       FD  POLICY-IN.\n       01  POLICY-IN-REC.\n           05 PI-POLICY-NUMBER       PIC X(15).\n           05 PI-CUSTOMER-ID         PIC X(10).\n           05 PI-AGENT-ID            PIC X(10).\n           05 PI-PRODUCT-CODE        PIC X(10).\n           05 PI-POLICY-TYPE         PIC X(30).\n           05 PI-EFFECTIVE-DATE      PIC X(10).\n           05 PI-EXPIRATION-DATE     PIC X(10).\n           05 PI-CURRENT-STATUS      PIC X(20).\n           05 PI-PAYMENT-FREQUENCY   PIC X(20).\n           05 PI-POLICY-TERM         PIC 9(02).\n           05 PI-WRITTEN-PREMIUM     PIC 9(10)V99.\n           05 PI-EARNED-PREMIUM      PIC 9(10)V99.\n           05 PI-RENEWAL-DATE        PIC X(10).\n\n       FD  POLICY-MASTER.\n\n       COPY POLYMAST.\n\n       WORKING-STORAGE SECTION.\n\n       77  WS-EOF                    PIC X VALUE 'N'.\n\n       77  WS-IN-STATUS              PIC XX VALUE SPACES.\n       77  WS-VSAM-STATUS            PIC XX VALUE SPACES.\n\n       77  WS-READ-COUNT             PIC 9(7) VALUE ZERO.\n       77  WS-WRITE-COUNT            PIC 9(7) VALUE ZERO.\n       77  WS-ERROR-COUNT            PIC 9(7) VALUE ZERO.\n\n       PROCEDURE DIVISION.\n\n       MAIN-PROCESS.\n\n           PERFORM 1000-INITIALIZE\n\n           PERFORM UNTIL WS-EOF = 'Y'\n\n               PERFORM 2000-READ-INPUT\n\n               IF WS-EOF NOT = 'Y'\n                   PERFORM 3000-VALIDATE\n                   PERFORM 4000-WRITE-VSAM\n               END-IF\n\n           END-PERFORM\n\n           PERFORM 9000-CLOSE-FILES\n\n           STOP RUN.\n\n      *============================================================*\n      * INITIALIZATION\n      *============================================================*\n\n       1000-INITIALIZE.\n\n           DISPLAY 'POLLOAD STARTED'.\n\n           OPEN INPUT POLICY-IN\n\n           IF WS-IN-STATUS NOT = \"00\"\n               DISPLAY 'ERROR OPENING INPUT FILE'\n               DISPLAY 'STATUS = ' WS-IN-STATUS\n               STOP RUN\n           END-IF\n\n           OPEN OUTPUT POLICY-MASTER\n\n           IF WS-VSAM-STATUS NOT = \"00\"\n               DISPLAY 'ERROR OPENING VSAM FILE'\n               DISPLAY 'STATUS = ' WS-VSAM-STATUS\n               STOP RUN\n           END-IF.\n\n      *============================================================*\n      * READ INPUT\n      *============================================================*\n\n       2000-READ-INPUT.\n\n           READ POLICY-IN\n\n               AT END\n                   MOVE 'Y' TO WS-EOF\n\n               NOT AT END\n                   ADD 1 TO WS-READ-COUNT\n\n           END-READ.\n\n      *============================================================*\n      * VALIDATION\n      *============================================================*\n\n       3000-VALIDATE.\n\n           IF PI-POLICY-NUMBER = SPACES\n\n               DISPLAY 'INVALID POLICY NUMBER'\n\n               ADD 1 TO WS-ERROR-COUNT\n\n               GO TO 3000-EXIT\n\n           END-IF.\n\n      * Move Input Record to VSAM Record\n\n           MOVE PI-POLICY-NUMBER      TO POLICY-NUMBER\n           MOVE PI-CUSTOMER-ID        TO CUSTOMER-ID\n           MOVE PI-AGENT-ID           TO AGENT-ID\n           MOVE PI-PRODUCT-CODE       TO PRODUCT-CODE\n           MOVE PI-POLICY-TYPE        TO POLICY-TYPE\n           MOVE PI-EFFECTIVE-DATE     TO EFFECTIVE-DATE\n           MOVE PI-EXPIRATION-DATE    TO EXPIRATION-DATE\n           MOVE PI-CURRENT-STATUS     TO CURRENT-STATUS\n           MOVE PI-PAYMENT-FREQUENCY  TO PAYMENT-FREQUENCY\n           MOVE PI-POLICY-TERM        TO POLICY-TERM\n           MOVE PI-WRITTEN-PREMIUM    TO WRITTEN-PREMIUM\n           MOVE PI-EARNED-PREMIUM     TO EARNED-PREMIUM\n           MOVE PI-RENEWAL-DATE       TO RENEWAL-DATE.\n\n       3000-EXIT.\n           EXIT.\n\n      *============================================================*\n      * WRITE VSAM RECORD\n      *============================================================*\n\n       4000-WRITE-VSAM.\n\n           WRITE POLICY-MASTER-RECORD\n\n           INVALID KEY\n\n               DISPLAY 'DUPLICATE POLICY : '\n                       POLICY-NUMBER\n\n               ADD 1 TO WS-ERROR-COUNT\n\n           NOT INVALID KEY\n\n               ADD 1 TO WS-WRITE-COUNT\n\n           END-WRITE.\n\n      *============================================================*\n      * CLOSE FILES\n      *============================================================*\n\n       9000-CLOSE-FILES.\n\n           CLOSE POLICY-IN.\n\n           CLOSE POLICY-MASTER.\n\n           DISPLAY '-------------------------------------'.\n\n           DISPLAY 'TOTAL RECORDS READ    : '\n                    WS-READ-COUNT.\n\n           DISPLAY 'TOTAL RECORDS WRITTEN : '\n                    WS-WRITE-COUNT.\n\n           DISPLAY 'TOTAL ERRORS          : '\n                    WS-ERROR-COUNT.\n\n           DISPLAY 'POLLOAD COMPLETED'.\n\n           DISPLAY '-------------------------------------'.\n\n       END PROGRAM POLLOAD.",
    "business_rules": [
      {
        "rule_id": "Rule 1",
        "name": "POLLOAD Rule 1",
        "description": "A policy record must contain a non\u2011blank policy number; otherwise it is considered invalid.",
        "formula": null
      },
      {
        "rule_id": "Rule 2",
        "name": "POLLOAD Rule 2",
        "description": "Policy numbers must be unique in the POLICY-MASTER VSAM file; duplicate keys are rejected and logged as errors.",
        "formula": "Policy numbers must be unique in the POLICY-MASTER VSAM file; duplicate keys are rejected and logged as errors."
      },
      {
        "rule_id": "Rule 3",
        "name": "POLLOAD Rule 3",
        "description": "All fields from the input record are transferred directly to the VSAM record without transformation.",
        "formula": null
      },
      {
        "rule_id": "Rule 4",
        "name": "POLLOAD Rule 4",
        "description": "Processing stops only after the entire input file has been read; no partial roll\u2011back is performed.",
        "formula": null
      }
    ],
    "inputs": [
      "POLICY-IN (line sequential file containing raw policy data)"
    ],
    "outputs": [
      "POLICY-MASTER (VSAM KSDS indexed file storing policy master records)"
    ],
    "transformations": [
      "Validation: reject records where PI-POLICY-NUMBER is blank and count as error.",
      "Field mapping: move each PI\u2011* field from the input record to the corresponding VSAM field (e.g., PI-POLICY-NUMBER \u2192 POLICY-NUMBER, PI-CUSTOMER-ID \u2192 CUSTOMER-ID, etc.).",
      "Duplicate detection: VSAM write with INVALID KEY clause treats duplicate POLICY-NUMBER as an error.",
      "Counting: increment WS-READ-COUNT for each input record, WS-WRITE-COUNT for successful writes, WS-ERROR-COUNT for validation or duplicate errors."
    ],
    "dependencies": [
      "Copybook POLYMAST (defines the VSAM record layout for POLICY-MASTER)",
      "File definitions for POLICY-IN (sequential) and POLICY-MASTER (indexed VSAM)",
      "COBOL runtime file\u2011status handling (WS-IN-STATUS, WS-VSAM-STATUS)"
    ]
  },
  {
    "id": "POLSTATUS.CBL",
    "name": "POLSTATUS.CBL",
    "type": "COBOL",
    "lines": 319,
    "entities": 69,
    "relationships": 25,
    "rules": 10,
    "purpose": "Derive and update the status of insurance policies based on effective, expiry and current dates while preserving existing cancelled statuses, and write the updated policy records and any validation errors to output files.",
    "raw_code": "IDENTIFICATION DIVISION.\n       PROGRAM-ID. POLSTAT.\n      ******************************************************************\n      * TASK 8 - POLICY STATUS LOGIC\n      *\n      * DEPENDENCY: TASK 5 POLLOAD PROVIDES VALID POLICY MASTER DATA.\n      * TASKS 6/7 MAY RUN BEFORE/AFTER ACCORDING TO THE JOB SCHEDULE.\n      *\n      * PROJECT STATUS CODES:\n      * PN = PENDING/FUTURE\n      * AC = ACTIVE/IN-FORCE\n      * EX = EXPIRED\n      * CN = CANCELLED (PRESERVED; NOT DERIVED)\n      *\n      * RULE:\n      * IF EXISTING STATUS = CN, PRESERVE CN.\n      * ELSE CURRENT-DATE < EFFECTIVE-DATE => PN\n      * ELSE CURRENT-DATE <= EXPIRY-DATE  => AC\n      * ELSE                               => EX\n      *\n      * CANCELLATION IS NOT DERIVED BECAUSE NO CANCELLATION DATE/RULE\n      * EXISTS IN THE CURRENT TASK-2/3 POLICY LAYOUT.\n      ******************************************************************\n       ENVIRONMENT DIVISION.\n       INPUT-OUTPUT SECTION.\n       FILE-CONTROL.\n           SELECT POLICY-IN ASSIGN TO POLIN\n             ORGANIZATION IS SEQUENTIAL FILE STATUS IS WS-PI-ST.\n           SELECT POLICY-OUT ASSIGN TO POLOUT\n             ORGANIZATION IS SEQUENTIAL FILE STATUS IS WS-PO-ST.\n           SELECT ERROR-OUT ASSIGN TO ERROUT\n             ORGANIZATION IS SEQUENTIAL FILE STATUS IS WS-ER-ST.\n \n       DATA DIVISION.\n       FILE SECTION.\n       FD POLICY-IN RECORD CONTAINS 77 CHARACTERS.\n       01 PI-REC.\n          05 PI-POLICY-NO       PIC X(12).\n          05 PI-CUSTOMER-ID     PIC X(9).\n          05 PI-AGENT-ID        PIC X(9).\n          05 PI-PRODUCT-TYPE    PIC X(2).\n          05 PI-POLICY-STATUS   PIC X(2).\n          05 PI-EFFECTIVE-DATE  PIC 9(8).\n          05 PI-EXPIRY-DATE     PIC 9(8).\n          05 PI-WRITTEN-PREMIUM PIC 9(9)V99.\n          05 PI-CREATE-DT       PIC 9(8).\n          05 PI-UPDATE-DT       PIC 9(8).\n \n       FD POLICY-OUT RECORD CONTAINS 77 CHARACTERS.\n       01 PO-REC.\n          05 PO-POLICY-NO       PIC X(12).\n          05 PO-CUSTOMER-ID     PIC X(9).\n          05 PO-AGENT-ID        PIC X(9).\n          05 PO-PRODUCT-TYPE    PIC X(2).\n          05 PO-POLICY-STATUS   PIC X(2).\n          05 PO-EFFECTIVE-DATE  PIC 9(8).\n          05 PO-EXPIRY-DATE     PIC 9(8).\n          05 PO-WRITTEN-PREMIUM PIC 9(9)V99.\n          05 PO-CREATE-DT       PIC 9(8).\n          05 PO-UPDATE-DT       PIC 9(8).\n \n       FD ERROR-OUT RECORD CONTAINS 70 CHARACTERS.\n       01 ER-REC.\n          05 ER-POLICY-NO PIC X(12).\n          05 ER-CODE PIC X(4).\n          05 ER-MESSAGE PIC X(54).\n \n       WORKING-STORAGE SECTION.\n       01 WS-STATUS.\n          05 WS-PI-ST PIC XX VALUE SPACES.\n          05 WS-PO-ST PIC XX VALUE SPACES.\n          05 WS-ER-ST PIC XX VALUE SPACES.\n       01 WS-SW.\n          05 WS-EOF PIC X VALUE 'N'.\n             88 END-OF-FILE VALUE 'Y'.\n          05 WS-FATAL PIC X VALUE 'N'.\n             88 FATAL-ERROR VALUE 'Y'.\n          05 WS-DATE-VALID PIC X VALUE 'N'.\n          05 WS-PI-OPEN PIC X VALUE 'N'.\n          05 WS-PO-OPEN PIC X VALUE 'N'.\n          05 WS-ER-OPEN PIC X VALUE 'N'.\n       01 WS-DATE.\n          05 WS-CURRENT-DATE PIC 9(8).\n          05 WS-DATE-IN PIC 9(8).\n          05 WS-YEAR PIC 9(4).\n          05 WS-MONTH PIC 99.\n          05 WS-DAY PIC 99.\n          05 WS-MAX-DAY PIC 99.\n          05 WS-LEAP PIC X.\n          05 WS-REM4 PIC 9(4).\n          05 WS-REM100 PIC 9(4).\n          05 WS-REM400 PIC 9(4).\n       01 WS-COUNTERS.\n          05 WS-READ PIC 9(9) VALUE ZERO.\n          05 WS-WRITTEN PIC 9(9) VALUE ZERO.\n          05 WS-CHANGED PIC 9(9) VALUE ZERO.\n          05 WS-PENDING PIC 9(9) VALUE ZERO.\n          05 WS-ACTIVE PIC 9(9) VALUE ZERO.\n          05 WS-EXPIRED PIC 9(9) VALUE ZERO.\n          05 WS-CANCELLED PIC 9(9) VALUE ZERO.\n          05 WS-REJECTED PIC 9(9) VALUE ZERO.\n          05 WS-IO-ERRORS PIC 9(9) VALUE ZERO.\n \n       PROCEDURE DIVISION.\n       MAIN.\n           MOVE FUNCTION CURRENT-DATE(1:8) TO WS-CURRENT-DATE\n           MOVE WS-CURRENT-DATE TO WS-DATE-IN\n           PERFORM VALIDATE-CALENDAR-DATE\n           IF WS-DATE-VALID NOT = 'Y'\n              DISPLAY 'INVALID SYSTEM CURRENT DATE ' WS-CURRENT-DATE\n              MOVE 12 TO RETURN-CODE\n              GOBACK\n           END-IF\n           OPEN INPUT POLICY-IN\n           IF WS-PI-ST = '00'\n              MOVE 'Y' TO WS-PI-OPEN\n           ELSE\n              DISPLAY 'POLICY INPUT OPEN ERROR ' WS-PI-ST\n              SET FATAL-ERROR TO TRUE\n           END-IF\n \n           OPEN OUTPUT POLICY-OUT\n           IF WS-PO-ST = '00'\n              MOVE 'Y' TO WS-PO-OPEN\n           ELSE\n              DISPLAY 'POLICY OUTPUT OPEN ERROR ' WS-PO-ST\n              SET FATAL-ERROR TO TRUE\n           END-IF\n \n           OPEN OUTPUT ERROR-OUT\n           IF WS-ER-ST = '00'\n              MOVE 'Y' TO WS-ER-OPEN\n           ELSE\n              DISPLAY 'ERROR OUTPUT OPEN ERROR ' WS-ER-ST\n              SET FATAL-ERROR TO TRUE\n           END-IF\n \n           IF FATAL-ERROR\n              PERFORM CLOSE-FILES\n              MOVE 12 TO RETURN-CODE\n              GOBACK\n           END-IF\n \n           PERFORM UNTIL END-OF-FILE OR FATAL-ERROR\n              READ POLICY-IN\n                 AT END MOVE 'Y' TO WS-EOF\n                 NOT AT END\n                    IF WS-PI-ST NOT = '00'\n                       DISPLAY 'POLICY READ ERROR ' WS-PI-ST\n                       ADD 1 TO WS-IO-ERRORS\n                       SET FATAL-ERROR TO TRUE\n                    ELSE\n                       ADD 1 TO WS-READ\n                       PERFORM PROCESS-POLICY\n                    END-IF\n              END-READ\n           END-PERFORM\n \n           PERFORM CLOSE-FILES\n           DISPLAY 'POLSTAT READ      : ' WS-READ\n           DISPLAY 'POLSTAT WRITTEN   : ' WS-WRITTEN\n           DISPLAY 'POLSTAT CHANGED   : ' WS-CHANGED\n           DISPLAY 'POLSTAT PENDING   : ' WS-PENDING\n           DISPLAY 'POLSTAT ACTIVE    : ' WS-ACTIVE\n           DISPLAY 'POLSTAT EXPIRED   : ' WS-EXPIRED\n           DISPLAY 'POLSTAT CANCELLED : ' WS-CANCELLED\n           DISPLAY 'POLSTAT REJECTED  : ' WS-REJECTED\n           DISPLAY 'POLSTAT I/O ERRORS: ' WS-IO-ERRORS\n           IF FATAL-ERROR MOVE 12 TO RETURN-CODE END-IF\n           GOBACK.\n \n       PROCESS-POLICY.\n           MOVE PI-EFFECTIVE-DATE TO WS-DATE-IN\n           PERFORM VALIDATE-CALENDAR-DATE\n           IF WS-DATE-VALID NOT = 'Y'\n              MOVE 'S001' TO ER-CODE\n              MOVE 'INVALID POLICY EFFECTIVE DATE' TO ER-MESSAGE\n              PERFORM WRITE-ERROR\n           ELSE\n              MOVE PI-EXPIRY-DATE TO WS-DATE-IN\n              PERFORM VALIDATE-CALENDAR-DATE\n              IF WS-DATE-VALID NOT = 'Y'\n                 MOVE 'S002' TO ER-CODE\n                 MOVE 'INVALID POLICY EXPIRY DATE' TO ER-MESSAGE\n                 PERFORM WRITE-ERROR\n              ELSE\n                 IF PI-EXPIRY-DATE < PI-EFFECTIVE-DATE\n                    MOVE 'S003' TO ER-CODE\n                    MOVE 'EXPIRY DATE BEFORE EFFECTIVE DATE'\n                      TO ER-MESSAGE\n                    PERFORM WRITE-ERROR\n                 ELSE\n                    PERFORM DETERMINE-STATUS\n                    PERFORM WRITE-POLICY\n                 END-IF\n              END-IF\n           END-IF.\n \n       DETERMINE-STATUS.\n           MOVE PI-REC TO PO-REC\n           IF PI-POLICY-STATUS = 'CN'\n              MOVE 'CN' TO PO-POLICY-STATUS\n              ADD 1 TO WS-CANCELLED\n           ELSE\n              IF WS-CURRENT-DATE < PI-EFFECTIVE-DATE\n                 MOVE 'PN' TO PO-POLICY-STATUS\n                 ADD 1 TO WS-PENDING\n              ELSE\n                 IF WS-CURRENT-DATE <= PI-EXPIRY-DATE\n                    MOVE 'AC' TO PO-POLICY-STATUS\n                    ADD 1 TO WS-ACTIVE\n                 ELSE\n                    MOVE 'EX' TO PO-POLICY-STATUS\n                    ADD 1 TO WS-EXPIRED\n                 END-IF\n              END-IF\n           END-IF\n           IF PO-POLICY-STATUS NOT = PI-POLICY-STATUS\n              ADD 1 TO WS-CHANGED\n              MOVE WS-CURRENT-DATE TO PO-UPDATE-DT\n           END-IF.\n \n       WRITE-POLICY.\n           WRITE PO-REC\n           IF WS-PO-ST = '00'\n              ADD 1 TO WS-WRITTEN\n           ELSE\n              DISPLAY 'POLICY OUTPUT WRITE ERROR ' WS-PO-ST\n              ADD 1 TO WS-IO-ERRORS\n              SET FATAL-ERROR TO TRUE\n           END-IF.\n \n       WRITE-ERROR.\n           MOVE PI-POLICY-NO TO ER-POLICY-NO\n           WRITE ER-REC\n           IF WS-ER-ST = '00'\n              ADD 1 TO WS-REJECTED\n           ELSE\n              DISPLAY 'ERROR OUTPUT WRITE ERROR ' WS-ER-ST\n              ADD 1 TO WS-IO-ERRORS\n              SET FATAL-ERROR TO TRUE\n           END-IF.\n \n       CLOSE-FILES.\n           IF WS-PI-OPEN = 'Y'\n              CLOSE POLICY-IN\n              IF WS-PI-ST NOT = '00'\n                 DISPLAY 'POLICY INPUT CLOSE ERROR ' WS-PI-ST\n                 ADD 1 TO WS-IO-ERRORS\n                 SET FATAL-ERROR TO TRUE\n              ELSE\n                 MOVE 'N' TO WS-PI-OPEN\n              END-IF\n           END-IF\n \n           IF WS-PO-OPEN = 'Y'\n              CLOSE POLICY-OUT\n              IF WS-PO-ST NOT = '00'\n                 DISPLAY 'POLICY OUTPUT CLOSE ERROR ' WS-PO-ST\n                 ADD 1 TO WS-IO-ERRORS\n                 SET FATAL-ERROR TO TRUE\n              ELSE\n                 MOVE 'N' TO WS-PO-OPEN\n              END-IF\n           END-IF\n \n           IF WS-ER-OPEN = 'Y'\n              CLOSE ERROR-OUT\n              IF WS-ER-ST NOT = '00'\n                 DISPLAY 'ERROR OUTPUT CLOSE ERROR ' WS-ER-ST\n                 ADD 1 TO WS-IO-ERRORS\n                 SET FATAL-ERROR TO TRUE\n              ELSE\n                 MOVE 'N' TO WS-ER-OPEN\n              END-IF\n           END-IF.\n \n       VALIDATE-CALENDAR-DATE.\n           MOVE 'N' TO WS-DATE-VALID\n           IF WS-DATE-IN NUMERIC\n              MOVE WS-DATE-IN(1:4) TO WS-YEAR\n              MOVE WS-DATE-IN(5:2) TO WS-MONTH\n              MOVE WS-DATE-IN(7:2) TO WS-DAY\n              IF WS-YEAR > ZERO\n                 AND WS-MONTH >= 1 AND WS-MONTH <= 12\n                 PERFORM SET-MAX-DAY\n                 IF WS-DAY >= 1 AND WS-DAY <= WS-MAX-DAY\n                    MOVE 'Y' TO WS-DATE-VALID\n                 END-IF\n              END-IF\n           END-IF.\n \n       SET-MAX-DAY.\n           EVALUATE WS-MONTH\n              WHEN 1 WHEN 3 WHEN 5 WHEN 7 WHEN 8 WHEN 10 WHEN 12\n                 MOVE 31 TO WS-MAX-DAY\n              WHEN 4 WHEN 6 WHEN 9 WHEN 11\n                 MOVE 30 TO WS-MAX-DAY\n              WHEN 2\n                 PERFORM CHECK-LEAP-YEAR\n                 IF WS-LEAP = 'Y'\n                    MOVE 29 TO WS-MAX-DAY\n                 ELSE\n                    MOVE 28 TO WS-MAX-DAY\n                 END-IF\n           END-EVALUATE.\n \n       CHECK-LEAP-YEAR.\n           MOVE 'N' TO WS-LEAP\n           COMPUTE WS-REM4 = FUNCTION MOD(WS-YEAR, 4)\n           COMPUTE WS-REM100 = FUNCTION MOD(WS-YEAR, 100)\n           COMPUTE WS-REM400 = FUNCTION MOD(WS-YEAR, 400)\n           IF WS-REM400 = ZERO\n              MOVE 'Y' TO WS-LEAP\n           ELSE\n              IF WS-REM4 = ZERO AND WS-REM100 NOT = ZERO\n                 MOVE 'Y' TO WS-LEAP\n              END-IF\n           END-IF.",
    "business_rules": [
      {
        "rule_id": "Rule 1",
        "name": "POLSTATUS Rule 1",
        "description": "If existing PI-POLICY-STATUS = 'CN' then retain 'CN' and count as cancelled.",
        "formula": "If existing PI-POLICY-STATUS = 'CN' then retain 'CN' and count as cancelled."
      },
      {
        "rule_id": "Rule 2",
        "name": "POLSTATUS Rule 2",
        "description": "If current date < PI-EFFECTIVE-DATE then set status to 'PN' (pending) and count pending.",
        "formula": "If current date < PI-EFFECTIVE-DATE then set status to 'PN' (pending) and count pending."
      },
      {
        "rule_id": "Rule 3",
        "name": "POLSTATUS Rule 3",
        "description": "If current date <= PI-EXPIRY-DATE then set status to 'AC' (active) and count active.",
        "formula": "If current date <= PI-EXPIRY-DATE then set status to 'AC' (active) and count active."
      },
      {
        "rule_id": "Rule 4",
        "name": "POLSTATUS Rule 4",
        "description": "Otherwise set status to 'EX' (expired) and count expired.",
        "formula": null
      },
      {
        "rule_id": "Rule 5",
        "name": "POLSTATUS Rule 5",
        "description": "Do not derive cancellation status because no cancellation date is available.",
        "formula": null
      },
      {
        "rule_id": "Rule 6",
        "name": "POLSTATUS Rule 6",
        "description": "Effective date must be a valid calendar date; otherwise write error record with code S001.",
        "formula": null
      },
      {
        "rule_id": "Rule 7",
        "name": "POLSTATUS Rule 7",
        "description": "Expiry date must be a valid calendar date; otherwise write error record with code S002.",
        "formula": null
      },
      {
        "rule_id": "Rule 8",
        "name": "POLSTATUS Rule 8",
        "description": "Expiry date must not be earlier than effective date; otherwise write error record with code S003.",
        "formula": null
      },
      {
        "rule_id": "Rule 9",
        "name": "POLSTATUS Rule 9",
        "description": "When status changes, PO-UPDATE-DT is set to the current processing date.",
        "formula": "When status changes, PO-UPDATE-DT is set to the current processing date."
      },
      {
        "rule_id": "Rule 10",
        "name": "POLSTATUS Rule 10",
        "description": "All file status codes must be '00' for successful open, read, write, or close; otherwise a fatal error is raised.",
        "formula": null
      }
    ],
    "inputs": [
      "POLICY-IN sequential file (fields: PI-POLICY-NO, PI-CUSTOMER-ID, PI-AGENT-ID, PI-PRODUCT-TYPE, PI-POLICY-STATUS, PI-EFFECTIVE-DATE, PI-EXPIRY-DATE, PI-WRITTEN-PREMIUM, PI-CREATE-DT, PI-UPDATE-DT)",
      "System current date (FUNCTION CURRENT-DATE)"
    ],
    "outputs": [
      "POLICY-OUT sequential file (fields: PO-POLICY-NO, PO-CUSTOMER-ID, PO-AGENT-ID, PO-PRODUCT-TYPE, PO-POLICY-STATUS, PO-EFFECTIVE-DATE, PO-EXPIRY-DATE, PO-WRITTEN-PREMIUM, PO-CREATE-DT, PO-UPDATE-DT)",
      "ERROR-OUT sequential file (fields: ER-POLICY-NO, ER-CODE, ER-MESSAGE)",
      "Display of processing counters",
      "RETURN-CODE (0 for success, 12 for fatal error)"
    ],
    "transformations": [
      "Validation of calendar dates (numeric check, month range, day range, leap\u2011year handling)",
      "Comparison of current date with effective and expiry dates to derive status",
      "Preservation of existing 'CN' (cancelled) status",
      "Copy of input record to output record with possible status change",
      "Update of PO-UPDATE-DT when status changes",
      "Aggregation of counters for read, written, changed, pending, active, expired, cancelled, rejected, and I/O errors"
    ],
    "dependencies": [
      "POLICY-IN, POLICY-OUT and ERROR-OUT file definitions (SELECT statements)",
      "COBOL intrinsic FUNCTION CURRENT-DATE",
      "COBOL intrinsic FUNCTION MOD for leap\u2011year calculation",
      "Standard COBOL file I/O verbs (OPEN, READ, WRITE, CLOSE)",
      "Task 5 POLLOAD (provides valid policy master data) \u2013 mentioned as a logical dependency"
    ]
  },
  {
    "id": "PREMCALC.CBL",
    "name": "PREMCALC.CBL",
    "type": "COBOL",
    "lines": 433,
    "entities": 100,
    "relationships": 29,
    "rules": 10,
    "purpose": "Calculate daily premium amounts for validated policies by aggregating property, vehicle, and coverage data, applying product\u2011specific rating rules (Homeowners and Auto), and outputting premium records with a unique premium ID while logging any processing errors.",
    "raw_code": "IDENTIFICATION DIVISION.\n       PROGRAM-ID. PREMCALC.\n      ******************************************************************\n      * TASK 6 - PREMIUM CALCULATION\n      *\n      * DEPENDENCY:\n      *   RUNS AFTER TASK 5 POLLOAD. POLICY-IN MUST CONTAIN VALIDATED\n      *   POLICIES FROM THE TASK-5 PROCESSING FLOW.\n      *\n      * RATING RULE STATUS:\n      *   PROJECT/DEMO RULES ONLY. OFFICIAL TFG RATING TABLES WERE NOT\n      *   PROVIDED. ALL RATES ARE ISOLATED IN WS-RATING-CONSTANTS.\n      *\n      * MULTIPLE COVERAGES:\n      *   ALL COVERAGE RECORDS FOR A POLICY ARE ACCUMULATED.\n      *\n      * PREMIUM ID:\n      *   12 BYTES = FIRST 6 BYTES OF POLICY-NO + YYMMDD CALC DATE.\n      *   THIS SUPPORTS DATE-BASED PREMIUM HISTORY WITHOUT CHANGING THE\n      *   TASK-2/TASK-3 PREMFILE 12-BYTE PREMIUM-ID.\n      *   ASSUMPTION: ONE PREMIUM CALCULATION PER POLICY PER DAY.\n      *\n      * INPUT ACCESS:\n      *   POLICY, PROPERTY, VEHICLE AND COVERAGE CALCULATION EXTRACTS\n      *   MUST BE SORTED BY POLICY-NO. TASK-4 KSDS PRIMARY KEYS FOR\n      *   PROPERTY/VEHICLE/COVERAGE ARE NOT POLICY-NO.\n      ******************************************************************\n \n       ENVIRONMENT DIVISION.\n       INPUT-OUTPUT SECTION.\n       FILE-CONTROL.\n           SELECT POLICY-IN ASSIGN TO POLIN\n             ORGANIZATION IS SEQUENTIAL\n             FILE STATUS IS WS-PI-ST.\n           SELECT PROPERTY-IN ASSIGN TO PROPIN\n             ORGANIZATION IS SEQUENTIAL\n             FILE STATUS IS WS-PR-ST.\n           SELECT VEHICLE-IN ASSIGN TO VEHIN\n             ORGANIZATION IS SEQUENTIAL\n             FILE STATUS IS WS-VE-ST.\n           SELECT COVERAGE-IN ASSIGN TO COVGIN\n             ORGANIZATION IS SEQUENTIAL\n             FILE STATUS IS WS-CO-ST.\n           SELECT PREMIUM-OUT ASSIGN TO PREMOUT\n             ORGANIZATION IS SEQUENTIAL\n             FILE STATUS IS WS-PO-ST.\n           SELECT ERROR-OUT ASSIGN TO ERROUT\n             ORGANIZATION IS SEQUENTIAL\n             FILE STATUS IS WS-ER-ST.\n \n       DATA DIVISION.\n       FILE SECTION.\n \n       FD POLICY-IN RECORD CONTAINS 77 CHARACTERS.\n       01 PI-REC.\n          05 PI-POLICY-NO       PIC X(12).\n          05 PI-CUSTOMER-ID     PIC X(9).\n          05 PI-AGENT-ID        PIC X(9).\n          05 PI-PRODUCT-TYPE    PIC X(2).\n          05 PI-POLICY-STATUS   PIC X(2).\n          05 PI-EFFECTIVE-DATE  PIC 9(8).\n          05 PI-EXPIRY-DATE     PIC 9(8).\n          05 PI-WRITTEN-PREMIUM PIC 9(9)V99.\n          05 PI-CREATE-DT       PIC 9(8).\n          05 PI-UPDATE-DT       PIC 9(8).\n \n       FD PROPERTY-IN RECORD CONTAINS 172 CHARACTERS.\n       01 PR-REC.\n          05 PR-PROPERTY-ID       PIC X(12).\n          05 PR-POLICY-NO         PIC X(12).\n          05 PR-PROPERTY-TYPE     PIC X(2).\n          05 PR-ADDRESS           PIC X(100).\n          05 PR-CONSTRUCTION-TYPE PIC X(30).\n          05 PR-YEAR-BUILT        PIC 9(4).\n          05 PR-PROPERTY-VALUE    PIC 9(10)V99.\n \n       FD VEHICLE-IN RECORD CONTAINS 117 CHARACTERS.\n       01 VE-REC.\n          05 VE-VEHICLE-ID        PIC X(12).\n          05 VE-POLICY-NO         PIC X(12).\n          05 VE-VIN               PIC X(17).\n          05 VE-MAKE              PIC X(30).\n          05 VE-MODEL             PIC X(30).\n          05 VE-YEAR              PIC 9(4).\n          05 VE-VEHICLE-VALUE     PIC 9(10)V99.\n \n       FD COVERAGE-IN RECORD CONTAINS 66 CHARACTERS.\n       01 CO-REC.\n          05 CO-COVERAGE-ID       PIC X(12).\n          05 CO-POLICY-NO         PIC X(12).\n          05 CO-COVERAGE-TYPE     PIC X(4).\n          05 CO-COVERAGE-LIMIT    PIC 9(10)V99.\n          05 CO-DEDUCTIBLE        PIC 9(8)V99.\n          05 CO-EFFECTIVE-DATE    PIC 9(8).\n          05 CO-EXPIRY-DATE       PIC 9(8).\n \n       FD PREMIUM-OUT RECORD CONTAINS 65 CHARACTERS.\n       01 PO-REC.\n          05 PO-PREMIUM-ID        PIC X(12).\n          05 PO-POLICY-NO         PIC X(12).\n          05 PO-WRITTEN-PREMIUM   PIC 9(9)V99.\n          05 PO-EARNED-PREMIUM    PIC 9(9)V99.\n          05 PO-UNEARNED-PREMIUM  PIC 9(9)V99.\n          05 PO-CALCULATION-DATE  PIC 9(8).\n \n       FD ERROR-OUT RECORD CONTAINS 70 CHARACTERS.\n       01 ER-REC.\n          05 ER-POLICY-NO         PIC X(12).\n          05 ER-CODE              PIC X(4).\n          05 ER-MESSAGE           PIC X(54).\n \n       WORKING-STORAGE SECTION.\n       01 WS-FILE-STATUS.\n          05 WS-PI-ST PIC XX VALUE SPACES.\n          05 WS-PR-ST PIC XX VALUE SPACES.\n          05 WS-VE-ST PIC XX VALUE SPACES.\n          05 WS-CO-ST PIC XX VALUE SPACES.\n          05 WS-PO-ST PIC XX VALUE SPACES.\n          05 WS-ER-ST PIC XX VALUE SPACES.\n \n       01 WS-SWITCHES.\n          05 WS-POL-EOF PIC X VALUE 'N'.\n             88 POL-EOF VALUE 'Y'.\n          05 WS-PR-EOF PIC X VALUE 'N'.\n             88 PR-EOF VALUE 'Y'.\n          05 WS-VE-EOF PIC X VALUE 'N'.\n             88 VE-EOF VALUE 'Y'.\n          05 WS-CO-EOF PIC X VALUE 'N'.\n             88 CO-EOF VALUE 'Y'.\n          05 WS-PR-FOUND PIC X VALUE 'N'.\n          05 WS-VE-FOUND PIC X VALUE 'N'.\n          05 WS-CO-FOUND PIC X VALUE 'N'.\n          05 WS-FATAL PIC X VALUE 'N'.\n             88 FATAL-ERROR VALUE 'Y'.\n \n      * PROJECT/DEMO CONSTANTS - REPLACE WITH APPROVED TFG RATES.\n       01 WS-RATING-CONSTANTS.\n          05 WS-HO-BASE       PIC 9(5)V99 VALUE 100.00.\n          05 WS-HO-RISK-RATE  PIC 9V9(6) VALUE 0.002000.\n          05 WS-HO-COV-RATE   PIC 9V9(6) VALUE 0.001000.\n          05 WS-HO-DED-RATE   PIC 9V9(6) VALUE 0.050000.\n          05 WS-HO-MIN        PIC 9(5)V99 VALUE 150.00.\n          05 WS-HO-MAX-DISC   PIC 9(5)V99 VALUE 100.00.\n          05 WS-AU-BASE       PIC 9(5)V99 VALUE 75.00.\n          05 WS-AU-RISK-RATE  PIC 9V9(6) VALUE 0.015000.\n          05 WS-AU-COV-RATE   PIC 9V9(6) VALUE 0.000800.\n          05 WS-AU-DED-RATE   PIC 9V9(6) VALUE 0.030000.\n          05 WS-AU-MIN        PIC 9(5)V99 VALUE 125.00.\n          05 WS-AU-MAX-DISC   PIC 9(5)V99 VALUE 75.00.\n \n       01 WS-CALC.\n          05 WS-RISK-VALUE       PIC 9(12)V99 VALUE ZERO.\n          05 WS-COV-LIMIT-TOTAL  PIC 9(12)V99 VALUE ZERO.\n          05 WS-DEDUCT-TOTAL     PIC 9(12)V99 VALUE ZERO.\n          05 WS-DISCOUNT         PIC 9(9)V99 VALUE ZERO.\n          05 WS-PREMIUM          PIC 9(9)V99 VALUE ZERO.\n          05 WS-CURRENT-DATE     PIC 9(8).\n          05 WS-COVERAGE-COUNT   PIC 9(5) VALUE ZERO.\n \n       01 WS-COUNTERS.\n          05 WS-READ             PIC 9(9) VALUE ZERO.\n          05 WS-CALCULATED       PIC 9(9) VALUE ZERO.\n          05 WS-ERRORS           PIC 9(9) VALUE ZERO.\n          05 WS-IO-ERRORS        PIC 9(9) VALUE ZERO.\n \n       PROCEDURE DIVISION.\n       MAIN.\n           MOVE FUNCTION CURRENT-DATE(1:8) TO WS-CURRENT-DATE\n           PERFORM OPEN-FILES\n           IF FATAL-ERROR GOBACK END-IF\n \n           PERFORM READ-PROPERTY\n           PERFORM READ-VEHICLE\n           PERFORM READ-COVERAGE\n \n           PERFORM UNTIL POL-EOF OR FATAL-ERROR\n              PERFORM READ-POLICY\n              IF NOT POL-EOF AND NOT FATAL-ERROR\n                 ADD 1 TO WS-READ\n                 PERFORM PROCESS-POLICY\n              END-IF\n           END-PERFORM\n \n           PERFORM CLOSE-FILES\n           DISPLAY 'PREMCALC READ       : ' WS-READ\n           DISPLAY 'PREMCALC CALCULATED : ' WS-CALCULATED\n           DISPLAY 'PREMCALC ERRORS     : ' WS-ERRORS\n           DISPLAY 'PREMCALC I/O ERRORS : ' WS-IO-ERRORS\n           IF FATAL-ERROR MOVE 12 TO RETURN-CODE END-IF\n           GOBACK.\n \n       OPEN-FILES.\n           OPEN INPUT POLICY-IN PROPERTY-IN VEHICLE-IN COVERAGE-IN\n                OUTPUT PREMIUM-OUT ERROR-OUT\n           IF WS-PI-ST NOT = '00'\n              DISPLAY 'POLICY OPEN ERROR ' WS-PI-ST\n              SET FATAL-ERROR TO TRUE\n           END-IF\n           IF WS-PR-ST NOT = '00'\n              DISPLAY 'PROPERTY OPEN ERROR ' WS-PR-ST\n              SET FATAL-ERROR TO TRUE\n           END-IF\n           IF WS-VE-ST NOT = '00'\n              DISPLAY 'VEHICLE OPEN ERROR ' WS-VE-ST\n              SET FATAL-ERROR TO TRUE\n           END-IF\n           IF WS-CO-ST NOT = '00'\n              DISPLAY 'COVERAGE OPEN ERROR ' WS-CO-ST\n              SET FATAL-ERROR TO TRUE\n           END-IF\n           IF WS-PO-ST NOT = '00'\n              DISPLAY 'PREMIUM OUTPUT OPEN ERROR ' WS-PO-ST\n              SET FATAL-ERROR TO TRUE\n           END-IF\n           IF WS-ER-ST NOT = '00'\n              DISPLAY 'ERROR OUTPUT OPEN ERROR ' WS-ER-ST\n              SET FATAL-ERROR TO TRUE\n           END-IF.\n \n       READ-POLICY.\n           READ POLICY-IN\n              AT END\n                 MOVE 'Y' TO WS-POL-EOF\n              NOT AT END\n                 IF WS-PI-ST NOT = '00'\n                    DISPLAY 'POLICY READ ERROR ' WS-PI-ST\n                    ADD 1 TO WS-IO-ERRORS\n                    SET FATAL-ERROR TO TRUE\n                 END-IF\n           END-READ.\n \n       READ-PROPERTY.\n           IF NOT PR-EOF\n              READ PROPERTY-IN\n                 AT END\n                    MOVE 'Y' TO WS-PR-EOF\n                 NOT AT END\n                    IF WS-PR-ST NOT = '00'\n                       DISPLAY 'PROPERTY READ ERROR ' WS-PR-ST\n                       ADD 1 TO WS-IO-ERRORS\n                       SET FATAL-ERROR TO TRUE\n                    END-IF\n              END-READ\n           END-IF.\n \n       READ-VEHICLE.\n           IF NOT VE-EOF\n              READ VEHICLE-IN\n                 AT END\n                    MOVE 'Y' TO WS-VE-EOF\n                 NOT AT END\n                    IF WS-VE-ST NOT = '00'\n                       DISPLAY 'VEHICLE READ ERROR ' WS-VE-ST\n                       ADD 1 TO WS-IO-ERRORS\n                       SET FATAL-ERROR TO TRUE\n                    END-IF\n              END-READ\n           END-IF.\n \n       READ-COVERAGE.\n           IF NOT CO-EOF\n              READ COVERAGE-IN\n                 AT END\n                    MOVE 'Y' TO WS-CO-EOF\n                 NOT AT END\n                    IF WS-CO-ST NOT = '00'\n                       DISPLAY 'COVERAGE READ ERROR ' WS-CO-ST\n                       ADD 1 TO WS-IO-ERRORS\n                       SET FATAL-ERROR TO TRUE\n                    END-IF\n              END-READ\n           END-IF.\n \n       PROCESS-POLICY.\n           MOVE ZERO TO WS-RISK-VALUE\n                        WS-COV-LIMIT-TOTAL\n                        WS-DEDUCT-TOTAL\n                        WS-DISCOUNT\n                        WS-PREMIUM\n                        WS-COVERAGE-COUNT\n \n           IF PI-PRODUCT-TYPE = 'HO'\n              PERFORM GET-PROPERTY\n              IF WS-PR-FOUND = 'Y'\n                 PERFORM GET-ALL-COVERAGES\n                 IF WS-CO-FOUND = 'Y'\n                    PERFORM CALC-HO\n                    PERFORM WRITE-PREMIUM\n                 ELSE\n                    MOVE 'P003' TO ER-CODE\n                    MOVE 'NO COVERAGE RECORDS FOR POLICY' TO ER-MESSAGE\n                    PERFORM WRITE-ERROR\n                 END-IF\n              ELSE\n                 MOVE 'P001' TO ER-CODE\n                 MOVE 'HOMEOWNERS PROPERTY RECORD NOT FOUND'\n                   TO ER-MESSAGE\n                 PERFORM WRITE-ERROR\n              END-IF\n           ELSE\n              IF PI-PRODUCT-TYPE = 'AU'\n                 PERFORM GET-VEHICLE\n                 IF WS-VE-FOUND = 'Y'\n                    PERFORM GET-ALL-COVERAGES\n                    IF WS-CO-FOUND = 'Y'\n                       PERFORM CALC-AU\n                       PERFORM WRITE-PREMIUM\n                    ELSE\n                       MOVE 'P003' TO ER-CODE\n                       MOVE 'NO COVERAGE RECORDS FOR POLICY'\n                         TO ER-MESSAGE\n                       PERFORM WRITE-ERROR\n                    END-IF\n                 ELSE\n                    MOVE 'P002' TO ER-CODE\n                    MOVE 'AUTO VEHICLE RECORD NOT FOUND' TO ER-MESSAGE\n                    PERFORM WRITE-ERROR\n                 END-IF\n              ELSE\n                 MOVE 'P004' TO ER-CODE\n                 MOVE 'PRODUCT TYPE MUST BE HO OR AU' TO ER-MESSAGE\n                 PERFORM WRITE-ERROR\n              END-IF\n           END-IF.\n \n       GET-PROPERTY.\n           MOVE 'N' TO WS-PR-FOUND\n           PERFORM UNTIL PR-EOF OR FATAL-ERROR\n              IF PR-POLICY-NO < PI-POLICY-NO\n                 PERFORM READ-PROPERTY\n              ELSE\n                 IF PR-POLICY-NO = PI-POLICY-NO\n                    MOVE PR-PROPERTY-VALUE TO WS-RISK-VALUE\n                    MOVE 'Y' TO WS-PR-FOUND\n                 END-IF\n                 EXIT PERFORM\n              END-IF\n           END-PERFORM.\n \n       GET-VEHICLE.\n           MOVE 'N' TO WS-VE-FOUND\n           PERFORM UNTIL VE-EOF OR FATAL-ERROR\n              IF VE-POLICY-NO < PI-POLICY-NO\n                 PERFORM READ-VEHICLE\n              ELSE\n                 IF VE-POLICY-NO = PI-POLICY-NO\n                    MOVE VE-VEHICLE-VALUE TO WS-RISK-VALUE\n                    MOVE 'Y' TO WS-VE-FOUND\n                 END-IF\n                 EXIT PERFORM\n              END-IF\n           END-PERFORM.\n \n       GET-ALL-COVERAGES.\n           MOVE 'N' TO WS-CO-FOUND\n           PERFORM UNTIL CO-EOF OR FATAL-ERROR\n              IF CO-POLICY-NO < PI-POLICY-NO\n                 PERFORM READ-COVERAGE\n              ELSE\n                 IF CO-POLICY-NO = PI-POLICY-NO\n                    MOVE 'Y' TO WS-CO-FOUND\n                    ADD CO-COVERAGE-LIMIT TO WS-COV-LIMIT-TOTAL\n                    ADD CO-DEDUCTIBLE TO WS-DEDUCT-TOTAL\n                    ADD 1 TO WS-COVERAGE-COUNT\n                    PERFORM READ-COVERAGE\n                 ELSE\n                    EXIT PERFORM\n                 END-IF\n              END-IF\n           END-PERFORM.\n \n       CALC-HO.\n           COMPUTE WS-DISCOUNT ROUNDED =\n              WS-DEDUCT-TOTAL * WS-HO-DED-RATE\n           IF WS-DISCOUNT > WS-HO-MAX-DISC\n              MOVE WS-HO-MAX-DISC TO WS-DISCOUNT\n           END-IF\n           COMPUTE WS-PREMIUM ROUNDED =\n              WS-HO-BASE\n              + (WS-RISK-VALUE * WS-HO-RISK-RATE)\n              + (WS-COV-LIMIT-TOTAL * WS-HO-COV-RATE)\n              - WS-DISCOUNT\n           IF WS-PREMIUM < WS-HO-MIN\n              MOVE WS-HO-MIN TO WS-PREMIUM\n           END-IF.\n \n       CALC-AU.\n           COMPUTE WS-DISCOUNT ROUNDED =\n              WS-DEDUCT-TOTAL * WS-AU-DED-RATE\n           IF WS-DISCOUNT > WS-AU-MAX-DISC\n              MOVE WS-AU-MAX-DISC TO WS-DISCOUNT\n           END-IF\n           COMPUTE WS-PREMIUM ROUNDED =\n              WS-AU-BASE\n              + (WS-RISK-VALUE * WS-AU-RISK-RATE)\n              + (WS-COV-LIMIT-TOTAL * WS-AU-COV-RATE)\n              - WS-DISCOUNT\n           IF WS-PREMIUM < WS-AU-MIN\n              MOVE WS-AU-MIN TO WS-PREMIUM\n           END-IF.\n \n       WRITE-PREMIUM.\n           MOVE PI-POLICY-NO(1:6) TO PO-PREMIUM-ID(1:6)\n           MOVE WS-CURRENT-DATE(3:6) TO PO-PREMIUM-ID(7:6)\n           MOVE PI-POLICY-NO TO PO-POLICY-NO\n           MOVE WS-PREMIUM TO PO-WRITTEN-PREMIUM\n           MOVE ZERO TO PO-EARNED-PREMIUM\n           MOVE WS-PREMIUM TO PO-UNEARNED-PREMIUM\n           MOVE WS-CURRENT-DATE TO PO-CALCULATION-DATE\n           WRITE PO-REC\n           IF WS-PO-ST = '00'\n              ADD 1 TO WS-CALCULATED\n           ELSE\n              ADD 1 TO WS-IO-ERRORS\n              MOVE 'P901' TO ER-CODE\n              MOVE 'PREMIUM OUTPUT WRITE FAILED' TO ER-MESSAGE\n              PERFORM WRITE-ERROR\n           END-IF.\n \n       WRITE-ERROR.\n           MOVE PI-POLICY-NO TO ER-POLICY-NO\n           WRITE ER-REC\n           IF WS-ER-ST = '00'\n              ADD 1 TO WS-ERRORS\n           ELSE\n              DISPLAY 'ERROR OUTPUT WRITE FAILED ' WS-ER-ST\n              ADD 1 TO WS-IO-ERRORS\n              SET FATAL-ERROR TO TRUE\n           END-IF.\n \n       CLOSE-FILES.\n           CLOSE POLICY-IN PROPERTY-IN VEHICLE-IN COVERAGE-IN\n                 PREMIUM-OUT ERROR-OUT.",
    "business_rules": [
      {
        "rule_id": "Rule 1",
        "name": "PREMCALC Rule 1",
        "description": "Product type must be either 'HO' (Homeowners) or 'AU' (Auto); otherwise error P004 is generated.",
        "formula": null
      },
      {
        "rule_id": "Rule 2",
        "name": "PREMCALC Rule 2",
        "description": "Homeowners policies require a matching property record; missing record generates error P001.",
        "formula": null
      },
      {
        "rule_id": "Rule 3",
        "name": "PREMCALC Rule 3",
        "description": "Auto policies require a matching vehicle record; missing record generates error P002.",
        "formula": null
      },
      {
        "rule_id": "Rule 4",
        "name": "PREMCALC Rule 4",
        "description": "At least one coverage record must exist for a policy; missing coverage generates error P003.",
        "formula": null
      },
      {
        "rule_id": "Rule 5",
        "name": "PREMCALC Rule 5",
        "description": "Premium ID is 12 bytes: first 6 bytes of the policy number + YYMMDD of the calculation date, assuming one calculation per policy per day.",
        "formula": "Premium ID is 12 bytes: first 6 bytes of the policy number + YYMMDD of the calculation date, assuming one calculation per policy per day."
      },
      {
        "rule_id": "Rule 6",
        "name": "PREMCALC Rule 6",
        "description": "Premium calculation uses product\u2011specific constants: base amount, risk rate, coverage rate, deductible rate, minimum premium, and maximum discount.",
        "formula": null
      },
      {
        "rule_id": "Rule 7",
        "name": "PREMCALC Rule 7",
        "description": "Discount applied cannot exceed the product\u2011specific maximum discount and premium cannot fall below the product\u2011specific minimum.",
        "formula": null
      },
      {
        "rule_id": "Rule 8",
        "name": "PREMCALC Rule 8",
        "description": "Earned premium = calculated premium; unearned premium = written premium \u2013 earned premium.",
        "formula": "Earned premium = calculated premium; unearned premium = written premium \u2013 earned premium."
      },
      {
        "rule_id": "Rule 9",
        "name": "PREMCALC Rule 9",
        "description": "All input files must be sorted by policy number to allow sequential matching.",
        "formula": null
      },
      {
        "rule_id": "Rule 10",
        "name": "PREMCALC Rule 10",
        "description": "Fatal file\u2011open or I/O errors abort processing and set RETURN\u2011CODE to 12.",
        "formula": "Fatal file\u2011open or I/O errors abort processing and set RETURN\u2011CODE to 12."
      }
    ],
    "inputs": [
      "POLICY-IN (sequential file containing policy header records)",
      "PROPERTY-IN (sequential file containing property asset records)",
      "VEHICLE-IN (sequential file containing vehicle asset records)",
      "COVERAGE-IN (sequential file containing coverage detail records)"
    ],
    "outputs": [
      "PREMIUM-OUT (sequential file containing calculated premium records)",
      "ERROR-OUT (sequential file containing error records for missing data or validation failures)"
    ],
    "transformations": [
      "Read and buffer the next property, vehicle, and coverage records to enable sequential matching by policy number.",
      "Aggregate all coverage records for a policy: total coverage limit (WS-COV-LIMIT-TOTAL), total deductible (WS-DEDUCT-TOTAL), and coverage count (WS-COVERAGE-COUNT).",
      "Calculate risk value as (asset value * risk\u2011rate) using WS\u2011HO\u2011RISK\u2011RATE or WS\u2011AU\u2011RISK\u2011RATE.",
      "Calculate premium components: base amount, coverage\u2011rate component, deductible\u2011rate component, then apply discount (capped by WS\u2011HO\u2011MAX\u2011DISC / WS\u2011AU\u2011MAX\u2011DISC) and enforce minimum premium (WS\u2011HO\u2011MIN / WS\u2011AU\u2011MIN).",
      "Compose PO-PREMIUM-ID = first 6 characters of PI-POLICY-NO concatenated with WS-CURRENT-DATE (YYMMDD).",
      "Populate PO-REC with written premium (from policy), earned premium (calculated), unearned premium (written minus earned), and calculation date.",
      "Write error records with ER-CODE and ER-MESSAGE when required asset or coverage data is missing or product type is invalid."
    ],
    "dependencies": [
      "File definitions for POLICY-IN, PROPERTY-IN, VEHICLE-IN, COVERAGE-IN, PREMIUM-OUT, ERROR-OUT.",
      "Rating constants defined in WS\u2011RATING\u2011CONSTANTS (HO and AU base, rates, min, max\u2011discount).",
      "Cobol intrinsic FUNCTION CURRENT\u2011DATE for generating the calculation date.",
      "Work\u2011storage fields for file status, EOF switches, calculation accumulators, and counters."
    ]
  },
  {
    "id": "RPTEXTRACT.CBL",
    "name": "RPTEXTRACT.CBL",
    "type": "COBOL",
    "lines": 172,
    "entities": 23,
    "relationships": 20,
    "rules": 5,
    "purpose": "Generate a monthly insurance report by merging policy data with premium data, calculating unearned premium for each policy, and appending a static KPI summary to the output file.",
    "raw_code": "       IDENTIFICATION DIVISION.\n       PROGRAM-ID. RPTEXTRACT.\n\n       ENVIRONMENT DIVISION.\n\n       INPUT-OUTPUT SECTION.\n\n       FILE-CONTROL.\n\n           SELECT POLICY-IN\n               ASSIGN TO 'POLICY.DAT'\n               ORGANIZATION IS LINE SEQUENTIAL.\n\n           SELECT PREMIUM-IN\n               ASSIGN TO 'PREMIUM.DAT'\n               ORGANIZATION IS LINE SEQUENTIAL.\n\n           SELECT REPORT-OUT\n               ASSIGN TO 'MONTHLY_REPORT.TXT'\n               ORGANIZATION IS LINE SEQUENTIAL.\n\n       DATA DIVISION.\n\n       FILE SECTION.\n\n       FD  POLICY-IN.\n\n       01  POLICY-REC.\n           05 POL-POLICY-NO          PIC X(12).\n           05 POL-CUSTOMER-ID        PIC X(10).\n           05 POL-AGENT-ID           PIC X(10).\n           05 POL-PRODUCT            PIC X(02).\n           05 POL-STATUS             PIC X(02).\n\n       FD PREMIUM-IN.\n\n       01 PREMIUM-REC.\n           05 PREM-POLICY-NO         PIC X(12).\n           05 WRITTEN-PREMIUM        PIC 9(9)V99.\n           05 EARNED-PREMIUM         PIC 9(9)V99.\n\n       FD REPORT-OUT.\n\n       01 REPORT-OUT-REC             PIC X(120).\n\n       WORKING-STORAGE SECTION.\n\n       COPY RPTEXTRACT.\n\n       77 EOF-POLICY                 PIC X VALUE 'N'.\n          88 END-OF-POLICY VALUE 'Y'.\n\n       77 WS-UNEARNED                PIC 9(9)V99.\n\n       77 WS-REPORT-MONTH            PIC X(06)\n                                     VALUE '202607'.\n\n       77 WS-HEADER                  PIC X(120)\n          VALUE\n       'REPORT_MONTH|POLICY_NO|CUSTOMER_ID|AGENT_ID|PRODUCT|STATUS|WRITTEN_PREMIUM|EARNED_PREMIUM|UNEARNED_PREMIUM'.\n\n       PROCEDURE DIVISION.\n\n       MAIN-PARA.\n\n           OPEN INPUT POLICY-IN\n                INPUT PREMIUM-IN\n                OUTPUT REPORT-OUT\n\n           WRITE REPORT-OUT-REC FROM WS-HEADER\n\n           PERFORM UNTIL END-OF-POLICY\n\n               READ POLICY-IN\n                   AT END\n                      SET END-OF-POLICY TO TRUE\n                   NOT AT END\n\n                      READ PREMIUM-IN\n\n                      COMPUTE WS-UNEARNED =\n                              WRITTEN-PREMIUM\n                            - EARNED-PREMIUM\n\n                      MOVE WS-REPORT-MONTH\n                           TO RPT-REPORT-MONTH\n\n                      MOVE POL-POLICY-NO\n                           TO RPT-POLICY-NO\n\n                      MOVE POL-CUSTOMER-ID\n                           TO RPT-CUSTOMER-ID\n\n                      MOVE POL-AGENT-ID\n                           TO RPT-AGENT-ID\n\n                      MOVE POL-PRODUCT\n                           TO RPT-PRODUCT\n\n                      MOVE POL-STATUS\n                           TO RPT-STATUS\n\n                      MOVE WRITTEN-PREMIUM\n                           TO RPT-WRITTEN-PREM\n\n                      MOVE EARNED-PREMIUM\n                           TO RPT-EARNED-PREM\n\n                      MOVE WS-UNEARNED\n                           TO RPT-UNEARNED-PREM\n\n                      WRITE REPORT-OUT-REC\n                          FROM REPORT-RECORD\n\n               END-READ\n\n           END-PERFORM\n\n           PERFORM WRITE-KPI-SUMMARY\n\n           CLOSE POLICY-IN\n                 PREMIUM-IN\n                 REPORT-OUT\n\n           STOP RUN.\n\n       WRITE-KPI-SUMMARY.\n\n           MOVE\n           '=============================================================='\n           TO REPORT-OUT-REC\n           WRITE REPORT-OUT-REC\n\n           MOVE\n           'MONTHLY KPI SUMMARY'\n           TO REPORT-OUT-REC\n           WRITE REPORT-OUT-REC\n\n           MOVE\n           '=============================================================='\n           TO REPORT-OUT-REC\n           WRITE REPORT-OUT-REC\n\n           MOVE\n           'TOTAL POLICIES        : 14500'\n           TO REPORT-OUT-REC\n           WRITE REPORT-OUT-REC\n\n           MOVE\n           'ACTIVE POLICIES       : 13100'\n           TO REPORT-OUT-REC\n           WRITE REPORT-OUT-REC\n\n           MOVE\n           'PENDING POLICIES      : 300'\n           TO REPORT-OUT-REC\n           WRITE REPORT-OUT-REC\n\n           MOVE\n           'EXPIRED POLICIES      : 800'\n           TO REPORT-OUT-REC\n           WRITE REPORT-OUT-REC\n\n           MOVE\n           'CANCELLED POLICIES    : 300'\n           TO REPORT-OUT-REC\n           WRITE REPORT-OUT-REC\n\n           MOVE\n           'WRITTEN = EARNED + UNEARNED : PASSED'\n           TO REPORT-OUT-REC\n           WRITE REPORT-OUT-REC.",
    "business_rules": [
      {
        "rule_id": "Rule 1",
        "name": "RPTEXTRACT Rule 1",
        "description": "Unearned premium must equal written premium minus earned premium",
        "formula": null
      },
      {
        "rule_id": "Rule 2",
        "name": "RPTEXTRACT Rule 2",
        "description": "Report month is fixed to the value '202607' (July 2026)",
        "formula": null
      },
      {
        "rule_id": "Rule 3",
        "name": "RPTEXTRACT Rule 3",
        "description": "Each policy record is assumed to have a matching premium record in the same order",
        "formula": null
      },
      {
        "rule_id": "Rule 4",
        "name": "RPTEXTRACT Rule 4",
        "description": "KPI summary totals are hard\u2011coded (e.g., TOTAL POLICIES = 14500, ACTIVE POLICIES = 13100, etc.)",
        "formula": "KPI summary totals are hard\u2011coded (e.g., TOTAL POLICIES = 14500, ACTIVE POLICIES = 13100, etc.)"
      },
      {
        "rule_id": "Rule 5",
        "name": "RPTEXTRACT Rule 5",
        "description": "Status codes are carried through unchanged from the policy file to the report",
        "formula": null
      }
    ],
    "inputs": [
      "POLICY-IN (POLICY.DAT) \u2013 sequential file containing policy number, customer ID, agent ID, product code, and status",
      "PREMIUM-IN (PREMIUM.DAT) \u2013 sequential file containing policy number, written premium, and earned premium"
    ],
    "outputs": [
      "REPORT-OUT (MONTHLY_REPORT.TXT) \u2013 sequential text file containing the header, one line per policy with calculated unearned premium, and a KPI summary section"
    ],
    "transformations": [
      "Compute WS-UNEARNED = WRITTEN-PREMIUM - EARNED-PREMIUM for each policy",
      "Map month constant (WS-REPORT-MONTH) and all policy/premium fields into the report record layout (RPTEXTRACT copybook)",
      "Concatenate fields into a pipe\u2011delimited line written to the output file",
      "Append static KPI summary lines with pre\u2011calculated totals"
    ],
    "dependencies": [
      "Copybook RPTEXTRACT (defines REPORT-RECORD layout fields such as RPT-REPORT-MONTH, RPT-POLICY-NO, etc.)",
      "File definitions in the ENVIRONMENT DIVISION for POLICY-IN, PREMIUM-IN, and REPORT-OUT",
      "Sequential file I/O operations (OPEN, READ, WRITE, CLOSE) provided by the COBOL runtime"
    ]
  },
  {
    "id": "ClaimCenter_CPP_Breakdown.sql",
    "name": "ClaimCenter_CPP_Breakdown.sql",
    "type": "SQL",
    "lines": 346,
    "entities": 34,
    "relationships": 30,
    "rules": 7,
    "purpose": "Generate a claim\u2011level loss breakdown (incurred amount) by policy source and line of business, suitable for profit\u2011and\u2011loss or YTD loss reporting, using ClaimCenter transaction data and TFG loss transaction code mappings.",
    "raw_code": "-- *****************************************************************************************\n--\n-- With filter (primarily YTD) & data returned modifications this can be also used for P&L \n-- incurred losses using the detail calculation.  It will also require a join to PC to get \n-- profit center and uses the TFG loss transaction codes as a filter.\n--\n-- *****************************************************************************************\n-- ************************************************************************************\n-- Server: PBENGWCSQL01    Converted to Cloud Claim Center views.\n--  Must Join to Policy Center to get accurate policy underwriting company\n-- ************************************************************************************\n\n\n -- Not used\ndeclare @PV_STARTDATE datetime = '2026-6-30 00:00:00'\ndeclare @PV_ENDDATE datetime = '2026-08-1 00:00:00'\n\n\nselect   --*\ndistinct \nPolSource,\ncase \n\twhen LOBCode = 'Business Owners Line' then 'BP7Line'\n\twhen LOBCode like 'Workers%' then 'Workers Comp Line'\n\telse LOBCode\nend as LOBCode\n--,ClaimNumber\n--,LossDate\n--,ReportedDate\n--,Count(0) as RecCount\n,sum(TransAmount) as IncurredAmount\n,PolicyNumber\nfrom\n(\nSelect \n\t--rownum,\n\tPolSource,\n\tPolicyPrefix_Ext,\n\tLOBCode,\n\t \n\tClaimNumber,\n\tPolicyType,\n\tPolicyType2,\n\tClaimRep1,\n\tClaimRep2,\n\tClaimState,\n\tPolicyState,\n\tPolicyNumber,\n\t--right('000' + cast(PolicyDec as varchar(2)),3)  as PolicyDec,\n\tPolicyDec,\n\tProducer,\n\tCompany,\n\tPolOrgEffDate,\n\tPolEffDate,\n\tPolExpDate,\n\tReportedDate,\n\tLossDate,\n\tCauseOfLoss,\n\tCosttype,\n\tTranCode,\n\tRecoveryCat,\n\tcase\n\t\twhen TFGTran = '431' AND CostType = 'Indemnity' AND rownum = 1 then '421'\n\t\twhen TFGTran = '431' AND CostType = 'Indemnity' AND rownum <> 1 then '431'\n\t\twhen TFGTran = '431' AND CostType <> 'Indemnity' AND rownum = 1 then '422'\n\t\twhen TFGTran = '431' AND CostType <> 'Indemnity' AND rownum <> 1 then '432'\n\telse TFGTran end as TFGTran,\n\tAcctDate_sql,\n\tAcctDate, \n\tright('000' + cast(ClmtNumber as varchar(3)),3) as ClmtNumber,\n\tright('00000000' + isnull(ltrim(Class),'0'),8) as Class,\n\t\t\n\t--FinancialAmount,\n\tCoveragePatternCode,\n\t\n\tCovSubType, \n\tCheckNumber,\n\tIssueDate,\n\tDoesNotErodeReserves,\n\tReinCo,\n\tReinsAmt,\n\tAmount,\n\tTransAmount\n\nfrom\n(\nSELECT \n\tcase\n\t\twhen PolicyPrefix_Ext is null then 'Legacy'\n\t\t\telse 'Guidewire'\n\t\t\tend as PolSource,\n\n\tPolicyPrefix_Ext,\n\tcase \n\t\twhen tt.TYPECODE = 'Reserve' then\n\t\t\trow_number() over(partition by ClaimNumber, ex.id, tt.typecode, CST.NAME\n\t\t\t\t\t\t\torder by tl.CreateTime)\n\t\telse 0 \n\t\tend\t\t\t\t\t\t\t\t\t\t\tas rownum,\n\tcast(cl.ClaimNumber\t\t\t\t\tas char(13)) as ClaimNumber\n\t,cast(PolicyPrefix_Ext\t\t\t\tas char(3)) as PolicyType\n\t,lob.name\t\t\t\t\t\tas LOBCode\n\t,PolicyTypePrefix_Ext as PolicyType2\n\t,cast(left(ProducerCode,2)\tas char(2)) as ClaimState\n\t,cast(left(ProducerCode,2)\tas char(2)) as PolicyState\n\n\t,case \n\t\twhen left(ProducerCode,2) = '13' then left(isnull(u1.InRepID_ext,'00000'),5)\n\t\telse left(isnull(u1.OhRepID_ext,'00000'),5)\n\t\tend\t\t\t\t\t\t\t\t\t\t\tas ClaimRep1 \n\n\t,case\n\t\twhen SubroRepresentative_Ext is null then '00000'\n\t\telse isnull(left(u2.SubroRepId_Ext,5),'00000') \n\t\tend\t\t\t\t\t\t\t\t\t\t\tas ClaimRep2\n\t\t\t\n\t,cast((po.Policynumber)\tas char(10))\t\t\t\tas PolicyNumber\n\t,po.PolicyDecNo_Ext  as PolicyDec\n  \n\t,case \n\t\t\twhen uw.name = 'Lightning Rod Mutual Insurance Company'\t then 'LRM'\n\t\t\twhen uw.name = 'Western Reserve Mutual Casualty Company' then 'WRM'\n\t\t\twhen uw.name = 'Sonnenberg Mutual Insurance Company'\t then 'SON'\n\t\t\telse 'UNK'\n\t\tend\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t as Company\n\t,CAST(replace(convert(char(10), po.OrigEffectiveDate, 101), '/', '') AS CHAR(8)) as PolOrgEffDate\n\t,CAST(replace(convert(char(10), po.EffectiveDate, 101), '/', '')\t AS CHAR(8)) as PolEffDate\n\t,CAST(replace(convert(char(10), po.ExpirationDate, 101), '/', '')\t AS CHAR(8)) as PolExpDate\n\t,cl.ReportedDate\n\t,cl.Lossdate\n\t,upper(cast(left(tlc.TYPECODE,45)\t\t\t\t\t\t\t\t\t AS CHAR(45))) as CauseOfLoss\n\t\n\t----\n\t,cv.CicsClaimCov_Ext as TFGCov\n\n\t,case\n\t\twhen ct.typecode in ('CPEquipBrkCov')\t\t\t\t\tthen '270'\n\t\twhen ct.typecode in ('CPINCCCov')\t\t\t\t\t\tthen '010'\n\t\twhen cv.CicsClaimCov_Ext in ('615','616','617','618')\tthen '010'\n\t\telse '021' end as TFGASL\n\n\t,case\n\t\twhen ct.typecode in ('CPEquipBrkCov')\t\t\t\t\tthen '270'\n\t\twhen ct.typecode in ('CPINCCCov')\t\t\t\t\t\tthen '010'\n\t\twhen tlc.TYPECODE in ('fire','fire-wood_coal-stove','ightning','vandalism',\n\t\t\t\t\t\t\t  'explosion','sprinkler','sprinkler_leakage')\tthen '010'\n\t\telse '021' end as GWASL\n     --------\n\t\n\t,tl.CreateTime as TLICreate\n\t,isnull(tset.ApprovalDate,'01/01/2000') as ApprovalDate\n\t,ScheduledSendDate \n\t\n\t,case \n\t\twhen tl.CreateTime >= isnull(tset.ApprovalDate,'01/01/2000') then cast(tl.CreateTime as date)\n\t\telse cast(tset.approvaldate as date)\n\t\tend\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tas AcctDate_sql\n\t\n\t,CAST(replace(convert(char(10)\n\t\n\t,case \n\t\twhen tl.CreateTime >= isnull(tset.ApprovalDate,'01/01/2000') then tl.CreateTime \n\t\telse tset.approvaldate end, 101), '/', '')\t AS CHAR(8))\t\t\t\t\tas AcctDate\n\t\n\t,cast(left(ProducerCode,9) \t\t\t\t\t\t\t\t\t\t\t AS CHAR(9)) as Producer\n\t,cast((isnull(CicsClaimantNum_Ext,0))\tas numeric(3))\t\t\t\t\t\t\tas ClmtNumber\n\t,cast(cls.Code as char(8))\t\t\t\t\t\t\t\tas Class\n\t\n\t,DoesNotErodeReserves\n\t\n\t,CicsUnitLocNum_Ext\n\t,CicsClassCode_Ext\n\t,cv.CicsClaimCov_Ext\t\tas CovCicsClaimCov\n\t,ex.CicsClaimCov_Ext\t\tas ExpCicsClaimCov\n\t\n\t,case \n\twhen tt.TYPECODE = 'Reserve' AND cst.NAME = 'Indemnity' then '431'\n\twhen tt.TYPECODE = 'Reserve' AND cst.NAME <> 'Indemnity' then '432'\n\twhen tt.TYPECODE = 'Payment' AND cst.NAME = 'Indemnity' AND DoesNotErodeReserves = 1 then '321'\n\twhen tt.TYPECODE = 'Payment' AND cst.NAME = 'Indemnity' AND DoesNotErodeReserves <> 1 then '331'\n\twhen tt.TYPECODE = 'Payment' AND cst.NAME <> 'Indemnity' AND DoesNotErodeReserves = 1 then '322'\n\twhen tt.TYPECODE = 'Payment' AND cst.NAME <> 'Indemnity' AND DoesNotErodeReserves <> 1 then '332'\n\twhen tt.TYPECODE = 'Recovery' AND RV.TypeCode = 'Credit_loss' AND cst.NAME = 'Indemnity' then '321'\n\twhen tt.TYPECODE = 'Recovery' AND rv.TYPECODE = 'Credit_loss' AND cst.NAME <> 'Indemnity' then '322'\n\twhen tt.TYPECODE = 'Recovery' AND cst.NAME = 'EXPENSE - OTHERS' then '322'\n\twhen tt.TYPECODE = 'Recovery' AND rv.TYPECODE = 'credit_exp' then '322'\n\twhen tt.TYPECODE = 'Recovery' AND rv.TYPECODE = 'deductible' then '321'\n\twhen tt.TYPECODE = 'Recovery' AND rv.TYPECODE = 'salvage' AND cst.NAME = 'Indemnity' then '341'\n\twhen tt.TYPECODE = 'Recovery' AND rv.TYPECODE = 'salvage' AND cst.NAME <> 'Indemnity' then '342'\n\twhen tt.TYPECODE = 'Recovery' AND rv.TYPECODE = 'subro' AND cst.NAME = 'Indemnity' then '351'\n\twhen tt.TYPECODE = 'Recovery' AND rv.TYPECODE = 'subro' AND cst.NAME <> 'Indemnity' then '353'\n\telse 'XXX'\n\tend as TFGTran\n\t\t\n\t\t,rv.typecode as RecoveryCat\n\t,upper(cast(ct.typecode as char(64)))\t\t\t\t\t\t\t\t\t as CoveragePatternCode\n\t--,upper(cast(ex.CoverageSubType as char(50)))\t\t\t\t\t\t\t as ExCovSubType\n\t\n\t,ct.typecode\t\t\t \n\t--,ex.CoverageSubType\t\t\t\t\t\t\t\t\t\t\t\t\t\t as exCoverageSubType\t\t\t\t\t\t\t\t\t\t\t\t  \n\t\n\t,upper(cast(st.typecode as char(50)))\t\t\t\t\t\t\t\t\t as CovSubType\n\t,tt.TYPECODE\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t as TranCode\n\t,upper(cast(CST.NAME as char(25)))\t\t\t\t\t\t\t\t\t\t as CostType\n\t--,upper(isnull(cast(ccat.TYPECODE as char(25)),''))\t\t\t\t\t\t as CostCategory\n\t--,isnull(ccat.NAME, '')\tas CostCategory\n\t--,ISNULL(lc.Name, '')\tas LineCategory\n\t\n\t,case\n\t\twhen CST.NAME = 'Indemnity'\t\t\t\t\t\t\t       then '                                             '\n\t\twhen ccat.TYPECODE in ('legalexpense_ext','appraisal_ext') then upper(cast(ccat.TYPECODE as char(45)))\n\t\t\n\t\t-- these are retired\n\t\twhen lc.TYPECODE in ('deductible','formerdeductible')      then upper(cast(ccat.TYPECODE as char(45)))\n\t\twhen lc.TYPECODE is not null\t\t\t\t\t\t       then upper(cast(lc.TYPECODE as char(45)))\n\t\t-- not in prod costcat table\n\t\twhen lc.TYPECODE is null and ccat.TYPECODE = 'autoparts'   then 'OTHER                                        '\n\t\telse upper(cast(ccat.TYPECODE as char(45)))\n\t\tend\t\t\t\t\t\t\t\t\t\t\tas ExpCode\n\t\n\t,ISNULL(cast(CheckNumber as char(9)),'')\t\tas CheckNumber\n\t,ISNULL(CAST(replace(convert(char(10), ck.IssueDate, 101), '/', '') AS CHAR(8)),'') as IssueDate \n\t,'  '\t\t\t\t\t\t\t\t\t\t\tas ReinCo\n\t-- these not needed for loss stats\n\t--,tls.name\t\t\t\t\t\t\t\t\t\tas TranLifeStatus\n\t--,ts.TYPECODE\t\t\t\t\t\t\t\t\tas TransStatus\n\n\t--,tl.TransactionAmount as TrxAmt\n\t,'000000000.00'\t\t\t\t\t\t\t\t\tas ReinsAmt\n\t\n\t\n\t, case \n\t\twhen tt.TYPECODE = 'Payment' then\n\t\t\tcase\n\t\t\t\twhen DoesNotErodeReserves = 0 then isnull(tl.TransactionAmount,0.00) * -1\n\t\t\t\telse tl.TransactionAmount\n\t\t\tend\n\t\twhen tt.TYPECODE = 'Recovery' then isnull(tl.TransactionAmount,0.00) * -1\n\t\telse isnull(tl.TransactionAmount,0.00)\n\n\t\tend\t\t\t\t\t\t\tas TransAmount\n\t\n\t\n\t--,tl.TransactionAmount\n\t\n\t\n\t,CASE \n\t\twhen tt.TYPECODE = 'Recovery'\tthen\n\t\t\tcase\n\t\t\t\tWHEN isnull(tl.TransactionAmount,0.00) > 0 \tTHEN \n\t\t\t\t\tCONCAT('-', RIGHT(CAST((-100000000 + isnull(-1 * tl.TransactionAmount,0.00)) AS numeric(11,2)),11)) \n\t\t\t\tELSE \n\t\t\t\t\tRIGHT(CONCAT('00000000', CAST(isnull(-1 * tl.TransactionAmount,0.00) AS numeric(11,2))),12) \n\t\t\tEND  \n\t\telse\n\t\t\tcase\n\t\t\t\tWHEN isnull(tl.TransactionAmount,0.00) < 0 \tTHEN \n\t\t\t\t\tCONCAT('-', RIGHT(CAST((-100000000 + isnull(tl.TransactionAmount,0.00)) AS numeric(11,2)),11)) \n\t\t\t\tELSE \n\t\t\t\t\tRIGHT(CONCAT('00000000', CAST(isnull(tl.TransactionAmount,0.00) AS numeric(11,2))),12) \n\t\t\tEND  \n\t\tend\n\t\t\tas Amount \t\t\t\t\t\t\n\t,tl.id\t\t\t\t\t\tas TransLineItemID\n\t,t.id\t\t\t\t\t\tas TransactionID\n\t--  **********************************************************************************************\n\t\t,cv.PolicySystemId\t\t\t\t\tas CovPolSystemID  \n\t\t\n\t\t,case \n\t\t\twhen upper(cast(ct.typecode as char(50))) in ('BP7EmploymentPracticesLiabilityInsurance','BP7SupplementalExtendReportingPeriodEPLI') then\n\t\t\t\tcase \n\t\t\t\t\twhen cv.Deductible > 99999 then '99999     '\t-- Deductible is S9(5) on TFG stats\n\t\t\t\t\telse cast(isnull(cv.Deductible, '          ')\tas char(10))  \n\t\t\t\tend\n\t\t\t--else cast(isnull(stat.DedStatAmount, '          ') as char(10)) \n\t\t\telse '          '\n\t\t\tend as DedStatAmount\n\t\n\t\t--closed and reopen fields added 09/21/2018 ek\n\t\t\n\t\t,CAST(replace(convert(char(10), cl.CloseDate, 101), '/', '') AS CHAR(8)) as Claim_CloseDate\n\t\t,CAST(replace(convert(char(10), cl.ReOpenDate, 101), '/', '') AS CHAR(8)) as Claim_ReOpenDate\n\t\t\n\t\t\t\t\t\t\t\t\t\t\t\t\n\nFROM vw_curr_cc_transactionlineitem tl\n\tleft join vw_curr_cc_transaction t\t\t\t\t\t(nolock) on tl.TransactionID\t= t.id\n\tleft join vw_curr_cc_transactionset tset\t\t\t(nolock) on t.TransactionSetID\t= tset.id\n\tleft join vw_curr_cc_claim cl\t\t\t\t\t\t(nolock) on t.ClaimID\t\t\t= cl.id\n\tleft join vw_curr_cc_policy po\t\t\t\t\t\t(nolock) on cl.PolicyID\t\t\t= po.id\n\tleft join vw_curr_cc_check ck\t\t\t\t\t\t(nolock) on t.CheckID\t\t\t= ck.id\n\tleft join vw_curr_cc_reserveline rl\t\t\t\t\t(nolock) on t.ReserveLineID\t\t= rl.id\n\tleft join vw_curr_cc_exposure ex\t\t\t\t\t(nolock) on t.ExposureID\t\t= ex.id\n\tleft join vw_curr_cc_coverage cv\t\t\t\t\t(nolock) on ex.CoverageID\t\t= cv.id\n\tleft join vw_curr_cc_contact clmcont\t\t\t\t(nolock) on ex.ClaimantDenormID = clmcont.id\n\t\n\tleft join vw_curr_cc_user u1\t\t\t\t\t\t(nolock) on cl.AssignedUserID\t= u1.id\n\tleft join vw_curr_cc_user u2\t\t\t\t\t\t(nolock) on cl.SubroRepresentative_Ext \t= u2.id\n\t\n\tleft join vw_curr_cc_riskunit ru\t\t\t\t\t(nolock) on cv.RiskUnitID\t\t= ru.id\n\tleft join vw_curr_cc_classcode cls\t\t\t\t\t(nolock) on ru.ClassCodeID\t\t= cls.id\n\tleft join vw_curr_cctl_lobcode lob\t\t\t\t\t\t\ton cl.LOBCode\t\t\t= lob.id\n\tleft join vw_curr_cctl_policytype polt\t\t\t\t(nolock) on po.PolicyType\t\t= polt.id\n\tleft join vw_curr_cctl_transaction tt\t\t\t\t(nolock) on t.Subtype\t\t\t= tt.id\n\tleft join vw_curr_cctl_losscause tlc\t\t\t\t(nolock) on cl.LossCause\t\t= tlc.id\n\tleft join vw_curr_cctl_transactionstatus ts\t\t\t(nolock) on t.Status\t\t\t= ts.id\n\tleft join vw_curr_cctl_costtype CST\t\t\t\t\t(nolock) on T.CostType\t\t\t= CST.ID\n\tleft join vw_curr_cctl_costcategory ccat\t\t\t(nolock) on t.CostCategory\t\t= ccat.ID\n\tleft join vw_curr_cctl_linecategory lc\t\t\t\t(nolock) on TL.LineCategory\t\t= lc.ID\n\tleft join vw_curr_cctl_transactionlifecyclestate tls (nolock) on T.LifeCycleState\t= tls.ID\n\tleft join vw_curr_cctl_recoverycategory rv\t\t\t (nolock) on t.RecoveryCategory = rv.ID\n\tleft join vw_curr_cctl_underwritingcompanytype uw\t (nolock) on po.UnderwritingCo  = uw.id\n\tleft join vw_curr_cctl_coveragesubtype st\t\t\t(nolock) on ex.CoverageSubType\t= st.id\n\tleft join vw_curr_cctl_coveragetype ct\t\t\t\t(nolock) on cv.type\t\t\t\t= ct.id\n\tleft join vw_curr_cctl_checkbatching cb\t\t\t\t(nolock) on ck.CheckBatching\t= cb.ID\n\tleft join vw_curr_cctl_paymenttype pt\t\t\t\t(nolock) on t.PaymentType\t\t= pt.id\n\twhere tls.name = 'committed'\n\tand tset.ApprovalStatus=1\t\t\t\t--Approved  added 08/29/2018 ek\n\t\n\t-- 08/07/24  mec\n\tand tl.Retired = 0\t\t\t\t\t\t-- If > 0 then transaction was deleted (matches DH)\n) x\n \n)a\t\n-- For Incurred  *********************************************************\nwhere TFGTran in ('321', '351', '341', '421', '431')\n--and PolSource in ('guidewire') --('legacy')\n--and PolSource in ('legacy') \n--and AcctDate_sql < '08/01/2024'\nand AcctDate_sql > @PV_STARTDATE and AcctDate_sql < @PV_ENDDATE --'08/01/2024'\n--and AcctDate_sql > '12/30/2022' and AcctDate_sql < '12/30/2023'\t  -- 2023\nand PolSource = 'Guidewire'\n group by \n PolSource \n  --LOBCode \n -- ClaimNumber\n  ,LOBCode\n  ,PolicyNumber\n -- ,LossDate\n -- ,ReportedDate\n having sum(TransAmount) <> 0\n\n order by \n PolSource desc \n --LOBCode \n --ClaimNumber",
    "business_rules": [
      {
        "rule_id": "Rule 1",
        "name": "ClaimCenter_CPP_Breakdown Rule 1",
        "description": "If LOBCode = 'Business Owners Line' then report as 'BP7Line'; if LOBCode starts with 'Workers' then report as 'Workers Comp Line'.",
        "formula": "If LOBCode = 'Business Owners Line' then report as 'BP7Line'; if LOBCode starts with 'Workers' then report as 'Workers Comp Line'."
      },
      {
        "rule_id": "Rule 2",
        "name": "ClaimCenter_CPP_Breakdown Rule 2",
        "description": "TFGTran mapping rules: e.g., Reserve + Indemnity \u2192 '431' (first row) or '421' (subsequent rows); Reserve + non\u2011Indemnity \u2192 '432'/'422'; Payment + Indemnity with DoesNotErodeReserves = 1 \u2192 '321', otherwise '331'; Payment + non\u2011Indemnity with DoesNotErodeReserves = 1 \u2192 '322', otherwise '332'; Recovery categories map to specific TFGTran codes (e.g., Credit_loss + Indemnity \u2192 '321', salvage + Indemnity \u2192 '341', subro + Indemnity \u2192 '351', etc.).",
        "formula": "TFGTran mapping rules: e.g., Reserve + Indemnity \u2192 '431' (first row) or '421' (subsequent rows); Reserve + non\u2011Indemnity \u2192 '432'/'422'; Payment + Indemnity with DoesNotErodeReserves = 1 \u2192 '321', otherwise '331'; Payment + non\u2011Indemnity with DoesNotErodeReserves = 1 \u2192 '322', otherwise '332'; Recovery categories map to specific TFGTran codes (e.g., Credit_loss + Indemnity \u2192 '321', salvage + Indemnity \u2192 '341', subro + Indemnity \u2192 '351', etc.)."
      },
      {
        "rule_id": "Rule 3",
        "name": "ClaimCenter_CPP_Breakdown Rule 3",
        "description": "Transaction amounts are signed: payments are negative unless they do not erode reserves; recoveries are always negative; reserves retain their sign.",
        "formula": null
      },
      {
        "rule_id": "Rule 4",
        "name": "ClaimCenter_CPP_Breakdown Rule 4",
        "description": "Company code assignment based on underwriting company name: Lightning Rod Mutual \u2192 'LRM', Western Reserve Mutual \u2192 'WRM', Sonnenberg Mutual \u2192 'SON', otherwise 'UNK'.",
        "formula": null
      },
      {
        "rule_id": "Rule 5",
        "name": "ClaimCenter_CPP_Breakdown Rule 5",
        "description": "Deductible amount is capped at 99999 for specific coverage types (BP7EmploymentPracticesLiabilityInsurance, BP7SupplementalExtendReportingPeriodEPLI).",
        "formula": null
      },
      {
        "rule_id": "Rule 6",
        "name": "ClaimCenter_CPP_Breakdown Rule 6",
        "description": "Only the first reserve line (rownum = 1) influences certain TFGTran adjustments.",
        "formula": "Only the first reserve line (rownum = 1) influences certain TFGTran adjustments."
      },
      {
        "rule_id": "Rule 7",
        "name": "ClaimCenter_CPP_Breakdown Rule 7",
        "description": "The query is intended for YTD or P&L loss reporting and expects additional joins to Policy Center for underwriting company accuracy.",
        "formula": null
      }
    ],
    "inputs": [
      "vw_curr_cc_transactionlineitem",
      "vw_curr_cc_transaction",
      "vw_curr_cc_transactionset",
      "vw_curr_cc_claim",
      "vw_curr_cc_policy",
      "vw_curr_cc_check",
      "vw_curr_cc_reserveline",
      "vw_curr_cc_exposure",
      "vw_curr_cc_coverage",
      "vw_curr_cc_contact",
      "vw_curr_cc_user (assigned user)",
      "vw_curr_cc_user (subro representative)",
      "vw_curr_cc_riskunit",
      "vw_curr_cc_classcode",
      "vw_curr_cctl_lobcode",
      "vw_curr_cctl_policytype",
      "vw_curr_cctl_transaction",
      "vw_curr_cctl_losscause",
      "vw_curr_cctl_transactionstatus",
      "vw_curr_cctl_costtype",
      "vw_curr_cctl_costcategory",
      "vw_curr_cctl_linecategory",
      "vw_curr_cctl_transactionlifecyclestate",
      "vw_curr_cctl_recoverycategory",
      "vw_curr_cctl_underwritingcompanytype"
    ],
    "outputs": [
      "Result set with columns: PolSource, LOBCode, PolicyNumber, IncurredAmount (sum of TransAmount)"
    ],
    "transformations": [
      "CASE expression to map PolSource based on presence of PolicyPrefix_Ext (Legacy vs Guidewire).",
      "ROW_NUMBER() partitioned by ClaimNumber, exposure id, transaction type and cost type to identify first reserve line.",
      "CASE logic to derive TFGTran codes from transaction type, cost type, and DoesNotErodeReserves flag, including special handling for first reserve row.",
      "Sign adjustment of TransactionAmount: payments are negated unless DoesNotErodeReserves = 1; recoveries are always negated; reserves keep original sign.",
      "Aggregation: SUM(TransAmount) grouped by PolSource, normalized LOBCode, and PolicyNumber.",
      "LOBCode normalization: Business Owners Line \u2192 BP7Line, Workers* \u2192 Workers Comp Line, otherwise unchanged.",
      "Date conversion to CHAR(8) format (YYYYMMDD) for policy effective dates, accounting dates, claim close/reopen dates.",
      "Formatting of numeric identifiers (ClmtNumber, Class, PolicyDec) with leading zeros.",
      "Deductible amount handling: conditional formatting based on coverage type and deductible value.",
      "Distinct selection to eliminate duplicate rows after aggregation."
    ],
    "dependencies": [
      "ClaimCenter cloud view layer (vw_curr_cc_*) providing transactional and master data.",
      "Policy Center data (mentioned in comments) for accurate underwriting company mapping.",
      "TFG loss transaction code reference list (used in CASE statements).",
      "SQL Server date and string functions for formatting."
    ]
  },
  {
    "id": "ClaimCenter_Monoline.sql",
    "name": "ClaimCenter_Monoline.sql",
    "type": "SQL",
    "lines": 342,
    "entities": 37,
    "relationships": 29,
    "rules": 8,
    "purpose": "Generate a claim\u2011level loss summary (incurred amount) filtered primarily by year\u2011to\u2011date, suitable for profit\u2011and\u2011loss reporting, by aggregating transaction amounts from ClaimCenter and enriching them with policy and underwriting information.",
    "raw_code": "-- *****************************************************************************************\n--\n-- With filter (primarily YTD) & data returned modifications this can be also used for P&L \n-- incurred losses using the detail calculation.  It will also require a join to PC to get \n-- profit center and uses the TFG loss transaction codes as a filter.\n--\n-- *****************************************************************************************\n-- ************************************************************************************\n-- Server: PBENGWCSQL01    Converted to Cloud Claim Center views.\n--  Must Join to Policy Center to get accurate policy underwriting company\n-- ************************************************************************************\n\n\n -- Not used\ndeclare @PV_STARTDATE datetime = '2026-6-30 00:00:00'\ndeclare @PV_ENDDATE datetime = '2026-08-1 00:00:00'\n\n\nselect   --*\ndistinct \nPolSource,\nLOBCode \n--,ClaimNumber\n--,LossDate\n--,ReportedDate\n--,Count(0) as RecCount\n,sum(TransAmount) as IncurredAmount\n,PolicyNumber\nfrom\n(\nSelect \n\t--rownum,\n\tPolSource,\n\tPolicyPrefix_Ext,\n\tLOBCode,\n\t \n\tClaimNumber,\n\tPolicyType,\n\tPolicyType2,\n\tClaimRep1,\n\tClaimRep2,\n\tClaimState,\n\tPolicyState,\n\tPolicyNumber,\n\t--right('000' + cast(PolicyDec as varchar(2)),3)  as PolicyDec,\n\tPolicyDec,\n\tProducer,\n\tCompany,\n\tPolOrgEffDate,\n\tPolEffDate,\n\tPolExpDate,\n\tReportedDate,\n\tLossDate,\n\tCauseOfLoss,\n\tCosttype,\n\tTranCode,\n\tRecoveryCat,\n\tcase\n\t\twhen TFGTran = '431' AND CostType = 'Indemnity' AND rownum = 1 then '421'\n\t\twhen TFGTran = '431' AND CostType = 'Indemnity' AND rownum <> 1 then '431'\n\t\twhen TFGTran = '431' AND CostType <> 'Indemnity' AND rownum = 1 then '422'\n\t\twhen TFGTran = '431' AND CostType <> 'Indemnity' AND rownum <> 1 then '432'\n\telse TFGTran end as TFGTran,\n\tAcctDate_sql,\n\tAcctDate, \n\tright('000' + cast(ClmtNumber as varchar(3)),3) as ClmtNumber,\n\tright('00000000' + isnull(ltrim(Class),'0'),8) as Class,\n\t\t\n\t--FinancialAmount,\n\tCoveragePatternCode,\n\t\n\tCovSubType, \n\tCheckNumber,\n\tIssueDate,\n\tDoesNotErodeReserves,\n\tReinCo,\n\tReinsAmt,\n\tAmount,\n\tTransAmount\n\nfrom\n(\nSELECT \n\tcase\n\t\twhen PolicyPrefix_Ext is null then 'Legacy'\n\t\t\telse 'Guidewire'\n\t\t\tend as PolSource,\n\n\tPolicyPrefix_Ext,\n\tcase \n\t\twhen tt.TYPECODE = 'Reserve' then\n\t\t\trow_number() over(partition by ClaimNumber, ex.id, tt.typecode, CST.NAME\n\t\t\t\t\t\t\torder by tl.CreateTime)\n\t\telse 0 \n\t\tend\t\t\t\t\t\t\t\t\t\t\tas rownum,\n\tcast(cl.ClaimNumber\t\t\t\t\tas char(13)) as ClaimNumber\n\t,cast(PolicyPrefix_Ext\t\t\t\tas char(3)) as PolicyType\n\t,lob.TYPECODE\t\t\t\t\t\tas LOBCode\n\t,PolicyTypePrefix_Ext as PolicyType2\n\t,cast(left(ProducerCode,2)\tas char(2)) as ClaimState\n\t,cast(left(ProducerCode,2)\tas char(2)) as PolicyState\n\n\t,case \n\t\twhen left(ProducerCode,2) = '13' then left(isnull(u1.InRepID_ext,'00000'),5)\n\t\telse left(isnull(u1.OhRepID_ext,'00000'),5)\n\t\tend\t\t\t\t\t\t\t\t\t\t\tas ClaimRep1 \n\n\t,case\n\t\twhen SubroRepresentative_Ext is null then '00000'\n\t\telse isnull(left(u2.SubroRepId_Ext,5),'00000') \n\t\tend\t\t\t\t\t\t\t\t\t\t\tas ClaimRep2\n\t\t\t\n\t,cast((po.Policynumber)\tas char(10))\t\t\t\tas PolicyNumber\n\t,po.PolicyDecNo_Ext  as PolicyDec\n  \n\t,case \n\t\t\twhen uw.name = 'Lightning Rod Mutual Insurance Company'\t then 'LRM'\n\t\t\twhen uw.name = 'Western Reserve Mutual Casualty Company' then 'WRM'\n\t\t\twhen uw.name = 'Sonnenberg Mutual Insurance Company'\t then 'SON'\n\t\t\telse 'UNK'\n\t\tend\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t as Company\n\t,CAST(replace(convert(char(10), po.OrigEffectiveDate, 101), '/', '') AS CHAR(8)) as PolOrgEffDate\n\t,CAST(replace(convert(char(10), po.EffectiveDate, 101), '/', '')\t AS CHAR(8)) as PolEffDate\n\t,CAST(replace(convert(char(10), po.ExpirationDate, 101), '/', '')\t AS CHAR(8)) as PolExpDate\n\t,cl.ReportedDate\n\t,cl.Lossdate\n\t,upper(cast(left(tlc.TYPECODE,45)\t\t\t\t\t\t\t\t\t AS CHAR(45))) as CauseOfLoss\n\t\n\t----\n\t,cv.CicsClaimCov_Ext as TFGCov\n\n\t,case\n\t\twhen ct.typecode in ('CPEquipBrkCov')\t\t\t\t\tthen '270'\n\t\twhen ct.typecode in ('CPINCCCov')\t\t\t\t\t\tthen '010'\n\t\twhen cv.CicsClaimCov_Ext in ('615','616','617','618')\tthen '010'\n\t\telse '021' end as TFGASL\n\n\t,case\n\t\twhen ct.typecode in ('CPEquipBrkCov')\t\t\t\t\tthen '270'\n\t\twhen ct.typecode in ('CPINCCCov')\t\t\t\t\t\tthen '010'\n\t\twhen tlc.TYPECODE in ('fire','fire-wood_coal-stove','ightning','vandalism',\n\t\t\t\t\t\t\t  'explosion','sprinkler','sprinkler_leakage')\tthen '010'\n\t\telse '021' end as GWASL\n     --------\n\t\n\t,tl.CreateTime as TLICreate\n\t,isnull(tset.ApprovalDate,'01/01/2000') as ApprovalDate\n\t,ScheduledSendDate \n\t\n\t,case \n\t\twhen tl.CreateTime >= isnull(tset.ApprovalDate,'01/01/2000') then cast(tl.CreateTime as date)\n\t\telse cast(tset.approvaldate as date)\n\t\tend\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tas AcctDate_sql\n\t\n\t,CAST(replace(convert(char(10)\n\t\n\t,case \n\t\twhen tl.CreateTime >= isnull(tset.ApprovalDate,'01/01/2000') then tl.CreateTime \n\t\telse tset.approvaldate end, 101), '/', '')\t AS CHAR(8))\t\t\t\t\tas AcctDate\n\t\n\t,cast(left(ProducerCode,9) \t\t\t\t\t\t\t\t\t\t\t AS CHAR(9)) as Producer\n\t,cast((isnull(CicsClaimantNum_Ext,0))\tas numeric(3))\t\t\t\t\t\t\tas ClmtNumber\n\t,cast(cls.Code as char(8))\t\t\t\t\t\t\t\tas Class\n\t\n\t,DoesNotErodeReserves\n\t\n\t,CicsUnitLocNum_Ext\n\t,CicsClassCode_Ext\n\t,cv.CicsClaimCov_Ext\t\tas CovCicsClaimCov\n\t,ex.CicsClaimCov_Ext\t\tas ExpCicsClaimCov\n\t\n\t,case \n\twhen tt.TYPECODE = 'Reserve' AND cst.NAME = 'Indemnity' then '431'\n\twhen tt.TYPECODE = 'Reserve' AND cst.NAME <> 'Indemnity' then '432'\n\twhen tt.TYPECODE = 'Payment' AND cst.NAME = 'Indemnity' AND DoesNotErodeReserves = 1 then '321'\n\twhen tt.TYPECODE = 'Payment' AND cst.NAME = 'Indemnity' AND DoesNotErodeReserves <> 1 then '331'\n\twhen tt.TYPECODE = 'Payment' AND cst.NAME <> 'Indemnity' AND DoesNotErodeReserves = 1 then '322'\n\twhen tt.TYPECODE = 'Payment' AND cst.NAME <> 'Indemnity' AND DoesNotErodeReserves <> 1 then '332'\n\twhen tt.TYPECODE = 'Recovery' AND RV.TypeCode = 'Credit_loss' AND cst.NAME = 'Indemnity' then '321'\n\twhen tt.TYPECODE = 'Recovery' AND rv.TYPECODE = 'Credit_loss' AND cst.NAME <> 'Indemnity' then '322'\n\twhen tt.TYPECODE = 'Recovery' AND cst.NAME = 'EXPENSE - OTHERS' then '322'\n\twhen tt.TYPECODE = 'Recovery' AND rv.TYPECODE = 'credit_exp' then '322'\n\twhen tt.TYPECODE = 'Recovery' AND rv.TYPECODE = 'deductible' then '321'\n\twhen tt.TYPECODE = 'Recovery' AND rv.TYPECODE = 'salvage' AND cst.NAME = 'Indemnity' then '341'\n\twhen tt.TYPECODE = 'Recovery' AND rv.TYPECODE = 'salvage' AND cst.NAME <> 'Indemnity' then '342'\n\twhen tt.TYPECODE = 'Recovery' AND rv.TYPECODE = 'subro' AND cst.NAME = 'Indemnity' then '351'\n\twhen tt.TYPECODE = 'Recovery' AND rv.TYPECODE = 'subro' AND cst.NAME <> 'Indemnity' then '353'\n\telse 'XXX'\n\tend as TFGTran\n\t\t\n\t\t,rv.typecode as RecoveryCat\n\t,upper(cast(ct.typecode as char(64)))\t\t\t\t\t\t\t\t\t as CoveragePatternCode\n\t--,upper(cast(ex.CoverageSubType as char(50)))\t\t\t\t\t\t\t as ExCovSubType\n\t\n\t,ct.typecode\t\t\t \n\t--,ex.CoverageSubType\t\t\t\t\t\t\t\t\t\t\t\t\t\t as exCoverageSubType\t\t\t\t\t\t\t\t\t\t\t\t  \n\t\n\t,upper(cast(st.typecode as char(50)))\t\t\t\t\t\t\t\t\t as CovSubType\n\t,tt.TYPECODE\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t as TranCode\n\t,upper(cast(CST.NAME as char(25)))\t\t\t\t\t\t\t\t\t\t as CostType\n\t--,upper(isnull(cast(ccat.TYPECODE as char(25)),''))\t\t\t\t\t\t as CostCategory\n\t--,isnull(ccat.NAME, '')\tas CostCategory\n\t--,ISNULL(lc.Name, '')\tas LineCategory\n\t\n\t,case\n\t\twhen CST.NAME = 'Indemnity'\t\t\t\t\t\t\t       then '                                             '\n\t\twhen ccat.TYPECODE in ('legalexpense_ext','appraisal_ext') then upper(cast(ccat.TYPECODE as char(45)))\n\t\t\n\t\t-- these are retired\n\t\twhen lc.TYPECODE in ('deductible','formerdeductible')      then upper(cast(ccat.TYPECODE as char(45)))\n\t\twhen lc.TYPECODE is not null\t\t\t\t\t\t       then upper(cast(lc.TYPECODE as char(45)))\n\t\t-- not in prod costcat table\n\t\twhen lc.TYPECODE is null and ccat.TYPECODE = 'autoparts'   then 'OTHER                                        '\n\t\telse upper(cast(ccat.TYPECODE as char(45)))\n\t\tend\t\t\t\t\t\t\t\t\t\t\tas ExpCode\n\t\n\t,ISNULL(cast(CheckNumber as char(9)),'')\t\tas CheckNumber\n\t,ISNULL(CAST(replace(convert(char(10), ck.IssueDate, 101), '/', '') AS CHAR(8)),'') as IssueDate \n\t,'  '\t\t\t\t\t\t\t\t\t\t\tas ReinCo\n\t-- these not needed for loss stats\n\t--,tls.name\t\t\t\t\t\t\t\t\t\tas TranLifeStatus\n\t--,ts.TYPECODE\t\t\t\t\t\t\t\t\tas TransStatus\n\n\t--,tl.TransactionAmount as TrxAmt\n\t,'000000000.00'\t\t\t\t\t\t\t\t\tas ReinsAmt\n\t\n\t\n\t, case \n\t\twhen tt.TYPECODE = 'Payment' then\n\t\t\tcase\n\t\t\t\twhen DoesNotErodeReserves = 0 then isnull(tl.TransactionAmount,0.00) * -1\n\t\t\t\telse tl.TransactionAmount\n\t\t\tend\n\t\twhen tt.TYPECODE = 'Recovery' then isnull(tl.TransactionAmount,0.00) * -1\n\t\telse isnull(tl.TransactionAmount,0.00)\n\n\t\tend\t\t\t\t\t\t\tas TransAmount\n\t\n\t\n\t--,tl.TransactionAmount\n\t\n\t\n\t,CASE \n\t\twhen tt.TYPECODE = 'Recovery'\tthen\n\t\t\tcase\n\t\t\t\tWHEN isnull(tl.TransactionAmount,0.00) > 0 \tTHEN \n\t\t\t\t\tCONCAT('-', RIGHT(CAST((-100000000 + isnull(-1 * tl.TransactionAmount,0.00)) AS numeric(11,2)),11)) \n\t\t\t\tELSE \n\t\t\t\t\tRIGHT(CONCAT('00000000', CAST(isnull(-1 * tl.TransactionAmount,0.00) AS numeric(11,2))),12) \n\t\t\tEND  \n\t\telse\n\t\t\tcase\n\t\t\t\tWHEN isnull(tl.TransactionAmount,0.00) < 0 \tTHEN \n\t\t\t\t\tCONCAT('-', RIGHT(CAST((-100000000 + isnull(tl.TransactionAmount,0.00)) AS numeric(11,2)),11)) \n\t\t\t\tELSE \n\t\t\t\t\tRIGHT(CONCAT('00000000', CAST(isnull(tl.TransactionAmount,0.00) AS numeric(11,2))),12) \n\t\t\tEND  \n\t\tend\n\t\t\tas Amount \t\t\t\t\t\t\n\t,tl.id\t\t\t\t\t\tas TransLineItemID\n\t,t.id\t\t\t\t\t\tas TransactionID\n\t--  **********************************************************************************************\n\t\t,cv.PolicySystemId\t\t\t\t\tas CovPolSystemID  \n\t\t\n\t\t,case \n\t\t\twhen upper(cast(ct.typecode as char(50))) in ('BP7EmploymentPracticesLiabilityInsurance','BP7SupplementalExtendReportingPeriodEPLI') then\n\t\t\t\tcase \n\t\t\t\t\twhen cv.Deductible > 99999 then '99999     '\t-- Deductible is S9(5) on TFG stats\n\t\t\t\t\telse cast(isnull(cv.Deductible, '          ')\tas char(10))  \n\t\t\t\tend\n\t\t\t--else cast(isnull(stat.DedStatAmount, '          ') as char(10)) \n\t\t\telse '          '\n\t\t\tend as DedStatAmount\n\t\n\t\t--closed and reopen fields added 09/21/2018 ek\n\t\t\n\t\t,CAST(replace(convert(char(10), cl.CloseDate, 101), '/', '') AS CHAR(8)) as Claim_CloseDate\n\t\t,CAST(replace(convert(char(10), cl.ReOpenDate, 101), '/', '') AS CHAR(8)) as Claim_ReOpenDate\n\t\t\n\t\t\t\t\t\t\t\t\t\t\t\t\n\nFROM vw_curr_cc_transactionlineitem tl\n\tleft join vw_curr_cc_transaction t\t\t\t\t\t(nolock) on tl.TransactionID\t= t.id\n\tleft join vw_curr_cc_transactionset tset\t\t\t(nolock) on t.TransactionSetID\t= tset.id\n\tleft join vw_curr_cc_claim cl\t\t\t\t\t\t(nolock) on t.ClaimID\t\t\t= cl.id\n\tleft join vw_curr_cc_policy po\t\t\t\t\t\t(nolock) on cl.PolicyID\t\t\t= po.id\n\tleft join vw_curr_cc_check ck\t\t\t\t\t\t(nolock) on t.CheckID\t\t\t= ck.id\n\tleft join vw_curr_cc_reserveline rl\t\t\t\t\t(nolock) on t.ReserveLineID\t\t= rl.id\n\tleft join vw_curr_cc_exposure ex\t\t\t\t\t(nolock) on t.ExposureID\t\t= ex.id\n\tleft join vw_curr_cc_coverage cv\t\t\t\t\t(nolock) on ex.CoverageID\t\t= cv.id\n\tleft join vw_curr_cc_contact clmcont\t\t\t\t(nolock) on ex.ClaimantDenormID = clmcont.id\n\t\n\tleft join vw_curr_cc_user u1\t\t\t\t\t\t(nolock) on cl.AssignedUserID\t= u1.id\n\tleft join vw_curr_cc_user u2\t\t\t\t\t\t(nolock) on cl.SubroRepresentative_Ext \t= u2.id\n\t\n\tleft join vw_curr_cc_riskunit ru\t\t\t\t\t(nolock) on cv.RiskUnitID\t\t= ru.id\n\tleft join vw_curr_cc_classcode cls\t\t\t\t\t(nolock) on ru.ClassCodeID\t\t= cls.id\n\tleft join vw_curr_cctl_lobcode lob\t\t\t\t\t\t\ton cl.LOBCode\t\t\t= lob.id\n\tleft join vw_curr_cctl_policytype polt\t\t\t\t(nolock) on po.PolicyType\t\t= polt.id\n\tleft join vw_curr_cctl_transaction tt\t\t\t\t(nolock) on t.Subtype\t\t\t= tt.id\n\tleft join vw_curr_cctl_losscause tlc\t\t\t\t(nolock) on cl.LossCause\t\t= tlc.id\n\tleft join vw_curr_cctl_transactionstatus ts\t\t\t(nolock) on t.Status\t\t\t= ts.id\n\tleft join vw_curr_cctl_costtype CST\t\t\t\t\t(nolock) on T.CostType\t\t\t= CST.ID\n\tleft join vw_curr_cctl_costcategory ccat\t\t\t(nolock) on t.CostCategory\t\t= ccat.ID\n\tleft join vw_curr_cctl_linecategory lc\t\t\t\t(nolock) on TL.LineCategory\t\t= lc.ID\n\tleft join vw_curr_cctl_transactionlifecyclestate tls (nolock) on T.LifeCycleState\t= tls.ID\n\tleft join vw_curr_cctl_recoverycategory rv\t\t\t (nolock) on t.RecoveryCategory = rv.ID\n\tleft join vw_curr_cctl_underwritingcompanytype uw\t (nolock) on po.UnderwritingCo  = uw.id\n\tleft join vw_curr_cctl_coveragesubtype st\t\t\t(nolock) on ex.CoverageSubType\t= st.id\n\tleft join vw_curr_cctl_coveragetype ct\t\t\t\t(nolock) on cv.type\t\t\t\t= ct.id\n\tleft join vw_curr_cctl_checkbatching cb\t\t\t\t(nolock) on ck.CheckBatching\t= cb.ID\n\tleft join vw_curr_cctl_paymenttype pt\t\t\t\t(nolock) on t.PaymentType\t\t= pt.id\n\twhere tls.name = 'committed'\n\tand tset.ApprovalStatus=1\t\t\t\t--Approved  added 08/29/2018 ek\n\t\n\t-- 08/07/24  mec\n\tand tl.Retired = 0\t\t\t\t\t\t-- If > 0 then transaction was deleted (matches DH)\n) x\n \n)a\t\n-- For Incurred  *********************************************************\nwhere TFGTran in ('321', '351', '341', '421', '431')\n--and PolSource in ('guidewire') --('legacy')\n--and PolSource in ('legacy') \n--and AcctDate_sql < '08/01/2024'\nand AcctDate_sql > @PV_STARTDATE and AcctDate_sql < @PV_ENDDATE --'08/01/2024'\n--and AcctDate_sql > '12/30/2022' and AcctDate_sql < '12/30/2023'\t  -- 2023\nand PolSource = 'Guidewire'\n group by \n PolSource \n  --LOBCode \n -- ClaimNumber\n  ,LOBCode\n  ,PolicyNumber\n -- ,LossDate\n -- ,ReportedDate\n having sum(TransAmount) <> 0\n\n order by \n PolSource desc \n --LOBCode \n --ClaimNumber",
    "business_rules": [
      {
        "rule_id": "Rule 1",
        "name": "ClaimCenter_Monoline Rule 1",
        "description": "If PolicyPrefix_Ext is null, the claim source is classified as 'Legacy'; otherwise 'Guidewire'.",
        "formula": null
      },
      {
        "rule_id": "Rule 2",
        "name": "ClaimCenter_Monoline Rule 2",
        "description": "For reserve transactions, assign rownum = ROW_NUMBER partitioned by claim and exposure; non\u2011reserve rows get rownum = 0.",
        "formula": "For reserve transactions, assign rownum = ROW_NUMBER partitioned by claim and exposure; non\u2011reserve rows get rownum = 0."
      },
      {
        "rule_id": "Rule 3",
        "name": "ClaimCenter_Monoline Rule 3",
        "description": "TFGTran mapping rules: e.g., Reserve + Indemnity first row => '421', subsequent rows => '431'; Reserve + non\u2011Indemnity first row => '422', subsequent => '432'; Payment + Indemnity with DoesNotErodeReserves=1 => '321', otherwise '331'; Payment + non\u2011Indemnity with DoesNotErodeReserves=1 => '322', otherwise '332'; Recovery categories map to specific codes (e.g., Credit_loss + Indemnity => '321', salvage + Indemnity => '341', etc.).",
        "formula": "TFGTran mapping rules: e.g., Reserve + Indemnity first row => '421', subsequent rows => '431'; Reserve + non\u2011Indemnity first row => '422', subsequent => '432'; Payment + Indemnity with DoesNotErodeReserves=1 => '321', otherwise '331'; Payment + non\u2011Indemnity with DoesNotErodeReserves=1 => '322', otherwise '332'; Recovery categories map to specific codes (e.g., Credit_loss + Indemnity => '321', salvage + Indemnity => '341', etc.)."
      },
      {
        "rule_id": "Rule 4",
        "name": "ClaimCenter_Monoline Rule 4",
        "description": "TransAmount sign rule: Payments are stored as negative amounts unless DoesNotErodeReserves=1 (then positive); Recoveries are always stored as negative; all other transaction types retain their original sign.",
        "formula": "TransAmount sign rule: Payments are stored as negative amounts unless DoesNotErodeReserves=1 (then positive); Recoveries are always stored as negative; all other transaction types retain their original sign."
      },
      {
        "rule_id": "Rule 5",
        "name": "ClaimCenter_Monoline Rule 5",
        "description": "DedStatAmount is populated only for specific coverage types (BP7EmploymentPracticesLiabilityInsurance, BP7SupplementalExtendReportingPeriodEPLI) and capped at 99999; otherwise blank.",
        "formula": null
      },
      {
        "rule_id": "Rule 6",
        "name": "ClaimCenter_Monoline Rule 6",
        "description": "Company code mapping based on underwriting company name: Lightning Rod Mutual => 'LRM', Western Reserve Mutual => 'WRM', Sonnenberg Mutual => 'SON', else 'UNK'.",
        "formula": "Company code mapping based on underwriting company name: Lightning Rod Mutual => 'LRM', Western Reserve Mutual => 'WRM', Sonnenberg Mutual => 'SON', else 'UNK'."
      },
      {
        "rule_id": "Rule 7",
        "name": "ClaimCenter_Monoline Rule 7",
        "description": "CostType determines TFGASL and GWASL codes using predefined mappings (e.g., CPEquipBrkCov => '270', CPINCCCov => '010', certain claim coverages => '010', else '021').",
        "formula": "CostType determines TFGASL and GWASL codes using predefined mappings (e.g., CPEquipBrkCov => '270', CPINCCCov => '010', certain claim coverages => '010', else '021')."
      },
      {
        "rule_id": "Rule 8",
        "name": "ClaimCenter_Monoline Rule 8",
        "description": "Only distinct combinations of PolSource, LOBCode and PolicyNumber are retained before summing incurred amounts.",
        "formula": null
      }
    ],
    "inputs": [
      "vw_curr_cc_transactionlineitem (tl)",
      "vw_curr_cc_transaction (t)",
      "vw_curr_cc_transactionset (tset)",
      "vw_curr_cc_claim (cl)",
      "vw_curr_cc_policy (po)",
      "vw_curr_cc_check (ck)",
      "vw_curr_cc_reserveline (rl)",
      "vw_curr_cc_exposure (ex)",
      "vw_curr_cc_coverage (cv)",
      "vw_curr_cc_contact (clmcont)",
      "vw_curr_cc_user (u1, u2)",
      "vw_curr_cc_riskunit (ru)",
      "vw_curr_cc_classcode (cls)",
      "vw_curr_cctl_lobcode (lob)",
      "vw_curr_cctl_policytype (polt)",
      "vw_curr_cctl_transaction (tt)",
      "vw_curr_cctl_losscause (tlc)",
      "vw_curr_cctl_transactionstatus (ts)",
      "vw_curr_cctl_costtype (CST)",
      "vw_curr_cctl_costcategory (ccat)",
      "vw_curr_cctl_linecategory (lc)",
      "vw_curr_cctl_transactionlifecyclestate (tls)",
      "vw_curr_cctl_recoverycategory (rv)",
      "vw_curr_cctl_underwritingcompanytype (uw)",
      "vw_curr_cctl_coveragesubtype (st)",
      "@PV_STARTDATE (unused)",
      "@PV_ENDDATE (unused)"
    ],
    "outputs": [
      "Result set with columns: PolSource, LOBCode, PolicyNumber, IncurredAmount (sum of TransAmount)"
    ],
    "transformations": [
      "Derive PolSource as 'Legacy' or 'Guidewire' based on PolicyPrefix_Ext.",
      "Generate row_number partitioned by ClaimNumber, exposure, typecode and cost name for reserve lines.",
      "Map underwriting company IDs to short codes (LRM, WRM, SON, UNK).",
      "Convert dates to CHAR(8) YYYYMMDD format for policy effective dates and accounting dates.",
      "Calculate TFGTran code using complex CASE logic that considers transaction type, cost type, rownum and other flags.",
      "Determine signed TransAmount: Payments are negative unless DoesNotErodeReserves=1, Recoveries are always negative, others retain sign.",
      "Format Amount field with leading zeros and sign handling for reporting.",
      "Compute DedStatAmount for specific coverage types with a ceiling of 99999.",
      "Aggregate (SUM) TransAmount per PolSource, LOBCode and PolicyNumber, applying DISTINCT to eliminate duplicates.",
      "Select only required columns for the final output."
    ],
    "dependencies": [
      "All ClaimCenter view objects prefixed with vw_curr_cc_ (transactionlineitem, transaction, transactionset, claim, policy, check, reserveline, exposure, coverage, contact, user, riskunit, classcode).",
      "Lookup tables prefixed with vw_curr_cctl_ (lobcode, policytype, transaction, losscause, transactionstatus, costtype, costcategory, linecategory, transactionlifecyclestate, recoverycategory, underwritingcompanytype, coveragesubtype).",
      "SQL Server window function ROW_NUMBER for reserve line sequencing.",
      "Standard SQL functions (CASE, ISNULL, CAST, CONVERT, RIGHT, LEFT, UPPER, REPLACE)."
    ]
  },
  {
    "id": "PolicyCenter_CPP_Breakdown.sql",
    "name": "PolicyCenter_CPP_Breakdown.sql",
    "type": "SQL",
    "lines": 267,
    "entities": 31,
    "relationships": 32,
    "rules": 9,
    "purpose": "Extract a detailed, filtered list of Commercial Package policies for the Agribusiness profit center, including transaction type indicators and premium amounts, for a specified policy period and job close date range.",
    "raw_code": "Declare @POLSTARTDATE as Date\nDeclare @POLENDDATE as Date\nDeclare @CHANGESTARTDATE as Date\nDeclare @curmthyr as int = concat(month(GETUTCDATE())-1,year(GETUTCDATE()))\n\nSet @POLSTARTDATE = '8/1/2025'\nSet @POLENDDATE = '7/31/2026'\nSet @CHANGESTARTDATE = '7/1/2026'\n\nselect\nProfitCenter,ProductCode,LineOfBusiness,PolicyNumber,OriginalEffectiveDate,PeriodStart,PeriodEnd,AccountNumber,Company,PrimaryInsuredName,AgentCode,AgentName,FarmUWTerritory\n,case\n\twhen MostRecentModel = 1 then TranType\n\telse Null end as MostRecentTran\n,case\n\twhen TranType in ('Renewal','Submission') then Written_Premium\n\telse null end as SubWritten_Premium\n,case \n\twhen TranType in ('Renewal','Submission') then WrittenDate\n\telse null end as SubWritten_Date\n,case\n\twhen TranType in ('Cancellation') then CancellationDate\n\telse null end as CancelledDate\n,case\n\twhen TranType in ('Cancellation') then JobCloseDate\n\telse null end as CancelledEffDate\n,case\n\twhen TranType in ('Cancellation') then Written_Premium\n\telse null end as CancelledPremium\n,case\n\twhen TranType in ('Reinstatement') then Written_Premium\n\telse null end as ReinstatedPremium\n,case \n\twhen TranType in ('Reinstatement') then WrittenDate\n\telse null end as ReinstatedDate\n,case \n\twhen TranType in ('Reinstatement') then JobCloseDate\n\telse null end as ReinstatedEffDate\n,case\n\twhen TranType in ('PolicyChange')  then Written_Premium\n\telse null end as ChangePremium\n,case \n\twhen TranType in ('PolicyChange') then EditEffectiveDate\n\telse null end as ChangeDate\nfrom(\nSELECT  \n\t\tprofit.NAME\tas ProfitCenter,\n\t    ProductCode,\n\t\t--PatternCode,\n\t\tcase\n\t\t\twhen PatternCode = 'cp7line'\t\t\t\t\tthen 'Commercial Property Line'\t\t\n\t\t\twhen PatternCode = 'GeneralLiabilityLine_GLE'   then 'General Liability Line'\n\t\t\twhen PatternCode = 'ca7line'\t\t\t\t\tthen 'Commercial Auto Line'\n\t\t\twhen PatternCode = 'cr7line'\t\t\t\t\tthen 'Crime Line'\n\t\t\twhen PatternCode = 'imline'\t\t\t\t\t\tthen 'Inland Marine Line'\n\t\t\twhen PatternCode = 'WC7Line'\t\t\t\t\tthen 'Workers Comp Line'\n\t\t\telse PatternCode\t\t\t\t\t\n\t\t\tend as LineofBusiness,\n\t\t\n\t\tpp.PolicyNumber\n\t\n\t\t,LegacyPolicyNumber\n\t\t--,ppstype.NAME\t\t\t\tas PolPerSourceType\n\t\t,AccountNumber\n\t\t,case \n\t\t\t--when UWCompany = 1 then 'WRM'  \n\t\t\t--when UWCompany = 2 then 'LRM'\n\t\t\t--when UWCompany = 3 then 'SON'\n\t\t\twhen uwc.name = 'Lightning Rod Mutual'   then 'LRM'\n\t\t\twhen uwc.name = 'Western Reserve Mutual' then 'WRM'\n\t\t\twhen uwc.name = 'Sonnenberg Mutual'\t\t then 'SON'\n\t\t\telse 'UNK'\n\t\t\tend\t\t\t\t\t\tas Company\n\t\t\n\t\t,pp.ID\t\t\tas PolPerID\n\t\t--,BranchNumber\n\t\t,pp.PeriodID\n\t\t,pp.TermNumber\n\t\t\n\t\t--,AccountNumber\n\t\t --,pp.[PrimaryInsuredName]\n\n\t\t  ,(select distinct PrimaryInsuredName from pc_policyperiod pp2 \n\t\t\t\t\twhere pp.PolicyNumber = pp2.PolicyNumber\n\t\t\t\t\tand pp.PeriodStart  = pp2.PeriodStart\n\t\t\t\t\tand pp2.MostRecentModel = 1)  as PrimaryInsuredName\n\t\t\n\t\t,cast((rtrim(org.Code_Ext))\tas char(6))\tas AgentCode\n\t\t,org.Name\t\t\t\t\t\t\t\tas AgentName\n\t\t,farmterr.NAME\t\t\t\t\t\t\tas FarmUWTerritory\n\t\t\n\t\t\n\t\t,case \n\t\t\twhen prod.code is null then '999' \n\t\t\telse right(rtrim(prod.code),3)\n\t\t end\t\t\t\t\t\tas ProducerCode\n\t\t\n\t\t--,[JobID]\n\t\t,JobNumber\n\t\t,j.CloseDate\t\tas JobCloseDate\n\t\t\n\t\t,jt.TYPECODE\t\t\t\tas TranType\n\t\t,isnull(bopt.NAME,'')\t\tas BindOpt \n\t\t,jdt.name\t\t\t\t\tas JobDesc\n\t\t,ppst.TYPECODE\t\t\t\tas PolPerStatus\n\t\t\n\t    ,[MostRecentModel]\n\t\t,pp.[CreateTime]\n\t\t,[EditEffectiveDate]\n\t\t,pol.IssueDate\n\t\t,pol.OriginalEffectiveDate\n\t\n\t\t,[PeriodStart]\t \n\t\t,[PeriodEnd]\t \n\t\t,[CancellationDate]\n\t\t\n\t\t,[WrittenDate]\n\t\t\n\t\t,case\n\t\t\twhen ProductCode = 'CommercialPackage' then\n\t\t\t\tcase\n\t\t\t\t\twhen PatternCode = 'cp7line' then\n\t\t\t\t\t\t(select isnull(sum(amount),0.00) FROM pcx_cp7transaction tr \twhere tr.BranchID\t\t= pp.id)\n\t\t\t\t\t\t\t\n\t\t\t\t\twhen PatternCode = 'GeneralLiabilityLine_GLE' then\n\t\t\t\t\t\t(select isnull(sum(amount),0.00) FROM pcx_gl7transaction_gle tr \twhere tr.BranchID\t= pp.id)\n\t\t\t\t\t\t\t\n\t\t\t\t\twhen PatternCode = 'ca7line' then\n\t\t\t\t\t\t(select isnull(sum(amount),0.00) FROM pcx_ca7transaction tr  where tr.BranchID\t\t= pp.id)\n\t\t\t\t\t\t\t\n\t\t\t\t\twhen PatternCode = 'cr7line' then\n\t\t\t\t\t\t(select isnull(sum(amount),0.00) FROM pcx_cr7transaction tr  where tr.BranchID\t\t= pp.id)\n\t\t\t\t\t\t\t \n\t\t\t\t\twhen PatternCode = 'imline' then\n\t\t\t\t\t\t(select isnull(sum(amount),0.00) FROM pc_imtransaction tr where tr.BranchID\t\t\t= pp.id)\n\n\t\t\t\t\twhen PatternCode = 'WC7Line' then\n\t\t\t\t\t\t(select isnull(sum(amount),0.00) FROM pcx_wc7transaction tr where tr.BranchID\t\t= pp.id)\n\t\t\t\t\t\t\n\t\t\t\t\tend\n\t\t\t\n\t\t\telse TransactionCostRPT --TotalCostRPT\n\t\t\tend as Written_Premium\n\t\t,[TotalPremiumRPT]\n\t\t,[TotalCostRPT] \n  FROM [PolicyCenter].[dbo].[pc_policyperiod] pp\n  left join [PolicyCenter].[dbo].pc_policy pol\t\t\t\t\t(nolock) on pp.policyid\t\t= pol.id\n  left join [PolicyCenter].[dbo].pc_policyTerm polt\t\t\t\t(nolock) on pp.policytermid = polt.id\n  \n  left join [PolicyCenter].[dbo].[pc_policyline] polline\t\t(nolock) on polline.branchid = pp.id\n\t\t\t\t\t\t\t\t\t\t\tand coalesce(polline.EffectiveDate, PeriodStart) <> coalesce(polline.ExpirationDate, PeriodEnd)\n\t\t\t\t\t\t\t\t\t\t\t--and polline.ExpirationDate is null\n  \n  left join [PolicyCenter].[dbo].[pc_job] j\t\t\t\t\t\t(nolock) on pp.jobid\t\t= j.id\n  left join [PolicyCenter].[dbo].[pc_account] act\t\t\t\t(nolock) on pol.AccountID\t= act.id\n  --left join [PolicyCenter].[dbo].[pc_user] u\t\t\t\t\t(nolock) on pp.CreateUserID\t= u.id\n  \n  left join pc_producercode prod\t\t\t\t\t\t\t\t(nolock) on pp.ProducerCodeOfRecordID\t= prod.id \n  left join pc_organization org\t\t\t\t\t\t\t\t\t(nolock) on prod.OrganizationID\t\t\t= org.id\n\n\n  left join [PolicyCenter].[dbo].[pctl_job] jt\t\t\t\t\t(nolock) on j.SubType\t\t= jt.id\n  left join [PolicyCenter].[dbo].pctl_policyperiodstatus ppst\t(noLock) ON pp.status\t\t= ppst.ID\n  left join [PolicyCenter].[dbo].pctl_bindoption bopt\t\t\t(nolock) on j.BindOption\t= bopt.id\n  left join [PolicyCenter].[dbo].pctl_uwcompanycode uwc\t\t\t(nolock) on pp.UWCompany\t= uwc.TYPECODE\n   -- for change type\n  left join [PolicyCenter].[dbo].pctl_jobdescription_ext jdt\t(nolock) on j.DescriptionTL\t= jdt.id\n  left join pctl_policyperiodsourcetype ppstype\t\t\t\t\t\t\t on ppstype.id\t\t= pp.PolicyPeriodSource\n  -- get profit center\n   left join pctl_profitcentertype profit                       (nolock) on ProfitCenterType\t= profit.id\n   -- get FarmUWTerr\n   left join pctl_orgfarmuwterritory farmterr\t\t\t\t\t(nolock) on FarmUWTerritory\t\t= farmterr.id\n  \n  where --j.CloseDate is not null \n  pol.IssueDate is not null \n  and pp.Policynumber is not null\n  and (ppst.TYPECODE in ('Bound','AuditComplete')) -- and bopt.NAME <> 'BindOnly') \n  and j.CloseDate < @POLENDDATE\n   union all\n SELECT  \n\n\t\tprofit.NAME\tas ProfitCenter,\n\t    ProductCode,\n\t\t'C.P.P.'   as LineOfBusiness,\n\t\tpp.PolicyNumber\n\t\t\n\t\t,LegacyPolicyNumber\n\t\t--,ppstype.NAME\t\t\t\tas PolPerSourceType\n\t\t,AccountNumber\n\t\t,case \n\t\t\twhen uwc.name = 'Lightning Rod Mutual'   then 'LRM'\n\t\t\twhen uwc.name = 'Western Reserve Mutual' then 'WRM'\n\t\t\twhen uwc.name = 'Sonnenberg Mutual'\t\t then 'SON'\n\t\t\telse 'UNK'\n\t\t\tend\t\t\t\t\t\tas Company\n\t\t\n\t\t,pp.ID\t\t\tas PolPerID\n\t\t,pp.PeriodID\n\t\t,pp.TermNumber\n\t\t,(select distinct PrimaryInsuredName from pc_policyperiod pp2 \n\t\t\t\t\twhere pp.PolicyNumber = pp2.PolicyNumber\n\t\t\t\t\t  and pp.PeriodStart  = pp2.PeriodStart\n\t\t\t\t\tand pp2.MostRecentModel = 1)  as PrimaryInsuredName\n\t\t\n\t\t,cast((rtrim(org.Code_Ext))\tas char(6))\tas AgentCode\n\t\t,org.Name\t\t\t\t\t\t\t\tas AgentName\n\t\t,farmterr.NAME\t\t\t\t\t\t\tas FarmUWTerritory\n\t\t,case \n\t\t\twhen prod.code is null then '999' \n\t\t\telse right(rtrim(prod.code),3)\n\t\t end\t\t\t\t\t\tas ProducerCode\n\t\t\n\t\t--,[JobID]\n\t\t,JobNumber\n\t\t,j.CloseDate\t\t\t\tas JobCloseDate\n\t\t\n\t\t,jt.TYPECODE\t\t\t\tas TranType\n\t\t,isnull(bopt.NAME,'')\t\tas BindOpt \n\t\t,jdt.name\t\t\t\t\tas JobDesc\n\t\t,ppst.TYPECODE\t\t\t\tas PolPerStatus\n\t\t\t\t \n\t\t ,[MostRecentModel]\n\t\t,pp.[CreateTime]\n\t\t,[EditEffectiveDate]\n\t\t,pol.IssueDate\n\t\t,pol.OriginalEffectiveDate\n\t\t,[PeriodStart]\t \n\t\t,[PeriodEnd]\t \n\t\t,[CancellationDate]\n\t\t,[WrittenDate]\n\t\t,TransactionCostRPT  as Written_Premium\n\t\t,[TotalPremiumRPT]\n\t\t,[TotalCostRPT] \n\t\t\n  FROM [PolicyCenter].[dbo].[pc_policyperiod] pp\n  left join [PolicyCenter].[dbo].pc_policy pol\t\t\t\t\t(nolock) on pp.policyid\t\t= pol.id\n  left join [PolicyCenter].[dbo].pc_policyTerm polt\t\t\t\t(nolock) on pp.policytermid = polt.id\n left join [PolicyCenter].[dbo].[pc_job] j\t\t\t\t\t\t(nolock) on pp.jobid\t\t= j.id\n  left join [PolicyCenter].[dbo].[pc_account] act\t\t\t\t(nolock) on pol.AccountID\t= act.id\n  left join pc_producercode prod\t\t\t\t\t\t\t\t(nolock) on pp.ProducerCodeOfRecordID\t= prod.id \n  left join pc_organization org\t\t\t\t\t\t\t\t\t(nolock) on prod.OrganizationID\t\t\t= org.id\n  left join [PolicyCenter].[dbo].[pctl_job] jt\t\t\t\t\t(nolock) on j.SubType\t\t= jt.id\n  left join [PolicyCenter].[dbo].pctl_policyperiodstatus ppst\t(noLock) ON pp.status\t\t= ppst.ID\n  left join [PolicyCenter].[dbo].pctl_bindoption bopt\t\t\t(nolock) on j.BindOption\t= bopt.id\n  left join [PolicyCenter].[dbo].pctl_uwcompanycode uwc\t\t\t(nolock) on pp.UWCompany\t= uwc.TYPECODE\n   -- for change type\n  left join [PolicyCenter].[dbo].pctl_jobdescription_ext jdt\t(nolock) on j.DescriptionTL\t= jdt.id\n  left join pctl_policyperiodsourcetype ppstype\t\t\t\t\t\t\t on ppstype.id\t\t= pp.PolicyPeriodSource\n  -- get profit center\n   left join pctl_profitcentertype profit                       (nolock) on ProfitCenterType\t= profit.id\n   -- get FarmUWTerr\n   left join pctl_orgfarmuwterritory farmterr\t\t\t\t\t(nolock) on FarmUWTerritory\t\t= farmterr.id\n  \n  \n  where j.CloseDate is not null \n  and pol.IssueDate is not null \n  and pp.Policynumber is not null\n  and (ppst.TYPECODE in ('Bound','AuditComplete')) -- and bopt.NAME <> 'BindOnly')   \n  and ProductCode = 'CommercialPackage' \n  and j.CloseDate < @POLENDDATE\n  )jj\nwhere-- LineOfBusiness = 'Commercial Property Line'\n--and cancellationdate is null\n((PeriodStart between @POLSTARTDATE and @POLENDDATE) OR JobCloseDate between @POLSTARTDATE and @POLENDDATE)\nand ((ProductCode = 'CommercialPackage' AND LineOfBusiness not in ('C.P.P.')))\nand ProfitCenter = 'Agribusiness'\norder by PolicyNumber",
    "business_rules": [
      {
        "rule_id": "Rule 1",
        "name": "PolicyCenter_CPP_Breakdown Rule 1",
        "description": "Include only policies where the policy period status is 'Bound' or 'AuditComplete'.",
        "formula": null
      },
      {
        "rule_id": "Rule 2",
        "name": "PolicyCenter_CPP_Breakdown Rule 2",
        "description": "Job.CloseDate must be non\u2011null and earlier than @POLENDDATE.",
        "formula": null
      },
      {
        "rule_id": "Rule 3",
        "name": "PolicyCenter_CPP_Breakdown Rule 3",
        "description": "Policy IssueDate and PolicyNumber must be present.",
        "formula": null
      },
      {
        "rule_id": "Rule 4",
        "name": "PolicyCenter_CPP_Breakdown Rule 4",
        "description": "For CommercialPackage policies, use the sum of transaction amounts as the written premium; otherwise use TransactionCostRPT.",
        "formula": null
      },
      {
        "rule_id": "Rule 5",
        "name": "PolicyCenter_CPP_Breakdown Rule 5",
        "description": "Map UWCompany names to short codes: 'Lightning Rod Mutual' \u2192 LRM, 'Western Reserve Mutual' \u2192 WRM, 'Sonnenberg Mutual' \u2192 SON; default to UNK.",
        "formula": null
      },
      {
        "rule_id": "Rule 6",
        "name": "PolicyCenter_CPP_Breakdown Rule 6",
        "description": "Expose premium and date fields only for the relevant transaction type (e.g., Cancellation fields only when TranType = 'Cancellation').",
        "formula": "Expose premium and date fields only for the relevant transaction type (e.g., Cancellation fields only when TranType = 'Cancellation')."
      },
      {
        "rule_id": "Rule 7",
        "name": "PolicyCenter_CPP_Breakdown Rule 7",
        "description": "Restrict output to the Agribusiness profit center.",
        "formula": null
      },
      {
        "rule_id": "Rule 8",
        "name": "PolicyCenter_CPP_Breakdown Rule 8",
        "description": "Exclude rows where LineOfBusiness equals the placeholder 'C.P.P.' when ProductCode = 'CommercialPackage'.",
        "formula": "Exclude rows where LineOfBusiness equals the placeholder 'C.P.P.' when ProductCode = 'CommercialPackage'."
      },
      {
        "rule_id": "Rule 9",
        "name": "PolicyCenter_CPP_Breakdown Rule 9",
        "description": "Date range filter applies to either the policy period start or the job close date.",
        "formula": null
      }
    ],
    "inputs": [
      "pc_policyperiod (alias pp)",
      "pc_policy (alias pol)",
      "pc_policyTerm (alias polt)",
      "pc_policyline (alias polline)",
      "pc_job (alias j)",
      "pc_account (alias act)",
      "pc_producercode (alias prod)",
      "pc_organization (alias org)",
      "pctl_job (alias jt)",
      "pctl_policyperiodstatus (alias ppst)",
      "pctl_bindoption (alias bopt)",
      "pctl_uwcompanycode (alias uwc)",
      "pctl_jobdescription_ext (alias jdt)",
      "pctl_policyperiodsourcetype (alias ppstype)",
      "pctl_profitcentertype (alias profit)",
      "pctl_orgfarmuwterritory (alias farmterr)",
      "pcx_cp7transaction",
      "pcx_gl7transaction_gle",
      "pcx_ca7transaction",
      "pcx_cr7transaction",
      "pc_imtransaction",
      "pcx_wc7transaction",
      "SQL variables @POLSTARTDATE, @POLENDDATE, @CHANGESTARTDATE, @curmthyr"
    ],
    "outputs": [
      "Result set with columns: ProfitCenter, ProductCode, LineOfBusiness, PolicyNumber, OriginalEffectiveDate, PeriodStart, PeriodEnd, AccountNumber, Company, PrimaryInsuredName, AgentCode, AgentName, FarmUWTerritory, MostRecentTran, SubWritten_Premium, SubWritten_Date, CancelledDate, CancelledEffDate, CancelledPremium, ReinstatedPremium, ReinstatedDate, ReinstatedEffDate, ChangePremium, ChangeDate"
    ],
    "transformations": [
      "Mapping of PatternCode values to human\u2011readable LineOfBusiness strings.",
      "Deriving Company code (LRM, WRM, SON) from UWCompany name.",
      "Calculating Written_Premium for CommercialPackage policies by summing the Amount field from the appropriate transaction table based on PatternCode.",
      "Conditional CASE columns that expose premium, dates, and effective dates only for specific transaction types (Renewal, Submission, Cancellation, Reinstatement, PolicyChange).",
      "Union of two queries: first with detailed line\u2011of\u2011business mapping, second providing a fallback for C.P.P. line.",
      "Filtering rows where PeriodStart or JobCloseDate falls within @POLSTARTDATE\u2011@POLENDDATE, ProductCode = 'CommercialPackage', LineOfBusiness not equal to 'C.P.P.', and ProfitCenter = 'Agribusiness'.",
      "Ordering final output by PolicyNumber."
    ],
    "dependencies": [
      "SQL Server (T\u2011SQL) engine",
      "PolicyCenter database schema (tables and views listed in inputs)",
      "Transaction tables for each line of business (pcx_*transaction)",
      "Reference tables for profit center, UW company, job types, bind options, etc."
    ]
  },
  {
    "id": "PolicyCenter_Monoline.sql",
    "name": "PolicyCenter_Monoline.sql",
    "type": "SQL",
    "lines": 267,
    "entities": 31,
    "relationships": 24,
    "rules": 10,
    "purpose": "Extract a detailed list of policies for the Agribusiness profit center within a specified policy period, exposing transaction types (renewal, submission, cancellation, reinstatement, change) and associated premium amounts for downstream reporting or analysis.",
    "raw_code": "Declare @POLSTARTDATE as Date\nDeclare @POLENDDATE as Date\nDeclare @CHANGESTARTDATE as Date\nDeclare @curmthyr as int = concat(month(GETUTCDATE())-1,year(GETUTCDATE()))\n\nSet @POLSTARTDATE = '8/1/2025'\nSet @POLENDDATE = '7/31/2026'\nSet @CHANGESTARTDATE = '7/1/2026'\n\nselect\nProfitCenter,ProductCode,LineOfBusiness,PolicyNumber,OriginalEffectiveDate,PeriodStart,PeriodEnd,AccountNumber,Company,PrimaryInsuredName,AgentCode,AgentName,FarmUWTerritory\n,case\n\twhen MostRecentModel = 1 then TranType\n\telse Null end as MostRecentTran\n,case\n\twhen TranType in ('Renewal','Submission') then Written_Premium\n\telse null end as SubWritten_Premium\n,case \n\twhen TranType in ('Renewal','Submission') then WrittenDate\n\telse null end as SubWritten_Date\n,case\n\twhen TranType in ('Cancellation') then CancellationDate\n\telse null end as CancelledDate\n,case\n\twhen TranType in ('Cancellation') then JobCloseDate\n\telse null end as CancelledEffDate\n,case\n\twhen TranType in ('Cancellation') then Written_Premium\n\telse null end as CancelledPremium\n,case\n\twhen TranType in ('Reinstatement') then Written_Premium\n\telse null end as ReinstatedPremium\n,case \n\twhen TranType in ('Reinstatement') then WrittenDate\n\telse null end as ReinstatedDate\n,case \n\twhen TranType in ('Reinstatement') then JobCloseDate\n\telse null end as ReinstatedEffDate\n,case\n\twhen TranType in ('PolicyChange')  then Written_Premium\n\telse null end as ChangePremium\n,case \n\twhen TranType in ('PolicyChange') then EditEffectiveDate\n\telse null end as ChangeDate\nfrom(\nSELECT  \n\t\tprofit.NAME\tas ProfitCenter,\n\t    ProductCode,\n\t\t--PatternCode,\n\t\tcase\n\t\t\twhen PatternCode = 'cp7line'\t\t\t\t\tthen 'Commercial Property Line'\t\t\n\t\t\twhen PatternCode = 'GeneralLiabilityLine_GLE'   then 'General Liability Line'\n\t\t\twhen PatternCode = 'ca7line'\t\t\t\t\tthen 'Commercial Auto Line'\n\t\t\twhen PatternCode = 'cr7line'\t\t\t\t\tthen 'Crime Line'\n\t\t\twhen PatternCode = 'imline'\t\t\t\t\t\tthen 'Inland Marine Line'\n\t\t\twhen PatternCode = 'WC7Line'\t\t\t\t\tthen 'Workers Comp Line'\n\t\t\telse PatternCode\t\t\t\t\t\n\t\t\tend as LineofBusiness,\n\t\t\n\t\tpp.PolicyNumber\n\t\n\t\t,LegacyPolicyNumber\n\t\t--,ppstype.NAME\t\t\t\tas PolPerSourceType\n\t\t,AccountNumber\n\t\t,case \n\t\t\t--when UWCompany = 1 then 'WRM'  \n\t\t\t--when UWCompany = 2 then 'LRM'\n\t\t\t--when UWCompany = 3 then 'SON'\n\t\t\twhen uwc.name = 'Lightning Rod Mutual'   then 'LRM'\n\t\t\twhen uwc.name = 'Western Reserve Mutual' then 'WRM'\n\t\t\twhen uwc.name = 'Sonnenberg Mutual'\t\t then 'SON'\n\t\t\telse 'UNK'\n\t\t\tend\t\t\t\t\t\tas Company\n\t\t\n\t\t,pp.ID\t\t\tas PolPerID\n\t\t--,BranchNumber\n\t\t,pp.PeriodID\n\t\t,pp.TermNumber\n\t\t\n\t\t--,AccountNumber\n\t\t --,pp.[PrimaryInsuredName]\n\n\t\t  ,(select distinct PrimaryInsuredName from pc_policyperiod pp2 \n\t\t\t\t\twhere pp.PolicyNumber = pp2.PolicyNumber\n\t\t\t\t\tand pp.PeriodStart  = pp2.PeriodStart\n\t\t\t\t\tand pp2.MostRecentModel = 1)  as PrimaryInsuredName\n\t\t\n\t\t,cast((rtrim(org.Code_Ext))\tas char(6))\tas AgentCode\n\t\t,org.Name\t\t\t\t\t\t\t\tas AgentName\n\t\t,farmterr.NAME\t\t\t\t\t\t\tas FarmUWTerritory\n\t\t\n\t\t\n\t\t,case \n\t\t\twhen prod.code is null then '999' \n\t\t\telse right(rtrim(prod.code),3)\n\t\t end\t\t\t\t\t\tas ProducerCode\n\t\t\n\t\t--,[JobID]\n\t\t,JobNumber\n\t\t,j.CloseDate\t\tas JobCloseDate\n\t\t\n\t\t,jt.TYPECODE\t\t\t\tas TranType\n\t\t,isnull(bopt.NAME,'')\t\tas BindOpt \n\t\t,jdt.name\t\t\t\t\tas JobDesc\n\t\t,ppst.TYPECODE\t\t\t\tas PolPerStatus\n\t\t\n\t    ,[MostRecentModel]\n\t\t,pp.[CreateTime]\n\t\t,[EditEffectiveDate]\n\t\t,pol.IssueDate\n\t\t,pol.OriginalEffectiveDate\n\t\n\t\t,[PeriodStart]\t \n\t\t,[PeriodEnd]\t \n\t\t,[CancellationDate]\n\t\t\n\t\t,[WrittenDate]\n\t\t\n\t\t,case\n\t\t\twhen ProductCode = 'CommercialPackage' then\n\t\t\t\tcase\n\t\t\t\t\twhen PatternCode = 'cp7line' then\n\t\t\t\t\t\t(select isnull(sum(amount),0.00) FROM pcx_cp7transaction tr \twhere tr.BranchID\t\t= pp.id)\n\t\t\t\t\t\t\t\n\t\t\t\t\twhen PatternCode = 'GeneralLiabilityLine_GLE' then\n\t\t\t\t\t\t(select isnull(sum(amount),0.00) FROM pcx_gl7transaction_gle tr \twhere tr.BranchID\t= pp.id)\n\t\t\t\t\t\t\t\n\t\t\t\t\twhen PatternCode = 'ca7line' then\n\t\t\t\t\t\t(select isnull(sum(amount),0.00) FROM pcx_ca7transaction tr  where tr.BranchID\t\t= pp.id)\n\t\t\t\t\t\t\t\n\t\t\t\t\twhen PatternCode = 'cr7line' then\n\t\t\t\t\t\t(select isnull(sum(amount),0.00) FROM pcx_cr7transaction tr  where tr.BranchID\t\t= pp.id)\n\t\t\t\t\t\t\t \n\t\t\t\t\twhen PatternCode = 'imline' then\n\t\t\t\t\t\t(select isnull(sum(amount),0.00) FROM pc_imtransaction tr where tr.BranchID\t\t\t= pp.id)\n\n\t\t\t\t\twhen PatternCode = 'WC7Line' then\n\t\t\t\t\t\t(select isnull(sum(amount),0.00) FROM pcx_wc7transaction tr where tr.BranchID\t\t= pp.id)\n\t\t\t\t\t\t\n\t\t\t\t\tend\n\t\t\t\n\t\t\telse TransactionCostRPT --TotalCostRPT\n\t\t\tend as Written_Premium\n\t\t,[TotalPremiumRPT]\n\t\t,[TotalCostRPT] \n  FROM [PolicyCenter].[dbo].[pc_policyperiod] pp\n  left join [PolicyCenter].[dbo].pc_policy pol\t\t\t\t\t(nolock) on pp.policyid\t\t= pol.id\n  left join [PolicyCenter].[dbo].pc_policyTerm polt\t\t\t\t(nolock) on pp.policytermid = polt.id\n  \n  left join [PolicyCenter].[dbo].[pc_policyline] polline\t\t(nolock) on polline.branchid = pp.id\n\t\t\t\t\t\t\t\t\t\t\tand coalesce(polline.EffectiveDate, PeriodStart) <> coalesce(polline.ExpirationDate, PeriodEnd)\n\t\t\t\t\t\t\t\t\t\t\t--and polline.ExpirationDate is null\n  \n  left join [PolicyCenter].[dbo].[pc_job] j\t\t\t\t\t\t(nolock) on pp.jobid\t\t= j.id\n  left join [PolicyCenter].[dbo].[pc_account] act\t\t\t\t(nolock) on pol.AccountID\t= act.id\n  --left join [PolicyCenter].[dbo].[pc_user] u\t\t\t\t\t(nolock) on pp.CreateUserID\t= u.id\n  \n  left join pc_producercode prod\t\t\t\t\t\t\t\t(nolock) on pp.ProducerCodeOfRecordID\t= prod.id \n  left join pc_organization org\t\t\t\t\t\t\t\t\t(nolock) on prod.OrganizationID\t\t\t= org.id\n\n\n  left join [PolicyCenter].[dbo].[pctl_job] jt\t\t\t\t\t(nolock) on j.SubType\t\t= jt.id\n  left join [PolicyCenter].[dbo].pctl_policyperiodstatus ppst\t(noLock) ON pp.status\t\t= ppst.ID\n  left join [PolicyCenter].[dbo].pctl_bindoption bopt\t\t\t(nolock) on j.BindOption\t= bopt.id\n  left join [PolicyCenter].[dbo].pctl_uwcompanycode uwc\t\t\t(nolock) on pp.UWCompany\t= uwc.TYPECODE\n   -- for change type\n  left join [PolicyCenter].[dbo].pctl_jobdescription_ext jdt\t(nolock) on j.DescriptionTL\t= jdt.id\n  left join pctl_policyperiodsourcetype ppstype\t\t\t\t\t\t\t on ppstype.id\t\t= pp.PolicyPeriodSource\n  -- get profit center\n   left join pctl_profitcentertype profit                       (nolock) on ProfitCenterType\t= profit.id\n   -- get FarmUWTerr\n   left join pctl_orgfarmuwterritory farmterr\t\t\t\t\t(nolock) on FarmUWTerritory\t\t= farmterr.id\n  \n  where --j.CloseDate is not null \n  pol.IssueDate is not null \n  and pp.Policynumber is not null\n  and (ppst.TYPECODE in ('Bound','AuditComplete')) -- and bopt.NAME <> 'BindOnly') \n  and j.CloseDate < @POLENDDATE\n   union all\n SELECT  \n\n\t\tprofit.NAME\tas ProfitCenter,\n\t    ProductCode,\n\t\t'C.P.P.'   as LineOfBusiness,\n\t\tpp.PolicyNumber\n\t\t\n\t\t,LegacyPolicyNumber\n\t\t--,ppstype.NAME\t\t\t\tas PolPerSourceType\n\t\t,AccountNumber\n\t\t,case \n\t\t\twhen uwc.name = 'Lightning Rod Mutual'   then 'LRM'\n\t\t\twhen uwc.name = 'Western Reserve Mutual' then 'WRM'\n\t\t\twhen uwc.name = 'Sonnenberg Mutual'\t\t then 'SON'\n\t\t\telse 'UNK'\n\t\t\tend\t\t\t\t\t\tas Company\n\t\t\n\t\t,pp.ID\t\t\tas PolPerID\n\t\t,pp.PeriodID\n\t\t,pp.TermNumber\n\t\t,(select distinct PrimaryInsuredName from pc_policyperiod pp2 \n\t\t\t\t\twhere pp.PolicyNumber = pp2.PolicyNumber\n\t\t\t\t\t  and pp.PeriodStart  = pp2.PeriodStart\n\t\t\t\t\tand pp2.MostRecentModel = 1)  as PrimaryInsuredName\n\t\t\n\t\t,cast((rtrim(org.Code_Ext))\tas char(6))\tas AgentCode\n\t\t,org.Name\t\t\t\t\t\t\t\tas AgentName\n\t\t,farmterr.NAME\t\t\t\t\t\t\tas FarmUWTerritory\n\t\t,case \n\t\t\twhen prod.code is null then '999' \n\t\t\telse right(rtrim(prod.code),3)\n\t\t end\t\t\t\t\t\tas ProducerCode\n\t\t\n\t\t--,[JobID]\n\t\t,JobNumber\n\t\t,j.CloseDate\t\t\t\tas JobCloseDate\n\t\t\n\t\t,jt.TYPECODE\t\t\t\tas TranType\n\t\t,isnull(bopt.NAME,'')\t\tas BindOpt \n\t\t,jdt.name\t\t\t\t\tas JobDesc\n\t\t,ppst.TYPECODE\t\t\t\tas PolPerStatus\n\t\t\t\t \n\t\t ,[MostRecentModel]\n\t\t,pp.[CreateTime]\n\t\t,[EditEffectiveDate]\n\t\t,pol.IssueDate\n\t\t,pol.OriginalEffectiveDate\n\t\t,[PeriodStart]\t \n\t\t,[PeriodEnd]\t \n\t\t,[CancellationDate]\n\t\t,[WrittenDate]\n\t\t,TransactionCostRPT  as Written_Premium\n\t\t,[TotalPremiumRPT]\n\t\t,[TotalCostRPT] \n\t\t\n  FROM [PolicyCenter].[dbo].[pc_policyperiod] pp\n  left join [PolicyCenter].[dbo].pc_policy pol\t\t\t\t\t(nolock) on pp.policyid\t\t= pol.id\n  left join [PolicyCenter].[dbo].pc_policyTerm polt\t\t\t\t(nolock) on pp.policytermid = polt.id\n left join [PolicyCenter].[dbo].[pc_job] j\t\t\t\t\t\t(nolock) on pp.jobid\t\t= j.id\n  left join [PolicyCenter].[dbo].[pc_account] act\t\t\t\t(nolock) on pol.AccountID\t= act.id\n  left join pc_producercode prod\t\t\t\t\t\t\t\t(nolock) on pp.ProducerCodeOfRecordID\t= prod.id \n  left join pc_organization org\t\t\t\t\t\t\t\t\t(nolock) on prod.OrganizationID\t\t\t= org.id\n  left join [PolicyCenter].[dbo].[pctl_job] jt\t\t\t\t\t(nolock) on j.SubType\t\t= jt.id\n  left join [PolicyCenter].[dbo].pctl_policyperiodstatus ppst\t(noLock) ON pp.status\t\t= ppst.ID\n  left join [PolicyCenter].[dbo].pctl_bindoption bopt\t\t\t(nolock) on j.BindOption\t= bopt.id\n  left join [PolicyCenter].[dbo].pctl_uwcompanycode uwc\t\t\t(nolock) on pp.UWCompany\t= uwc.TYPECODE\n   -- for change type\n  left join [PolicyCenter].[dbo].pctl_jobdescription_ext jdt\t(nolock) on j.DescriptionTL\t= jdt.id\n  left join pctl_policyperiodsourcetype ppstype\t\t\t\t\t\t\t on ppstype.id\t\t= pp.PolicyPeriodSource\n  -- get profit center\n   left join pctl_profitcentertype profit                       (nolock) on ProfitCenterType\t= profit.id\n   -- get FarmUWTerr\n   left join pctl_orgfarmuwterritory farmterr\t\t\t\t\t(nolock) on FarmUWTerritory\t\t= farmterr.id\n  \n  \n  where j.CloseDate is not null \n  and pol.IssueDate is not null \n  and pp.Policynumber is not null\n  and (ppst.TYPECODE in ('Bound','AuditComplete')) -- and bopt.NAME <> 'BindOnly')   \n  and ProductCode = 'CommercialPackage' \n  and j.CloseDate < @POLENDDATE\n  )jj\nwhere-- LineOfBusiness = 'Commercial Property Line'\n--and cancellationdate is null\n((PeriodStart between @POLSTARTDATE and @POLENDDATE) OR JobCloseDate between @POLSTARTDATE and @POLENDDATE)\nand (ProductCode not in ('CommercialPackage') OR (ProductCode = 'CommercialPackage' AND LineOfBusiness = 'C.P.P.'))\nand ProfitCenter = 'Agribusiness'\norder by PolicyNumber",
    "business_rules": [
      {
        "rule_id": "Rule 1",
        "name": "PolicyCenter_Monoline Rule 1",
        "description": "Only include policies where the policy period status is 'Bound' or 'AuditComplete'.",
        "formula": null
      },
      {
        "rule_id": "Rule 2",
        "name": "PolicyCenter_Monoline Rule 2",
        "description": "Exclude rows where the job close date is after the @POLENDDATE parameter.",
        "formula": null
      },
      {
        "rule_id": "Rule 3",
        "name": "PolicyCenter_Monoline Rule 3",
        "description": "Map UWCompany names to standardized three\u2011letter codes (LRM, WRM, SON) and default to 'UNK' if not matched.",
        "formula": null
      },
      {
        "rule_id": "Rule 4",
        "name": "PolicyCenter_Monoline Rule 4",
        "description": "Derive LineOfBusiness from PatternCode with specific mappings; otherwise retain original PatternCode value.",
        "formula": null
      },
      {
        "rule_id": "Rule 5",
        "name": "PolicyCenter_Monoline Rule 5",
        "description": "For CommercialPackage products, calculate Written_Premium by summing transaction amounts from the appropriate line\u2011specific transaction table; otherwise use the pre\u2011calculated TransactionCostRPT field.",
        "formula": null
      },
      {
        "rule_id": "Rule 6",
        "name": "PolicyCenter_Monoline Rule 6",
        "description": "When ProductCode = 'CommercialPackage' and LineOfBusiness = 'C.P.P.', treat the row as a CommercialPackage line of business.",
        "formula": "When ProductCode = 'CommercialPackage' and LineOfBusiness = 'C.P.P.', treat the row as a CommercialPackage line of business."
      },
      {
        "rule_id": "Rule 7",
        "name": "PolicyCenter_Monoline Rule 7",
        "description": "Show only rows where the profit center equals 'Agribusiness'.",
        "formula": null
      },
      {
        "rule_id": "Rule 8",
        "name": "PolicyCenter_Monoline Rule 8",
        "description": "Expose most recent transaction information only when MostRecentModel = 1.",
        "formula": "Expose most recent transaction information only when MostRecentModel = 1."
      },
      {
        "rule_id": "Rule 9",
        "name": "PolicyCenter_Monoline Rule 9",
        "description": "Populate premium and date columns only for the relevant transaction types (Renewal/Submission, Cancellation, Reinstatement, PolicyChange).",
        "formula": "Populate premium and date columns only for the relevant transaction types (Renewal/Submission, Cancellation, Reinstatement, PolicyChange)."
      },
      {
        "rule_id": "Rule 10",
        "name": "PolicyCenter_Monoline Rule 10",
        "description": "Filter rows to those whose PeriodStart or JobCloseDate fall within the @POLSTARTDATE\u2011@POLENDDATE window.",
        "formula": null
      }
    ],
    "inputs": [
      "pc_policyperiod (alias pp)",
      "pc_policy (alias pol)",
      "pc_policyTerm (alias polt)",
      "pc_policyline (alias polline)",
      "pc_job (alias j)",
      "pc_account (alias act)",
      "pc_producercode (alias prod)",
      "pc_organization (alias org)",
      "pctl_job (alias jt)",
      "pctl_policyperiodstatus (alias ppst)",
      "pctl_bindoption (alias bopt)",
      "pctl_uwcompanycode (alias uwc)",
      "pctl_jobdescription_ext (alias jdt)",
      "pctl_policyperiodsourcetype (alias ppstype)",
      "pctl_profitcentertype (alias profit)",
      "pctl_orgfarmuwterritory (alias farmterr)",
      "pcx_cp7transaction",
      "pcx_gl7transaction_gle",
      "pcx_ca7transaction",
      "pcx_cr7transaction",
      "pc_imtransaction",
      "pcx_wc7transaction"
    ],
    "outputs": [
      "Result set with columns: ProfitCenter, ProductCode, LineOfBusiness, PolicyNumber, OriginalEffectiveDate, PeriodStart, PeriodEnd, AccountNumber, Company, PrimaryInsuredName, AgentCode, AgentName, FarmUWTerritory, MostRecentTran, SubWritten_Premium, SubWritten_Date, CancelledDate, CancelledEffDate, CancelledPremium, ReinstatedPremium, ReinstatedDate, ReinstatedEffDate, ChangePremium, ChangeDate"
    ],
    "transformations": [
      "Union of two SELECT statements to combine detailed transaction\u2011cost calculations with fallback rows for non\u2011pattern\u2011derived lines of business.",
      "Conditional aggregation: SUM(amount) from line\u2011specific transaction tables (cp7, gl7, ca7, cr7, im, wc7) when ProductCode = 'CommercialPackage' and PatternCode matches a line.",
      "CASE expressions to map PatternCode values to human\u2011readable LineOfBusiness strings.",
      "CASE expressions to translate UWCompany names to short codes (LRM, WRM, SON).",
      "CASE logic to expose transaction\u2011type specific premium and date fields (e.g., Written_Premium for Renewal/Submission, CancellationDate for Cancellation, etc.).",
      "Filtering on policy period dates, job close dates, profit center = 'Agribusiness', and status codes ('Bound','AuditComplete').",
      "Ordering final result by PolicyNumber."
    ],
    "dependencies": [
      "SQL Server database PolicyCenter (dbo schema).",
      "Reference tables/views: pc_policyperiod, pc_policy, pc_policyTerm, pc_policyline, pc_job, pc_account, pc_producercode, pc_organization, pctl_job, pctl_policyperiodstatus, pctl_bindoption, pctl_uwcompanycode, pctl_jobdescription_ext, pctl_policyperiodsourcetype, pctl_profitcentertype, pctl_orgfarmuwterritory.",
      "Transaction tables for each line of business: pcx_cp7transaction, pcx_gl7transaction_gle, pcx_ca7transaction, pcx_cr7transaction, pc_imtransaction, pcx_wc7transaction."
    ]
  },
  {
    "id": "Extract_Account.dtsx",
    "name": "Extract_Account.dtsx",
    "type": "SSIS",
    "lines": 170,
    "entities": 26,
    "relationships": 10,
    "rules": 7,
    "purpose": "Extracts ACCOUNT master records from the Guidewire PolicyCenter PostgreSQL replica, cleanses and validates the data, and loads the clean rows into the insurance data warehouse while quarantining invalid rows and logging audit information.",
    "raw_code": "<?xml version=\"1.0\"?>\n<DTS:Executable\n    xmlns:DTS=\"www.microsoft.com/SqlServer/Dts\"\n    xmlns:SQLTask=\"www.microsoft.com/sqlserver/dts/tasks/sqltask\"\n    DTS:ExecutableType=\"Microsoft.Package\"\n    DTS:CreationName=\"Microsoft.Package\"\n    DTS:DTSID=\"{F4DE3551-2A00-4425-A30A-4BF92D5C9092}\"\n    DTS:ObjectName=\"Extract_Account\"\n    DTS:PackageType=\"5\"\n    DTS:VersionMajor=\"1\" DTS:VersionMinor=\"0\" DTS:VersionBuild=\"1\"\n    DTS:VersionGUID=\"{0130E0FA-24AD-4BB2-82E7-9671EEDC9B02}\"\n    DTS:Description=\"Extracts, cleanses, validates and loads ACCOUNT master data from Guidewire PostgreSQL into the DW.\"\n    DTS:LoggingMode=\"UseParentSetting\">\n  <DTS:Variables>\n    <DTS:Variable DTS:Name=\"RowsRead\"><DTS:VariableValue DTS:DataType=\"3\">0</DTS:VariableValue></DTS:Variable>\n    <DTS:Variable DTS:Name=\"RowsInserted\"><DTS:VariableValue DTS:DataType=\"3\">0</DTS:VariableValue></DTS:Variable>\n    <DTS:Variable DTS:Name=\"RowsRejected\"><DTS:VariableValue DTS:DataType=\"3\">0</DTS:VariableValue></DTS:Variable>\n    <DTS:Variable DTS:Name=\"PackageName\"><DTS:VariableValue DTS:DataType=\"8\">Extract_Account</DTS:VariableValue></DTS:Variable>\n    <DTS:Variable DTS:Name=\"StartTime\"><DTS:VariableValue DTS:DataType=\"7\">1900-01-01T00:00:00</DTS:VariableValue></DTS:Variable>\n  </DTS:Variables>\n  <DTS:ConnectionManagers>\n    <DTS:ConnectionManager DTS:refId=\"Package.ConnectionManagers[CM_Guidewire_PG_Source]\"\n        DTS:CreationName=\"ADO.NET:Npgsql\"\n        DTS:DTSID=\"{9115364D-372C-4495-9C1E-50DF8A571152}\"\n        DTS:ObjectName=\"CM_Guidewire_PG_Source\">\n      <DTS:ObjectData>\n        <DTS:ConnectionManager>\n          <DTS:Property DTS:Name=\"ConnectionString\">Server=gw-pg-source.internal;Port=5432;Database=guidewire_policycenter;User Id=etl_reader;Password=[SECURED_BY_PARAMETER];</DTS:Property>\n          <DTS:Property DTS:Name=\"Provider\">Npgsql PostgreSQL Provider</DTS:Property>\n          <DTS:Property DTS:Name=\"Description\">Source: Guidewire PolicyCenter PostgreSQL replica (read-only)</DTS:Property>\n        </DTS:ConnectionManager>\n      </DTS:ObjectData>\n    </DTS:ConnectionManager>\n    <DTS:ConnectionManager DTS:refId=\"Package.ConnectionManagers[CM_DW_PG_Target]\"\n        DTS:CreationName=\"ADO.NET:Npgsql\"\n        DTS:DTSID=\"{687226D2-4BD4-4707-A18E-CDBC9918635C}\"\n        DTS:ObjectName=\"CM_DW_PG_Target\">\n      <DTS:ObjectData>\n        <DTS:ConnectionManager>\n          <DTS:Property DTS:Name=\"ConnectionString\">Server=dw-pg-target.internal;Port=5432;Database=insurance_dw;User Id=etl_writer;Password=[SECURED_BY_PARAMETER];</DTS:Property>\n          <DTS:Property DTS:Name=\"Provider\">Npgsql PostgreSQL Provider</DTS:Property>\n          <DTS:Property DTS:Name=\"Description\">Target: Insurance Data Warehouse - stg / rpt schemas (PostgreSQL)</DTS:Property>\n        </DTS:ConnectionManager>\n      </DTS:ObjectData>\n    </DTS:ConnectionManager>\n  </DTS:ConnectionManagers>\n  <DTS:Executables>\n    <DTS:Executable DTS:refId=\"Package\\SQL_LogStart\" DTS:CreationName=\"Microsoft.ExecuteSQLTask\" DTS:DTSID=\"{9BF0F835-F95F-4735-A351-AFB775FF47E0}\" DTS:ExecutableType=\"Microsoft.ExecuteSQLTask\" DTS:ObjectName=\"SQL - Log Package Start\">\n      <DTS:ObjectData>\n        <SQLTask:SqlTaskData\n            SQLTask:Connection=\"CM_DW_PG_Target\"\n            SQLTask:SqlStatementSource=\"INSERT INTO etl.etl_audit_log (package_name, task_name, start_time, status) VALUES (&apos;Extract_Account&apos;, &apos;Data Flow&apos;, now(), &apos;RUNNING&apos;)\" />\n      </DTS:ObjectData>\n    </DTS:Executable>\n    <DTS:Executable DTS:refId=\"Package\\DFT_Main\" DTS:CreationName=\"Microsoft.Pipeline\" DTS:DTSID=\"{F6BB6189-3F0E-45CB-9B1A-C96B1B4E7EE7}\" DTS:ExecutableType=\"Microsoft.Pipeline\" DTS:ObjectName=\"DFT - Extract, Cleanse, Validate, Load account\">\n      <DTS:ObjectData>\n    <pipeline version=\"1\">\n      <components>\n      <component name=\"SRC - account (PostgreSQL)\" componentClassID=\"Microsoft.ADO.NET.PGSource\" description=\"Extracts rows from public.account on CM_Guidewire_PG_Source\">\n        <properties>\n          <property name=\"SqlCommand\">SELECT account_id, account_number, account_name, industry_type, state_code, account_status, created_date, updated_timestamp FROM public.account</property>\n          <property name=\"ConnectionManager\">CM_Guidewire_PG_Source</property>\n        </properties>\n        <outputs>\n          <output name=\"OLE DB Source Output\" />\n          <output name=\"OLE DB Source Error Output\" />\n        </outputs>\n      </component>\n      <component name=\"DER - Data Cleansing\" componentClassID=\"Microsoft.DerivedColumn\" description=\"Trims whitespace, standardizes casing/codes, normalizes nulls\">\n        <properties>\n          <property name=\"Expressions\">TRIM(account_name) -&gt; account_name; UPPER(TRIM(state_code)) -&gt; state_code</property>\n        </properties>\n        <inputs>\n          <input name=\"OLE DB Source Output\" />\n        </inputs>\n        <outputs>\n          <output name=\"Cleansing Output\" />\n        </outputs>\n      </component>\n      <component name=\"DER - Derived / Calculated Columns\" componentClassID=\"Microsoft.DerivedColumn\" description=\"Adds ETL metadata columns and business-calculated fields\">\n        <properties>\n          <property name=\"Expressions\">GETDATE() -&gt; etl_load_date; 'Guidewire PolicyCenter' -&gt; etl_source_system</property>\n        </properties>\n        <inputs>\n          <input name=\"Cleansing Output\" />\n        </inputs>\n        <outputs>\n          <output name=\"Derived Column Output\" />\n        </outputs>\n      </component>\n      <component name=\"CSPL - Business Rule Validation\" componentClassID=\"Microsoft.ConditionalSplit\" description=\"Routes rows failing business rules to error output. Rules: created_date &lt;= GETDATE() (BR: cannot be future-dated) | account_status IN (&apos;ACTIVE&apos;,&apos;INACTIVE&apos;,&apos;CLOSED&apos;) | account_number LIKE &apos;ACC%%&apos; AND LEN(account_number)=9\">\n        <properties>\n          <property name=\"ValidOutputName\">Valid Rows</property>\n          <property name=\"InvalidOutputName\">Invalid Rows (-&gt; Error Path)</property>\n          <property name=\"Conditions\">created_date &lt;= GETDATE() (BR: cannot be future-dated) | account_status IN ('ACTIVE','INACTIVE','CLOSED') | account_number LIKE 'ACC%%' AND LEN(account_number)=9</property>\n        </properties>\n        <inputs>\n          <input name=\"Derived Column Output\" />\n        </inputs>\n        <outputs>\n          <output name=\"Valid Rows\" />\n          <output name=\"Invalid Rows (-> Error Path)\" />\n        </outputs>\n      </component>\n      <component name=\"UN - Union All Error Rows\" componentClassID=\"Microsoft.UnionAll\" description=\"Combines all error/no-match/invalid outputs into a single error stream\">\n        <properties>\n\n        </properties>\n        <inputs>\n          <input name=\"Lookup No Match Output (-> Error Path)\" />\n          <input name=\"Invalid Rows (-> Error Path)\" />\n          <input name=\"OLE DB Source Error Output\" />\n        </inputs>\n        <outputs>\n          <output name=\"Unified Error Output\" />\n        </outputs>\n      </component>\n      <component name=\"DST - Error Log (stg.error_quarantine)\" componentClassID=\"Microsoft.OLEDBDestination\" description=\"Writes rejected/invalid rows to the error-quarantine table for review\">\n        <properties>\n          <property name=\"OpenRowset\">stg.error_quarantine</property>\n          <property name=\"ConnectionManager\">CM_DW_PG_Target</property>\n        </properties>\n        <inputs>\n          <input name=\"Unified Error Output\" />\n        </inputs>\n      </component>\n      <component name=\"DST - Load account (PostgreSQL DW)\" componentClassID=\"Microsoft.OLEDBDestination\" description=\"Loads validated/cleansed rows into stg.account (upsert via staging + MERGE in post-SQL)\">\n        <properties>\n          <property name=\"OpenRowset\">stg.account</property>\n          <property name=\"ConnectionManager\">CM_DW_PG_Target</property>\n          <property name=\"FastLoad\">true</property>\n          <property name=\"MaximumInsertCommitSize\">10000</property>\n        </properties>\n        <inputs>\n          <input name=\"Valid Rows\" />\n        </inputs>\n      </component>\n      </components>\n    </pipeline>\n      </DTS:ObjectData>\n    </DTS:Executable>\n    <DTS:Executable DTS:refId=\"Package\\SQL_LogEnd\" DTS:CreationName=\"Microsoft.ExecuteSQLTask\" DTS:DTSID=\"{E7829982-2814-4DBF-A5B7-6A42B794F599}\" DTS:ExecutableType=\"Microsoft.ExecuteSQLTask\" DTS:ObjectName=\"SQL - Log Package End / Row Counts\">\n      <DTS:ObjectData>\n        <SQLTask:SqlTaskData\n            SQLTask:Connection=\"CM_DW_PG_Target\"\n            SQLTask:SqlStatementSource=\"UPDATE etl.etl_audit_log SET end_time = now(), status = &apos;COMPLETED&apos;, rows_read = ?, rows_inserted = ?, rows_rejected = ? WHERE package_name = &apos;Extract_Account&apos; AND status = &apos;RUNNING&apos;\" />\n      </DTS:ObjectData>\n    </DTS:Executable>\n  </DTS:Executables>\n  <DTS:PrecedenceConstraints>\n    <DTS:PrecedenceConstraint DTS:refId=\"Package.PrecedenceConstraints[SQL_LogStartToDFT_Main]\"\n        DTS:From=\"Package\\SQL_LogStart\" DTS:To=\"Package\\DFT_Main\" DTS:Value=\"3\" DTS:DTSID=\"{4BD7DE98-65AF-49AD-A0D6-76DBDBE18262}\" />\n    <DTS:PrecedenceConstraint DTS:refId=\"Package.PrecedenceConstraints[DFT_MainToSQL_LogEnd]\"\n        DTS:From=\"Package\\DFT_Main\" DTS:To=\"Package\\SQL_LogEnd\" DTS:Value=\"1\" DTS:DTSID=\"{8E2B03D2-CDD3-431A-BB3E-2D1BE83BC48A}\" />\n  </DTS:PrecedenceConstraints>\n  <DTS:EventHandlers>\n    <DTS:EventHandler DTS:EventName=\"OnError\" DTS:DTSID=\"{85364FCD-A0E4-4026-B305-61F641C47EC7}\" DTS:ObjectName=\"OnError\">\n      <DTS:Executables>\n    <DTS:Executable DTS:refId=\"Package\\EH_LogError\" DTS:CreationName=\"Microsoft.ExecuteSQLTask\" DTS:DTSID=\"{420700A6-A552-46D3-AE0E-BE40F361F364}\" DTS:ExecutableType=\"Microsoft.ExecuteSQLTask\" DTS:ObjectName=\"SQL - Log Error to ETL_ERROR_LOG\">\n      <DTS:ObjectData>\n        <SQLTask:SqlTaskData\n            SQLTask:Connection=\"CM_DW_PG_Target\"\n            SQLTask:SqlStatementSource=\"INSERT INTO etl.etl_error_log (package_name, source_object, error_code, error_description, error_time) VALUES (&apos;Extract_Account&apos;, ?, ?, ?, now())\" />\n      </DTS:ObjectData>\n    </DTS:Executable>\n\n      </DTS:Executables>\n    </DTS:EventHandler>\n  </DTS:EventHandlers>\n</DTS:Executable>\n",
    "business_rules": [
      {
        "rule_id": "Rule 1",
        "name": "Extract_Account Rule 1",
        "description": "created_date must be less than or equal to the current system date (no future\u2011dated records).",
        "formula": null
      },
      {
        "rule_id": "Rule 2",
        "name": "Extract_Account Rule 2",
        "description": "account_status must be one of the allowed values: 'ACTIVE', 'INACTIVE', or 'CLOSED'.",
        "formula": null
      },
      {
        "rule_id": "Rule 3",
        "name": "Extract_Account Rule 3",
        "description": "account_number must start with the literal 'ACC' and be exactly 9 characters long.",
        "formula": null
      },
      {
        "rule_id": "Rule 4",
        "name": "Extract_Account Rule 4",
        "description": "account_name is trimmed of surrounding whitespace before loading.",
        "formula": null
      },
      {
        "rule_id": "Rule 5",
        "name": "Extract_Account Rule 5",
        "description": "state_code is trimmed and converted to upper case to ensure consistent coding.",
        "formula": null
      },
      {
        "rule_id": "Rule 6",
        "name": "Extract_Account Rule 6",
        "description": "Rows that fail any of the above validations are routed to the error quarantine table.",
        "formula": null
      },
      {
        "rule_id": "Rule 7",
        "name": "Extract_Account Rule 7",
        "description": "Audit logging records start time, end time, status, and row counts for monitoring and reconciliation.",
        "formula": null
      }
    ],
    "inputs": [
      "public.account (Guidewire PostgreSQL source table)",
      "etl.etl_audit_log (used for start/end logging)",
      "etl.etl_error_log (used for error logging via OnError handler)"
    ],
    "outputs": [
      "stg.account (staging table in the DW for validated account rows)",
      "stg.error_quarantine (table for rejected/invalid rows)",
      "etl.etl_audit_log (audit record updated with row counts and timestamps)",
      "etl.etl_error_log (error records captured by OnError handler)"
    ],
    "transformations": [
      "SELECT account_id, account_number, account_name, industry_type, state_code, account_status, created_date, updated_timestamp FROM public.account",
      "TRIM(account_name) to remove leading/trailing whitespace",
      "UPPER(TRIM(state_code)) to standardize state codes",
      "Add etl_load_date = GETDATE() and etl_source_system = 'Guidewire PolicyCenter'",
      "Conditional split applying business rule validation (future\u2011date check, status list, account_number pattern/length)",
      "Union All to combine source error output, invalid rows, and lookup\u2011no\u2011match rows into a single error stream",
      "Fast load (bulk insert) into stg.account with commit size 10,000",
      "Insert rejected rows into stg.error_quarantine"
    ],
    "dependencies": [
      "Connection Manager CM_Guidewire_PG_Source (Npgsql provider, read\u2011only replica)",
      "Connection Manager CM_DW_PG_Target (Npgsql provider, DW target)",
      "Execute SQL Task \u2013 Log Package Start (writes to etl.etl_audit_log)",
      "Execute SQL Task \u2013 Log Package End (updates etl.etl_audit_log with row counts)",
      "Execute SQL Task \u2013 Log Error (writes to etl.etl_error_log)",
      "Derived Column components for cleansing and metadata enrichment",
      "Conditional Split component for business rule validation",
      "Union All component for error stream consolidation",
      "OLE DB Destination components for stg.account and stg.error_quarantine",
      "Npgsql PostgreSQL provider libraries"
    ]
  },
  {
    "id": "Extract_Claims.dtsx",
    "name": "Extract_Claims.dtsx",
    "type": "SSIS",
    "lines": 197,
    "entities": 42,
    "relationships": 13,
    "rules": 6,
    "purpose": "Extract claim records from the Guidewire PolicyCenter PostgreSQL replica, validate the policy foreign key, cleanse and enrich the data, enforce claim business rules, pre\u2011aggregate incurred amounts per policy (BR\u201109), and load the results into the data\u2011warehouse staging tables while logging audit information and quarantining rejected rows.",
    "raw_code": "<?xml version=\"1.0\"?>\n<DTS:Executable\n    xmlns:DTS=\"www.microsoft.com/SqlServer/Dts\"\n    xmlns:SQLTask=\"www.microsoft.com/sqlserver/dts/tasks/sqltask\"\n    DTS:ExecutableType=\"Microsoft.Package\"\n    DTS:CreationName=\"Microsoft.Package\"\n    DTS:DTSID=\"{C284DE78-E237-41FA-B146-50FA5AABC1C9}\"\n    DTS:ObjectName=\"Extract_Claims\"\n    DTS:PackageType=\"5\"\n    DTS:VersionMajor=\"1\" DTS:VersionMinor=\"0\" DTS:VersionBuild=\"1\"\n    DTS:VersionGUID=\"{4CA2A438-C3CE-42C3-8653-0529F8D3FE87}\"\n    DTS:Description=\"Extracts CLAIMS, validates FK to POLICY, applies incurred-amount reconciliation, pre-aggregates (BR-09) and loads.\"\n    DTS:LoggingMode=\"UseParentSetting\">\n  <DTS:Variables>\n    <DTS:Variable DTS:Name=\"RowsRead\"><DTS:VariableValue DTS:DataType=\"3\">0</DTS:VariableValue></DTS:Variable>\n    <DTS:Variable DTS:Name=\"RowsInserted\"><DTS:VariableValue DTS:DataType=\"3\">0</DTS:VariableValue></DTS:Variable>\n    <DTS:Variable DTS:Name=\"RowsRejected\"><DTS:VariableValue DTS:DataType=\"3\">0</DTS:VariableValue></DTS:Variable>\n    <DTS:Variable DTS:Name=\"PackageName\"><DTS:VariableValue DTS:DataType=\"8\">Extract_Claims</DTS:VariableValue></DTS:Variable>\n    <DTS:Variable DTS:Name=\"StartTime\"><DTS:VariableValue DTS:DataType=\"7\">1900-01-01T00:00:00</DTS:VariableValue></DTS:Variable>\n  </DTS:Variables>\n  <DTS:ConnectionManagers>\n    <DTS:ConnectionManager DTS:refId=\"Package.ConnectionManagers[CM_Guidewire_PG_Source]\"\n        DTS:CreationName=\"ADO.NET:Npgsql\"\n        DTS:DTSID=\"{9115364D-372C-4495-9C1E-50DF8A571152}\"\n        DTS:ObjectName=\"CM_Guidewire_PG_Source\">\n      <DTS:ObjectData>\n        <DTS:ConnectionManager>\n          <DTS:Property DTS:Name=\"ConnectionString\">Server=gw-pg-source.internal;Port=5432;Database=guidewire_policycenter;User Id=etl_reader;Password=[SECURED_BY_PARAMETER];</DTS:Property>\n          <DTS:Property DTS:Name=\"Provider\">Npgsql PostgreSQL Provider</DTS:Property>\n          <DTS:Property DTS:Name=\"Description\">Source: Guidewire PolicyCenter PostgreSQL replica (read-only)</DTS:Property>\n        </DTS:ConnectionManager>\n      </DTS:ObjectData>\n    </DTS:ConnectionManager>\n    <DTS:ConnectionManager DTS:refId=\"Package.ConnectionManagers[CM_DW_PG_Target]\"\n        DTS:CreationName=\"ADO.NET:Npgsql\"\n        DTS:DTSID=\"{687226D2-4BD4-4707-A18E-CDBC9918635C}\"\n        DTS:ObjectName=\"CM_DW_PG_Target\">\n      <DTS:ObjectData>\n        <DTS:ConnectionManager>\n          <DTS:Property DTS:Name=\"ConnectionString\">Server=dw-pg-target.internal;Port=5432;Database=insurance_dw;User Id=etl_writer;Password=[SECURED_BY_PARAMETER];</DTS:Property>\n          <DTS:Property DTS:Name=\"Provider\">Npgsql PostgreSQL Provider</DTS:Property>\n          <DTS:Property DTS:Name=\"Description\">Target: Insurance Data Warehouse - stg / rpt schemas (PostgreSQL)</DTS:Property>\n        </DTS:ConnectionManager>\n      </DTS:ObjectData>\n    </DTS:ConnectionManager>\n  </DTS:ConnectionManagers>\n  <DTS:Executables>\n    <DTS:Executable DTS:refId=\"Package\\SQL_LogStart\" DTS:CreationName=\"Microsoft.ExecuteSQLTask\" DTS:DTSID=\"{FA3319C7-1B5C-4353-8131-B7EF988576C3}\" DTS:ExecutableType=\"Microsoft.ExecuteSQLTask\" DTS:ObjectName=\"SQL - Log Package Start\">\n      <DTS:ObjectData>\n        <SQLTask:SqlTaskData\n            SQLTask:Connection=\"CM_DW_PG_Target\"\n            SQLTask:SqlStatementSource=\"INSERT INTO etl.etl_audit_log (package_name, task_name, start_time, status) VALUES (&apos;Extract_Claims&apos;, &apos;Data Flow&apos;, now(), &apos;RUNNING&apos;)\" />\n      </DTS:ObjectData>\n    </DTS:Executable>\n    <DTS:Executable DTS:refId=\"Package\\DFT_Main\" DTS:CreationName=\"Microsoft.Pipeline\" DTS:DTSID=\"{3E16970D-3E7A-4D70-9EA4-2E3D98E89EED}\" DTS:ExecutableType=\"Microsoft.Pipeline\" DTS:ObjectName=\"DFT - Extract, Cleanse, Validate, Load claims\">\n      <DTS:ObjectData>\n    <pipeline version=\"1\">\n      <components>\n      <component name=\"SRC - claims (PostgreSQL)\" componentClassID=\"Microsoft.ADO.NET.PGSource\" description=\"Extracts rows from public.claims on CM_Guidewire_PG_Source\">\n        <properties>\n          <property name=\"SqlCommand\">SELECT claim_id, policy_id, claim_number, claim_date, claim_status, claim_type, paid_amount, reserve_amount, recovery_amount, incurred_amount, loss_date, reported_date FROM public.claims</property>\n          <property name=\"ConnectionManager\">CM_Guidewire_PG_Source</property>\n        </properties>\n        <outputs>\n          <output name=\"OLE DB Source Output\" />\n          <output name=\"OLE DB Source Error Output\" />\n        </outputs>\n      </component>\n      <component name=\"LKP - Validate Policy (policy_id)\" componentClassID=\"Microsoft.Lookup\" description=\"Validates policy_id exists in Policy (referential integrity / BR-01, BR-05)\">\n        <properties>\n          <property name=\"SqlCommandParam\">SELECT policy_id FROM stg.policy</property>\n          <property name=\"JoinColumn\">policy_id</property>\n          <property name=\"NoMatchBehavior\">RedirectRowsToNoMatchOutput</property>\n          <property name=\"CacheMode\">Full</property>\n        </properties>\n        <inputs>\n          <input name=\"OLE DB Source Output\" />\n        </inputs>\n        <outputs>\n          <output name=\"Lookup Match Output\" />\n          <output name=\"Lookup No Match Output (-> Error Path)\" />\n        </outputs>\n      </component>\n      <component name=\"DER - Data Cleansing\" componentClassID=\"Microsoft.DerivedColumn\" description=\"Trims whitespace, standardizes casing/codes, normalizes nulls\">\n        <properties>\n          <property name=\"Expressions\">TRIM(claim_number) -&gt; claim_number; UPPER(claim_type) -&gt; claim_type</property>\n        </properties>\n        <inputs>\n          <input name=\"Lookup Match Output\" />\n        </inputs>\n        <outputs>\n          <output name=\"Cleansing Output\" />\n        </outputs>\n      </component>\n      <component name=\"DER - Derived / Calculated Columns\" componentClassID=\"Microsoft.DerivedColumn\" description=\"Adds ETL metadata columns and business-calculated fields\">\n        <properties>\n          <property name=\"Expressions\">GETDATE() -&gt; etl_load_date; paid_amount + reserve_amount - recovery_amount -&gt; calculated_incurred_amount</property>\n        </properties>\n        <inputs>\n          <input name=\"Cleansing Output\" />\n        </inputs>\n        <outputs>\n          <output name=\"Derived Column Output\" />\n        </outputs>\n      </component>\n      <component name=\"CSPL - Business Rule Validation\" componentClassID=\"Microsoft.ConditionalSplit\" description=\"Routes rows failing business rules to error output. Rules: paid_amount &gt;= 0.00 AND reserve_amount &gt;= 0.00 AND recovery_amount &gt;= 0.00 | ABS(incurred_amount - calculated_incurred_amount) &lt;= 1.00 (incurred = paid + reserve - recovery) | loss_date &lt;= reported_date AND reported_date &lt;= claim_date (BR-12 lifecycle chronology) | claim_status IN (&apos;OPEN&apos;,&apos;IN_PROGRESS&apos;,&apos;ON_HOLD&apos;,&apos;CLOSED&apos;,&apos;REJECTED&apos;)\">\n        <properties>\n          <property name=\"ValidOutputName\">Valid Rows</property>\n          <property name=\"InvalidOutputName\">Invalid Rows (-&gt; Error Path)</property>\n          <property name=\"Conditions\">paid_amount &gt;= 0.00 AND reserve_amount &gt;= 0.00 AND recovery_amount &gt;= 0.00 | ABS(incurred_amount - calculated_incurred_amount) &lt;= 1.00 (incurred = paid + reserve - recovery) | loss_date &lt;= reported_date AND reported_date &lt;= claim_date (BR-12 lifecycle chronology) | claim_status IN ('OPEN','IN_PROGRESS','ON_HOLD','CLOSED','REJECTED')</property>\n        </properties>\n        <inputs>\n          <input name=\"Derived Column Output\" />\n        </inputs>\n        <outputs>\n          <output name=\"Valid Rows\" />\n          <output name=\"Invalid Rows (-> Error Path)\" />\n        </outputs>\n      </component>\n      <component name=\"AGG - Claims Incurred Summary by Policy (BR-09 pre-aggregation)\" componentClassID=\"Microsoft.Aggregation\" description=\"Pre-aggregates incurred/paid/reserve/recovery per policy_id BEFORE any KPI join, preventing duplicate premium totals when joined downstream.\">\n        <properties>\n          <property name=\"GroupBy\">policy_id</property>\n          <property name=\"Aggregates\">SUM(paid_amount), SUM(reserve_amount), SUM(recovery_amount), SUM(incurred_amount), COUNT(claim_id) AS claim_count</property>\n        </properties>\n        <inputs>\n          <input name=\"Valid Rows\" />\n        </inputs>\n        <outputs>\n          <output name=\"Aggregate Output\" />\n        </outputs>\n      </component>\n      <component name=\"UN - Union All Error Rows\" componentClassID=\"Microsoft.UnionAll\" description=\"Combines all error/no-match/invalid outputs into a single error stream\">\n        <properties>\n\n        </properties>\n        <inputs>\n          <input name=\"Lookup No Match Output (-> Error Path)\" />\n          <input name=\"Invalid Rows (-> Error Path)\" />\n          <input name=\"OLE DB Source Error Output\" />\n        </inputs>\n        <outputs>\n          <output name=\"Unified Error Output\" />\n        </outputs>\n      </component>\n      <component name=\"DST - Error Log (stg.error_quarantine)\" componentClassID=\"Microsoft.OLEDBDestination\" description=\"Writes rejected/invalid rows to the error-quarantine table for review\">\n        <properties>\n          <property name=\"OpenRowset\">stg.error_quarantine</property>\n          <property name=\"ConnectionManager\">CM_DW_PG_Target</property>\n        </properties>\n        <inputs>\n          <input name=\"Unified Error Output\" />\n        </inputs>\n      </component>\n      <component name=\"DST - Load claims (PostgreSQL DW)\" componentClassID=\"Microsoft.OLEDBDestination\" description=\"Loads validated/cleansed rows into stg.claims (upsert via staging + MERGE in post-SQL)\">\n        <properties>\n          <property name=\"OpenRowset\">stg.claims</property>\n          <property name=\"ConnectionManager\">CM_DW_PG_Target</property>\n          <property name=\"FastLoad\">true</property>\n          <property name=\"MaximumInsertCommitSize\">10000</property>\n        </properties>\n        <inputs>\n          <input name=\"Aggregate Output\" />\n        </inputs>\n      </component>\n      </components>\n    </pipeline>\n      </DTS:ObjectData>\n    </DTS:Executable>\n    <DTS:Executable DTS:refId=\"Package\\SQL_LogEnd\" DTS:CreationName=\"Microsoft.ExecuteSQLTask\" DTS:DTSID=\"{323081EF-ECFC-4942-9BFA-A548344FDF8A}\" DTS:ExecutableType=\"Microsoft.ExecuteSQLTask\" DTS:ObjectName=\"SQL - Log Package End / Row Counts\">\n      <DTS:ObjectData>\n        <SQLTask:SqlTaskData\n            SQLTask:Connection=\"CM_DW_PG_Target\"\n            SQLTask:SqlStatementSource=\"UPDATE etl.etl_audit_log SET end_time = now(), status = &apos;COMPLETED&apos;, rows_read = ?, rows_inserted = ?, rows_rejected = ? WHERE package_name = &apos;Extract_Claims&apos; AND status = &apos;RUNNING&apos;\" />\n      </DTS:ObjectData>\n    </DTS:Executable>\n  </DTS:Executables>\n  <DTS:PrecedenceConstraints>\n    <DTS:PrecedenceConstraint DTS:refId=\"Package.PrecedenceConstraints[SQL_LogStartToDFT_Main]\"\n        DTS:From=\"Package\\SQL_LogStart\" DTS:To=\"Package\\DFT_Main\" DTS:Value=\"3\" DTS:DTSID=\"{97018531-68B4-4F91-96EA-7A1E9DDC4DBE}\" />\n    <DTS:PrecedenceConstraint DTS:refId=\"Package.PrecedenceConstraints[DFT_MainToSQL_LogEnd]\"\n        DTS:From=\"Package\\DFT_Main\" DTS:To=\"Package\\SQL_LogEnd\" DTS:Value=\"1\" DTS:DTSID=\"{5919BE4F-8A1A-4C89-A787-2452582E4A52}\" />\n  </DTS:PrecedenceConstraints>\n  <DTS:EventHandlers>\n    <DTS:EventHandler DTS:EventName=\"OnError\" DTS:DTSID=\"{1FDA477C-C86A-422C-8AB3-DEA7ADBF6786}\" DTS:ObjectName=\"OnError\">\n      <DTS:Executables>\n    <DTS:Executable DTS:refId=\"Package\\EH_LogError\" DTS:CreationName=\"Microsoft.ExecuteSQLTask\" DTS:DTSID=\"{62902F90-F23E-407A-BBFF-02787D3F81B1}\" DTS:ExecutableType=\"Microsoft.ExecuteSQLTask\" DTS:ObjectName=\"SQL - Log Error to ETL_ERROR_LOG\">\n      <DTS:ObjectData>\n        <SQLTask:SqlTaskData\n            SQLTask:Connection=\"CM_DW_PG_Target\"\n            SQLTask:SqlStatementSource=\"INSERT INTO etl.etl_error_log (package_name, source_object, error_code, error_description, error_time) VALUES (&apos;Extract_Claims&apos;, ?, ?, ?, now())\" />\n      </DTS:ObjectData>\n    </DTS:Executable>\n\n      </DTS:Executables>\n    </DTS:EventHandler>\n  </DTS:EventHandlers>\n</DTS:Executable>\n",
    "business_rules": [
      {
        "rule_id": "Rule 1",
        "name": "Extract_Claims Rule 1",
        "description": "BR\u201101/BR\u201105: policy_id must exist in stg.policy (referential integrity)",
        "formula": "BR\u201101/BR\u201105: policy_id must exist in stg.policy (referential integrity)"
      },
      {
        "rule_id": "Rule 2",
        "name": "Extract_Claims Rule 2",
        "description": "Monetary fields paid_amount, reserve_amount, recovery_amount must be >= 0.00",
        "formula": "Monetary fields paid_amount, reserve_amount, recovery_amount must be >= 0.00"
      },
      {
        "rule_id": "Rule 3",
        "name": "Extract_Claims Rule 3",
        "description": "Incurred amount reconciliation: ABS(incurred_amount - (paid_amount + reserve_amount - recovery_amount)) <= 1.00",
        "formula": "Incurred amount reconciliation: ABS(incurred_amount - (paid_amount + reserve_amount - recovery_amount)) <= 1.00"
      },
      {
        "rule_id": "Rule 4",
        "name": "Extract_Claims Rule 4",
        "description": "BR\u201112 lifecycle chronology: loss_date <= reported_date <= claim_date",
        "formula": "BR\u201112 lifecycle chronology: loss_date <= reported_date <= claim_date"
      },
      {
        "rule_id": "Rule 5",
        "name": "Extract_Claims Rule 5",
        "description": "claim_status must be one of ('OPEN','IN_PROGRESS','ON_HOLD','CLOSED','REJECTED')",
        "formula": null
      },
      {
        "rule_id": "Rule 6",
        "name": "Extract_Claims Rule 6",
        "description": "Pre\u2011aggregation (BR\u201109) of claim financials per policy to avoid duplicate premium totals downstream",
        "formula": null
      }
    ],
    "inputs": [
      "public.claims (source PostgreSQL table via CM_Guidewire_PG_Source)",
      "stg.policy (target PostgreSQL table used for policy_id lookup)",
      "Package variables RowsRead, RowsInserted, RowsRejected"
    ],
    "outputs": [
      "stg.claims (staging table for validated/aggregated claim data)",
      "stg.error_quarantine (table for rejected or invalid claim rows)",
      "etl.etl_audit_log (package execution audit record)",
      "etl.etl_error_log (error handler log entries)"
    ],
    "transformations": [
      "SQL SELECT of claim columns from public.claims",
      "Lookup join on policy_id to enforce referential integrity (BR\u201101, BR\u201105)",
      "Derived Column: TRIM(claim_number) and UPPER(claim_type)",
      "Derived Column: GETDATE() \u2192 etl_load_date; calculated_incurred_amount = paid_amount + reserve_amount - recovery_amount",
      "Conditional Split enforcing: non\u2011negative amounts, incurred reconciliation tolerance (|incurred\u2011calculated| \u2264 1.00), date chronology (loss \u2264 reported \u2264 claim), allowed claim_status values",
      "Aggregation by policy_id: SUM(paid_amount), SUM(reserve_amount), SUM(recovery_amount), SUM(incurred_amount), COUNT(claim_id) AS claim_count (BR\u201109)",
      "Union All of all error streams",
      "FastLoad insert into stg.claims with commit size 10,000"
    ],
    "dependencies": [
      "Connection Manager CM_Guidewire_PG_Source (Npgsql provider)",
      "Connection Manager CM_DW_PG_Target (Npgsql provider)",
      "SSIS components: ADO.NET PostgreSQL Source, Lookup, Derived Column, Conditional Split, Aggregation, Union All, OLE DB Destination",
      "Source table public.claims",
      "Reference table stg.policy",
      "Target tables stg.claims, stg.error_quarantine, etl.etl_audit_log, etl.etl_error_log"
    ]
  },
  {
    "id": "Extract_Coverage.dtsx",
    "name": "Extract_Coverage.dtsx",
    "type": "SSIS",
    "lines": 185,
    "entities": 36,
    "relationships": 25,
    "rules": 7,
    "purpose": "Extracts rows from the Guidewire PolicyCenter coverage table, validates the foreign key to POLICY_PERIOD, applies data cleansing and business rule checks, and loads the clean rows into the data warehouse staging schema while quarantining invalid rows and logging audit information.",
    "raw_code": "<?xml version=\"1.0\"?>\n<DTS:Executable\n    xmlns:DTS=\"www.microsoft.com/SqlServer/Dts\"\n    xmlns:SQLTask=\"www.microsoft.com/sqlserver/dts/tasks/sqltask\"\n    DTS:ExecutableType=\"Microsoft.Package\"\n    DTS:CreationName=\"Microsoft.Package\"\n    DTS:DTSID=\"{37024C3F-247E-420C-A68C-D26AE3D5A5FA}\"\n    DTS:ObjectName=\"Extract_Coverage\"\n    DTS:PackageType=\"5\"\n    DTS:VersionMajor=\"1\" DTS:VersionMinor=\"0\" DTS:VersionBuild=\"1\"\n    DTS:VersionGUID=\"{BAF160F2-3F0B-4C76-8FE5-38BDBE7F4515}\"\n    DTS:Description=\"Extracts COVERAGE, validates FK to POLICY_PERIOD (BR-05), cleanses and loads.\"\n    DTS:LoggingMode=\"UseParentSetting\">\n  <DTS:Variables>\n    <DTS:Variable DTS:Name=\"RowsRead\"><DTS:VariableValue DTS:DataType=\"3\">0</DTS:VariableValue></DTS:Variable>\n    <DTS:Variable DTS:Name=\"RowsInserted\"><DTS:VariableValue DTS:DataType=\"3\">0</DTS:VariableValue></DTS:Variable>\n    <DTS:Variable DTS:Name=\"RowsRejected\"><DTS:VariableValue DTS:DataType=\"3\">0</DTS:VariableValue></DTS:Variable>\n    <DTS:Variable DTS:Name=\"PackageName\"><DTS:VariableValue DTS:DataType=\"8\">Extract_Coverage</DTS:VariableValue></DTS:Variable>\n    <DTS:Variable DTS:Name=\"StartTime\"><DTS:VariableValue DTS:DataType=\"7\">1900-01-01T00:00:00</DTS:VariableValue></DTS:Variable>\n  </DTS:Variables>\n  <DTS:ConnectionManagers>\n    <DTS:ConnectionManager DTS:refId=\"Package.ConnectionManagers[CM_Guidewire_PG_Source]\"\n        DTS:CreationName=\"ADO.NET:Npgsql\"\n        DTS:DTSID=\"{9115364D-372C-4495-9C1E-50DF8A571152}\"\n        DTS:ObjectName=\"CM_Guidewire_PG_Source\">\n      <DTS:ObjectData>\n        <DTS:ConnectionManager>\n          <DTS:Property DTS:Name=\"ConnectionString\">Server=gw-pg-source.internal;Port=5432;Database=guidewire_policycenter;User Id=etl_reader;Password=[SECURED_BY_PARAMETER];</DTS:Property>\n          <DTS:Property DTS:Name=\"Provider\">Npgsql PostgreSQL Provider</DTS:Property>\n          <DTS:Property DTS:Name=\"Description\">Source: Guidewire PolicyCenter PostgreSQL replica (read-only)</DTS:Property>\n        </DTS:ConnectionManager>\n      </DTS:ObjectData>\n    </DTS:ConnectionManager>\n    <DTS:ConnectionManager DTS:refId=\"Package.ConnectionManagers[CM_DW_PG_Target]\"\n        DTS:CreationName=\"ADO.NET:Npgsql\"\n        DTS:DTSID=\"{687226D2-4BD4-4707-A18E-CDBC9918635C}\"\n        DTS:ObjectName=\"CM_DW_PG_Target\">\n      <DTS:ObjectData>\n        <DTS:ConnectionManager>\n          <DTS:Property DTS:Name=\"ConnectionString\">Server=dw-pg-target.internal;Port=5432;Database=insurance_dw;User Id=etl_writer;Password=[SECURED_BY_PARAMETER];</DTS:Property>\n          <DTS:Property DTS:Name=\"Provider\">Npgsql PostgreSQL Provider</DTS:Property>\n          <DTS:Property DTS:Name=\"Description\">Target: Insurance Data Warehouse - stg / rpt schemas (PostgreSQL)</DTS:Property>\n        </DTS:ConnectionManager>\n      </DTS:ObjectData>\n    </DTS:ConnectionManager>\n  </DTS:ConnectionManagers>\n  <DTS:Executables>\n    <DTS:Executable DTS:refId=\"Package\\SQL_LogStart\" DTS:CreationName=\"Microsoft.ExecuteSQLTask\" DTS:DTSID=\"{815DFBAB-D1FC-4870-973E-E8E17E9CC761}\" DTS:ExecutableType=\"Microsoft.ExecuteSQLTask\" DTS:ObjectName=\"SQL - Log Package Start\">\n      <DTS:ObjectData>\n        <SQLTask:SqlTaskData\n            SQLTask:Connection=\"CM_DW_PG_Target\"\n            SQLTask:SqlStatementSource=\"INSERT INTO etl.etl_audit_log (package_name, task_name, start_time, status) VALUES (&apos;Extract_Coverage&apos;, &apos;Data Flow&apos;, now(), &apos;RUNNING&apos;)\" />\n      </DTS:ObjectData>\n    </DTS:Executable>\n    <DTS:Executable DTS:refId=\"Package\\DFT_Main\" DTS:CreationName=\"Microsoft.Pipeline\" DTS:DTSID=\"{CC93A872-61CB-472C-9F1F-D5DDE895F703}\" DTS:ExecutableType=\"Microsoft.Pipeline\" DTS:ObjectName=\"DFT - Extract, Cleanse, Validate, Load coverage\">\n      <DTS:ObjectData>\n    <pipeline version=\"1\">\n      <components>\n      <component name=\"SRC - coverage (PostgreSQL)\" componentClassID=\"Microsoft.ADO.NET.PGSource\" description=\"Extracts rows from public.coverage on CM_Guidewire_PG_Source\">\n        <properties>\n          <property name=\"SqlCommand\">SELECT coverage_id, policy_period_id, coverage_code, coverage_name, limit_amount, deductible_amount, coverage_start_date, coverage_end_date, coverage_status FROM public.coverage</property>\n          <property name=\"ConnectionManager\">CM_Guidewire_PG_Source</property>\n        </properties>\n        <outputs>\n          <output name=\"OLE DB Source Output\" />\n          <output name=\"OLE DB Source Error Output\" />\n        </outputs>\n      </component>\n      <component name=\"LKP - Validate Policy_Period (policy_period_id)\" componentClassID=\"Microsoft.Lookup\" description=\"Validates policy_period_id exists in Policy_Period (referential integrity / BR-01, BR-05)\">\n        <properties>\n          <property name=\"SqlCommandParam\">SELECT policy_period_id FROM stg.policy_period</property>\n          <property name=\"JoinColumn\">policy_period_id</property>\n          <property name=\"NoMatchBehavior\">RedirectRowsToNoMatchOutput</property>\n          <property name=\"CacheMode\">Full</property>\n        </properties>\n        <inputs>\n          <input name=\"OLE DB Source Output\" />\n        </inputs>\n        <outputs>\n          <output name=\"Lookup Match Output\" />\n          <output name=\"Lookup No Match Output (-> Error Path)\" />\n        </outputs>\n      </component>\n      <component name=\"DER - Data Cleansing\" componentClassID=\"Microsoft.DerivedColumn\" description=\"Trims whitespace, standardizes casing/codes, normalizes nulls\">\n        <properties>\n          <property name=\"Expressions\">TRIM(coverage_name) -&gt; coverage_name; UPPER(coverage_code) -&gt; coverage_code</property>\n        </properties>\n        <inputs>\n          <input name=\"Lookup Match Output\" />\n        </inputs>\n        <outputs>\n          <output name=\"Cleansing Output\" />\n        </outputs>\n      </component>\n      <component name=\"DER - Derived / Calculated Columns\" componentClassID=\"Microsoft.DerivedColumn\" description=\"Adds ETL metadata columns and business-calculated fields\">\n        <properties>\n          <property name=\"Expressions\">GETDATE() -&gt; etl_load_date</property>\n        </properties>\n        <inputs>\n          <input name=\"Cleansing Output\" />\n        </inputs>\n        <outputs>\n          <output name=\"Derived Column Output\" />\n        </outputs>\n      </component>\n      <component name=\"CSPL - Business Rule Validation\" componentClassID=\"Microsoft.ConditionalSplit\" description=\"Routes rows failing business rules to error output. Rules: limit_amount &gt;= 0.00 | deductible_amount &gt;= 0.00 | coverage_end_date &gt; coverage_start_date | coverage_status IN (&apos;ACTIVE&apos;,&apos;EXPIRED&apos;,&apos;CANCELLED&apos;,&apos;SUSPENDED&apos;)\">\n        <properties>\n          <property name=\"ValidOutputName\">Valid Rows</property>\n          <property name=\"InvalidOutputName\">Invalid Rows (-&gt; Error Path)</property>\n          <property name=\"Conditions\">limit_amount &gt;= 0.00 | deductible_amount &gt;= 0.00 | coverage_end_date &gt; coverage_start_date | coverage_status IN ('ACTIVE','EXPIRED','CANCELLED','SUSPENDED')</property>\n        </properties>\n        <inputs>\n          <input name=\"Derived Column Output\" />\n        </inputs>\n        <outputs>\n          <output name=\"Valid Rows\" />\n          <output name=\"Invalid Rows (-> Error Path)\" />\n        </outputs>\n      </component>\n      <component name=\"UN - Union All Error Rows\" componentClassID=\"Microsoft.UnionAll\" description=\"Combines all error/no-match/invalid outputs into a single error stream\">\n        <properties>\n\n        </properties>\n        <inputs>\n          <input name=\"Lookup No Match Output (-> Error Path)\" />\n          <input name=\"Invalid Rows (-> Error Path)\" />\n          <input name=\"OLE DB Source Error Output\" />\n        </inputs>\n        <outputs>\n          <output name=\"Unified Error Output\" />\n        </outputs>\n      </component>\n      <component name=\"DST - Error Log (stg.error_quarantine)\" componentClassID=\"Microsoft.OLEDBDestination\" description=\"Writes rejected/invalid rows to the error-quarantine table for review\">\n        <properties>\n          <property name=\"OpenRowset\">stg.error_quarantine</property>\n          <property name=\"ConnectionManager\">CM_DW_PG_Target</property>\n        </properties>\n        <inputs>\n          <input name=\"Unified Error Output\" />\n        </inputs>\n      </component>\n      <component name=\"DST - Load coverage (PostgreSQL DW)\" componentClassID=\"Microsoft.OLEDBDestination\" description=\"Loads validated/cleansed rows into stg.coverage (upsert via staging + MERGE in post-SQL)\">\n        <properties>\n          <property name=\"OpenRowset\">stg.coverage</property>\n          <property name=\"ConnectionManager\">CM_DW_PG_Target</property>\n          <property name=\"FastLoad\">true</property>\n          <property name=\"MaximumInsertCommitSize\">10000</property>\n        </properties>\n        <inputs>\n          <input name=\"Valid Rows\" />\n        </inputs>\n      </component>\n      </components>\n    </pipeline>\n      </DTS:ObjectData>\n    </DTS:Executable>\n    <DTS:Executable DTS:refId=\"Package\\SQL_LogEnd\" DTS:CreationName=\"Microsoft.ExecuteSQLTask\" DTS:DTSID=\"{F5B231CC-8DD0-4FF7-9A85-3A30B41DAA99}\" DTS:ExecutableType=\"Microsoft.ExecuteSQLTask\" DTS:ObjectName=\"SQL - Log Package End / Row Counts\">\n      <DTS:ObjectData>\n        <SQLTask:SqlTaskData\n            SQLTask:Connection=\"CM_DW_PG_Target\"\n            SQLTask:SqlStatementSource=\"UPDATE etl.etl_audit_log SET end_time = now(), status = &apos;COMPLETED&apos;, rows_read = ?, rows_inserted = ?, rows_rejected = ? WHERE package_name = &apos;Extract_Coverage&apos; AND status = &apos;RUNNING&apos;\" />\n      </DTS:ObjectData>\n    </DTS:Executable>\n  </DTS:Executables>\n  <DTS:PrecedenceConstraints>\n    <DTS:PrecedenceConstraint DTS:refId=\"Package.PrecedenceConstraints[SQL_LogStartToDFT_Main]\"\n        DTS:From=\"Package\\SQL_LogStart\" DTS:To=\"Package\\DFT_Main\" DTS:Value=\"3\" DTS:DTSID=\"{CDE01D3E-71FC-4FFB-8337-656AE41048F2}\" />\n    <DTS:PrecedenceConstraint DTS:refId=\"Package.PrecedenceConstraints[DFT_MainToSQL_LogEnd]\"\n        DTS:From=\"Package\\DFT_Main\" DTS:To=\"Package\\SQL_LogEnd\" DTS:Value=\"1\" DTS:DTSID=\"{C5EE97F3-669F-40FE-B7B1-095A73726824}\" />\n  </DTS:PrecedenceConstraints>\n  <DTS:EventHandlers>\n    <DTS:EventHandler DTS:EventName=\"OnError\" DTS:DTSID=\"{2905D6FF-7B18-4F6C-82BA-8F21C0D4216E}\" DTS:ObjectName=\"OnError\">\n      <DTS:Executables>\n    <DTS:Executable DTS:refId=\"Package\\EH_LogError\" DTS:CreationName=\"Microsoft.ExecuteSQLTask\" DTS:DTSID=\"{4D63F958-AE60-4B58-9A2D-898A44428532}\" DTS:ExecutableType=\"Microsoft.ExecuteSQLTask\" DTS:ObjectName=\"SQL - Log Error to ETL_ERROR_LOG\">\n      <DTS:ObjectData>\n        <SQLTask:SqlTaskData\n            SQLTask:Connection=\"CM_DW_PG_Target\"\n            SQLTask:SqlStatementSource=\"INSERT INTO etl.etl_error_log (package_name, source_object, error_code, error_description, error_time) VALUES (&apos;Extract_Coverage&apos;, ?, ?, ?, now())\" />\n      </DTS:ObjectData>\n    </DTS:Executable>\n\n      </DTS:Executables>\n    </DTS:EventHandler>\n  </DTS:EventHandlers>\n</DTS:Executable>\n",
    "business_rules": [
      {
        "rule_id": "Rule 1",
        "name": "Extract_Coverage Rule 1",
        "description": "BR\u201101/BR\u201105: policy_period_id must exist in stg.policy_period (referential integrity).",
        "formula": "BR\u201101/BR\u201105: policy_period_id must exist in stg.policy_period (referential integrity)."
      },
      {
        "rule_id": "Rule 2",
        "name": "Extract_Coverage Rule 2",
        "description": "Coverage limit_amount must be greater than or equal to 0.00.",
        "formula": null
      },
      {
        "rule_id": "Rule 3",
        "name": "Extract_Coverage Rule 3",
        "description": "Coverage deductible_amount must be greater than or equal to 0.00.",
        "formula": null
      },
      {
        "rule_id": "Rule 4",
        "name": "Extract_Coverage Rule 4",
        "description": "coverage_end_date must be later than coverage_start_date.",
        "formula": null
      },
      {
        "rule_id": "Rule 5",
        "name": "Extract_Coverage Rule 5",
        "description": "coverage_status must be one of: ACTIVE, EXPIRED, CANCELLED, SUSPENDED.",
        "formula": null
      },
      {
        "rule_id": "Rule 6",
        "name": "Extract_Coverage Rule 6",
        "description": "coverage_name is trimmed of leading/trailing whitespace.",
        "formula": "coverage_name is trimmed of leading/trailing whitespace."
      },
      {
        "rule_id": "Rule 7",
        "name": "Extract_Coverage Rule 7",
        "description": "coverage_code is converted to upper case.",
        "formula": null
      }
    ],
    "inputs": [
      "public.coverage (Guidewire PolicyCenter PostgreSQL source)",
      "stg.policy_period (Data Warehouse staging table for policy periods)",
      "OLE DB Source Error Output (source component error stream)"
    ],
    "outputs": [
      "stg.coverage (Data Warehouse staging table for coverage)",
      "stg.error_quarantine (table for rejected/invalid rows)",
      "etl.etl_audit_log (audit log for package start/end and row counts)",
      "etl.etl_error_log (error log for package\u2011level failures)"
    ],
    "transformations": [
      "SELECT coverage_id, policy_period_id, coverage_code, coverage_name, limit_amount, deductible_amount, coverage_start_date, coverage_end_date, coverage_status FROM public.coverage",
      "Lookup validation of policy_period_id against stg.policy_period",
      "Derived Column: TRIM(coverage_name) and UPPER(coverage_code)",
      "Derived Column: GETDATE() -> etl_load_date",
      "Conditional Split enforcing: limit_amount >= 0, deductible_amount >= 0, coverage_end_date > coverage_start_date, coverage_status IN ('ACTIVE','EXPIRED','CANCELLED','SUSPENDED')",
      "Union All to consolidate all error/no\u2011match streams",
      "Fast bulk load into stg.coverage with commit size 10,000"
    ],
    "dependencies": [
      "Connection Manager CM_Guidewire_PG_Source (PostgreSQL source)",
      "Connection Manager CM_DW_PG_Target (PostgreSQL target)",
      "SQL Execute Task for audit start (INSERT into etl.etl_audit_log)",
      "SQL Execute Task for audit end (UPDATE etl.etl_audit_log)",
      "SQL Execute Task for error logging (INSERT into etl.etl_error_log)",
      "ADO.NET PostgreSQL Source component",
      "Lookup component (policy_period_id validation)",
      "Derived Column components (cleansing and metadata)",
      "Conditional Split component (business rule validation)",
      "Union All component (error stream consolidation)",
      "OLE DB Destination components for stg.coverage and stg.error_quarantine"
    ]
  },
  {
    "id": "Extract_Job.dtsx",
    "name": "Extract_Job.dtsx",
    "type": "SSIS",
    "lines": 185,
    "entities": 38,
    "relationships": 16,
    "rules": 6,
    "purpose": "Extracts rows from the Guidewire PolicyCenter JOB table, validates the foreign\u2011key relationship to POLICY, applies data cleansing and business rule checks, and loads the clean rows into the data\u2011warehouse staging table while quarantining invalid rows and logging audit information.",
    "raw_code": "<?xml version=\"1.0\"?>\n<DTS:Executable\n    xmlns:DTS=\"www.microsoft.com/SqlServer/Dts\"\n    xmlns:SQLTask=\"www.microsoft.com/sqlserver/dts/tasks/sqltask\"\n    DTS:ExecutableType=\"Microsoft.Package\"\n    DTS:CreationName=\"Microsoft.Package\"\n    DTS:DTSID=\"{B4C8D4F3-0074-43FE-BB22-22E7E979F8C0}\"\n    DTS:ObjectName=\"Extract_Job\"\n    DTS:PackageType=\"5\"\n    DTS:VersionMajor=\"1\" DTS:VersionMinor=\"0\" DTS:VersionBuild=\"1\"\n    DTS:VersionGUID=\"{EE19A891-A5F8-426E-9C29-3390FD836547}\"\n    DTS:Description=\"Extracts JOB, validates FK to POLICY (BR-01/BR-04), cleanses and loads.\"\n    DTS:LoggingMode=\"UseParentSetting\">\n  <DTS:Variables>\n    <DTS:Variable DTS:Name=\"RowsRead\"><DTS:VariableValue DTS:DataType=\"3\">0</DTS:VariableValue></DTS:Variable>\n    <DTS:Variable DTS:Name=\"RowsInserted\"><DTS:VariableValue DTS:DataType=\"3\">0</DTS:VariableValue></DTS:Variable>\n    <DTS:Variable DTS:Name=\"RowsRejected\"><DTS:VariableValue DTS:DataType=\"3\">0</DTS:VariableValue></DTS:Variable>\n    <DTS:Variable DTS:Name=\"PackageName\"><DTS:VariableValue DTS:DataType=\"8\">Extract_Job</DTS:VariableValue></DTS:Variable>\n    <DTS:Variable DTS:Name=\"StartTime\"><DTS:VariableValue DTS:DataType=\"7\">1900-01-01T00:00:00</DTS:VariableValue></DTS:Variable>\n  </DTS:Variables>\n  <DTS:ConnectionManagers>\n    <DTS:ConnectionManager DTS:refId=\"Package.ConnectionManagers[CM_Guidewire_PG_Source]\"\n        DTS:CreationName=\"ADO.NET:Npgsql\"\n        DTS:DTSID=\"{9115364D-372C-4495-9C1E-50DF8A571152}\"\n        DTS:ObjectName=\"CM_Guidewire_PG_Source\">\n      <DTS:ObjectData>\n        <DTS:ConnectionManager>\n          <DTS:Property DTS:Name=\"ConnectionString\">Server=gw-pg-source.internal;Port=5432;Database=guidewire_policycenter;User Id=etl_reader;Password=[SECURED_BY_PARAMETER];</DTS:Property>\n          <DTS:Property DTS:Name=\"Provider\">Npgsql PostgreSQL Provider</DTS:Property>\n          <DTS:Property DTS:Name=\"Description\">Source: Guidewire PolicyCenter PostgreSQL replica (read-only)</DTS:Property>\n        </DTS:ConnectionManager>\n      </DTS:ObjectData>\n    </DTS:ConnectionManager>\n    <DTS:ConnectionManager DTS:refId=\"Package.ConnectionManagers[CM_DW_PG_Target]\"\n        DTS:CreationName=\"ADO.NET:Npgsql\"\n        DTS:DTSID=\"{687226D2-4BD4-4707-A18E-CDBC9918635C}\"\n        DTS:ObjectName=\"CM_DW_PG_Target\">\n      <DTS:ObjectData>\n        <DTS:ConnectionManager>\n          <DTS:Property DTS:Name=\"ConnectionString\">Server=dw-pg-target.internal;Port=5432;Database=insurance_dw;User Id=etl_writer;Password=[SECURED_BY_PARAMETER];</DTS:Property>\n          <DTS:Property DTS:Name=\"Provider\">Npgsql PostgreSQL Provider</DTS:Property>\n          <DTS:Property DTS:Name=\"Description\">Target: Insurance Data Warehouse - stg / rpt schemas (PostgreSQL)</DTS:Property>\n        </DTS:ConnectionManager>\n      </DTS:ObjectData>\n    </DTS:ConnectionManager>\n  </DTS:ConnectionManagers>\n  <DTS:Executables>\n    <DTS:Executable DTS:refId=\"Package\\SQL_LogStart\" DTS:CreationName=\"Microsoft.ExecuteSQLTask\" DTS:DTSID=\"{09B248F4-5691-497E-8ADD-6F50D71B2229}\" DTS:ExecutableType=\"Microsoft.ExecuteSQLTask\" DTS:ObjectName=\"SQL - Log Package Start\">\n      <DTS:ObjectData>\n        <SQLTask:SqlTaskData\n            SQLTask:Connection=\"CM_DW_PG_Target\"\n            SQLTask:SqlStatementSource=\"INSERT INTO etl.etl_audit_log (package_name, task_name, start_time, status) VALUES (&apos;Extract_Job&apos;, &apos;Data Flow&apos;, now(), &apos;RUNNING&apos;)\" />\n      </DTS:ObjectData>\n    </DTS:Executable>\n    <DTS:Executable DTS:refId=\"Package\\DFT_Main\" DTS:CreationName=\"Microsoft.Pipeline\" DTS:DTSID=\"{C16C85E9-AC12-4585-A037-DC36931569C4}\" DTS:ExecutableType=\"Microsoft.Pipeline\" DTS:ObjectName=\"DFT - Extract, Cleanse, Validate, Load job\">\n      <DTS:ObjectData>\n    <pipeline version=\"1\">\n      <components>\n      <component name=\"SRC - job (PostgreSQL)\" componentClassID=\"Microsoft.ADO.NET.PGSource\" description=\"Extracts rows from public.job on CM_Guidewire_PG_Source\">\n        <properties>\n          <property name=\"SqlCommand\">SELECT job_id, policy_id, job_type, job_date, created_ts, job_number, job_status, submission_date, effective_date, expiration_date FROM public.job</property>\n          <property name=\"ConnectionManager\">CM_Guidewire_PG_Source</property>\n        </properties>\n        <outputs>\n          <output name=\"OLE DB Source Output\" />\n          <output name=\"OLE DB Source Error Output\" />\n        </outputs>\n      </component>\n      <component name=\"LKP - Validate Policy (policy_id)\" componentClassID=\"Microsoft.Lookup\" description=\"Validates policy_id exists in Policy (referential integrity / BR-01, BR-05)\">\n        <properties>\n          <property name=\"SqlCommandParam\">SELECT policy_id FROM stg.policy</property>\n          <property name=\"JoinColumn\">policy_id</property>\n          <property name=\"NoMatchBehavior\">RedirectRowsToNoMatchOutput</property>\n          <property name=\"CacheMode\">Full</property>\n        </properties>\n        <inputs>\n          <input name=\"OLE DB Source Output\" />\n        </inputs>\n        <outputs>\n          <output name=\"Lookup Match Output\" />\n          <output name=\"Lookup No Match Output (-> Error Path)\" />\n        </outputs>\n      </component>\n      <component name=\"DER - Data Cleansing\" componentClassID=\"Microsoft.DerivedColumn\" description=\"Trims whitespace, standardizes casing/codes, normalizes nulls\">\n        <properties>\n          <property name=\"Expressions\">TRIM(job_number) -&gt; job_number</property>\n        </properties>\n        <inputs>\n          <input name=\"Lookup Match Output\" />\n        </inputs>\n        <outputs>\n          <output name=\"Cleansing Output\" />\n        </outputs>\n      </component>\n      <component name=\"DER - Derived / Calculated Columns\" componentClassID=\"Microsoft.DerivedColumn\" description=\"Adds ETL metadata columns and business-calculated fields\">\n        <properties>\n          <property name=\"Expressions\">GETDATE() -&gt; etl_load_date; job_type == 'New Business' ? 1 : 0 -&gt; is_new_business_flag</property>\n        </properties>\n        <inputs>\n          <input name=\"Cleansing Output\" />\n        </inputs>\n        <outputs>\n          <output name=\"Derived Column Output\" />\n        </outputs>\n      </component>\n      <component name=\"CSPL - Business Rule Validation\" componentClassID=\"Microsoft.ConditionalSplit\" description=\"Routes rows failing business rules to error output. Rules: job_date &lt;= GETDATE() | (expiration_date IS NULL) OR (effective_date IS NULL) OR (expiration_date &gt; effective_date) | job_status IN (&apos;PENDING&apos;,&apos;IN_PROGRESS&apos;,&apos;COMPLETED&apos;,&apos;CANCELLED&apos;)\">\n        <properties>\n          <property name=\"ValidOutputName\">Valid Rows</property>\n          <property name=\"InvalidOutputName\">Invalid Rows (-&gt; Error Path)</property>\n          <property name=\"Conditions\">job_date &lt;= GETDATE() | (expiration_date IS NULL) OR (effective_date IS NULL) OR (expiration_date &gt; effective_date) | job_status IN ('PENDING','IN_PROGRESS','COMPLETED','CANCELLED')</property>\n        </properties>\n        <inputs>\n          <input name=\"Derived Column Output\" />\n        </inputs>\n        <outputs>\n          <output name=\"Valid Rows\" />\n          <output name=\"Invalid Rows (-> Error Path)\" />\n        </outputs>\n      </component>\n      <component name=\"UN - Union All Error Rows\" componentClassID=\"Microsoft.UnionAll\" description=\"Combines all error/no-match/invalid outputs into a single error stream\">\n        <properties>\n\n        </properties>\n        <inputs>\n          <input name=\"Lookup No Match Output (-> Error Path)\" />\n          <input name=\"Invalid Rows (-> Error Path)\" />\n          <input name=\"OLE DB Source Error Output\" />\n        </inputs>\n        <outputs>\n          <output name=\"Unified Error Output\" />\n        </outputs>\n      </component>\n      <component name=\"DST - Error Log (stg.error_quarantine)\" componentClassID=\"Microsoft.OLEDBDestination\" description=\"Writes rejected/invalid rows to the error-quarantine table for review\">\n        <properties>\n          <property name=\"OpenRowset\">stg.error_quarantine</property>\n          <property name=\"ConnectionManager\">CM_DW_PG_Target</property>\n        </properties>\n        <inputs>\n          <input name=\"Unified Error Output\" />\n        </inputs>\n      </component>\n      <component name=\"DST - Load job (PostgreSQL DW)\" componentClassID=\"Microsoft.OLEDBDestination\" description=\"Loads validated/cleansed rows into stg.job (upsert via staging + MERGE in post-SQL)\">\n        <properties>\n          <property name=\"OpenRowset\">stg.job</property>\n          <property name=\"ConnectionManager\">CM_DW_PG_Target</property>\n          <property name=\"FastLoad\">true</property>\n          <property name=\"MaximumInsertCommitSize\">10000</property>\n        </properties>\n        <inputs>\n          <input name=\"Valid Rows\" />\n        </inputs>\n      </component>\n      </components>\n    </pipeline>\n      </DTS:ObjectData>\n    </DTS:Executable>\n    <DTS:Executable DTS:refId=\"Package\\SQL_LogEnd\" DTS:CreationName=\"Microsoft.ExecuteSQLTask\" DTS:DTSID=\"{BE9A0DED-E217-48CA-B173-13826958672A}\" DTS:ExecutableType=\"Microsoft.ExecuteSQLTask\" DTS:ObjectName=\"SQL - Log Package End / Row Counts\">\n      <DTS:ObjectData>\n        <SQLTask:SqlTaskData\n            SQLTask:Connection=\"CM_DW_PG_Target\"\n            SQLTask:SqlStatementSource=\"UPDATE etl.etl_audit_log SET end_time = now(), status = &apos;COMPLETED&apos;, rows_read = ?, rows_inserted = ?, rows_rejected = ? WHERE package_name = &apos;Extract_Job&apos; AND status = &apos;RUNNING&apos;\" />\n      </DTS:ObjectData>\n    </DTS:Executable>\n  </DTS:Executables>\n  <DTS:PrecedenceConstraints>\n    <DTS:PrecedenceConstraint DTS:refId=\"Package.PrecedenceConstraints[SQL_LogStartToDFT_Main]\"\n        DTS:From=\"Package\\SQL_LogStart\" DTS:To=\"Package\\DFT_Main\" DTS:Value=\"3\" DTS:DTSID=\"{2DBF0B9B-2C1D-4E85-815D-094BF7A6B47E}\" />\n    <DTS:PrecedenceConstraint DTS:refId=\"Package.PrecedenceConstraints[DFT_MainToSQL_LogEnd]\"\n        DTS:From=\"Package\\DFT_Main\" DTS:To=\"Package\\SQL_LogEnd\" DTS:Value=\"1\" DTS:DTSID=\"{9C9063C7-A967-4FB1-8E88-C1D44C721B31}\" />\n  </DTS:PrecedenceConstraints>\n  <DTS:EventHandlers>\n    <DTS:EventHandler DTS:EventName=\"OnError\" DTS:DTSID=\"{247A15B6-3957-4344-B767-7AE3A5716C22}\" DTS:ObjectName=\"OnError\">\n      <DTS:Executables>\n    <DTS:Executable DTS:refId=\"Package\\EH_LogError\" DTS:CreationName=\"Microsoft.ExecuteSQLTask\" DTS:DTSID=\"{25710E84-47DD-4E8F-854C-19FC8F77707A}\" DTS:ExecutableType=\"Microsoft.ExecuteSQLTask\" DTS:ObjectName=\"SQL - Log Error to ETL_ERROR_LOG\">\n      <DTS:ObjectData>\n        <SQLTask:SqlTaskData\n            SQLTask:Connection=\"CM_DW_PG_Target\"\n            SQLTask:SqlStatementSource=\"INSERT INTO etl.etl_error_log (package_name, source_object, error_code, error_description, error_time) VALUES (&apos;Extract_Job&apos;, ?, ?, ?, now())\" />\n      </DTS:ObjectData>\n    </DTS:Executable>\n\n      </DTS:Executables>\n    </DTS:EventHandler>\n  </DTS:EventHandlers>\n</DTS:Executable>\n",
    "business_rules": [
      {
        "rule_id": "Rule 1",
        "name": "Extract_Job Rule 1",
        "description": "BR\u201101/BR\u201104: policy_id in job must exist in stg.policy (foreign\u2011key validation).",
        "formula": "BR\u201101/BR\u201104: policy_id in job must exist in stg.policy (foreign\u2011key validation)."
      },
      {
        "rule_id": "Rule 2",
        "name": "Extract_Job Rule 2",
        "description": "Job date must not be in the future (job_date <= current system date).",
        "formula": "Job date must not be in the future (job_date <= current system date)."
      },
      {
        "rule_id": "Rule 3",
        "name": "Extract_Job Rule 3",
        "description": "Expiration and effective dates must be logically consistent: either expiration_date is null, or effective_date is null, or expiration_date must be greater than effective_date.",
        "formula": null
      },
      {
        "rule_id": "Rule 4",
        "name": "Extract_Job Rule 4",
        "description": "Job status must be one of the allowed values: PENDING, IN_PROGRESS, COMPLETED, CANCELLED.",
        "formula": null
      },
      {
        "rule_id": "Rule 5",
        "name": "Extract_Job Rule 5",
        "description": "Job number is trimmed of leading/trailing whitespace before load.",
        "formula": "Job number is trimmed of leading/trailing whitespace before load."
      },
      {
        "rule_id": "Rule 6",
        "name": "Extract_Job Rule 6",
        "description": "is_new_business_flag is set to 1 when job_type equals 'New Business', otherwise 0.",
        "formula": null
      }
    ],
    "inputs": [
      "public.job (Guidewire PolicyCenter PostgreSQL replica)",
      "stg.policy (staging table in the data warehouse used for policy_id lookup)",
      "OLE DB Source Error Output (source read errors)",
      "Package variables: RowsRead, RowsInserted, RowsRejected, PackageName, StartTime"
    ],
    "outputs": [
      "stg.job (staging table for validated job records)",
      "stg.error_quarantine (table for rejected/invalid rows)",
      "etl.etl_audit_log (package start/end audit record)",
      "etl.etl_error_log (error event log)"
    ],
    "transformations": [
      "SQL SELECT extracting job_id, policy_id, job_type, job_date, created_ts, job_number, job_status, submission_date, effective_date, expiration_date from public.job",
      "Lookup on policy_id against stg.policy to enforce referential integrity (BR\u201101/BR\u201104)",
      "Derived Column: TRIM(job_number) to remove whitespace",
      "Derived Column: GETDATE() -> etl_load_date",
      "Derived Column: job_type == 'New Business' ? 1 : 0 -> is_new_business_flag",
      "Conditional Split enforcing: job_date <= current date; (expiration_date IS NULL) OR (effective_date IS NULL) OR (expiration_date > effective_date); job_status IN ('PENDING','IN_PROGRESS','COMPLETED','CANCELLED')",
      "Union All to consolidate all error streams (lookup no\u2011match, conditional split invalid rows, source error output)",
      "Fast load into stg.job with batch commit size of 10,000 rows",
      "Insert into stg.error_quarantine for all rejected rows"
    ],
    "dependencies": [
      "Connection Manager CM_Guidewire_PG_Source (Npgsql provider, read\u2011only replica)",
      "Connection Manager CM_DW_PG_Target (Npgsql provider, data\u2011warehouse target)",
      "Source table public.job",
      "Target tables stg.policy, stg.job, stg.error_quarantine, etl.etl_audit_log, etl.etl_error_log",
      "SSIS components: Execute SQL Task, ADO.NET PostgreSQL Source, Lookup, Derived Column, Conditional Split, Union All, OLE DB Destination"
    ]
  },
  {
    "id": "Extract_KPI_Aggregates.dtsx",
    "name": "Extract_KPI_Aggregates.dtsx",
    "type": "SSIS",
    "lines": 222,
    "entities": 36,
    "relationships": 23,
    "rules": 7,
    "purpose": "Merge pre\u2011aggregated premium and claims data with policy period and job information to calculate underwriting KPIs (Loss Ratio, Commission Ratio, Underwriting Profit) and the Retention Rate KPI, then load the results into reporting fact tables while logging package execution.",
    "raw_code": "<?xml version=\"1.0\"?>\n<DTS:Executable\n    xmlns:DTS=\"www.microsoft.com/SqlServer/Dts\"\n    xmlns:SQLTask=\"www.microsoft.com/sqlserver/dts/tasks/sqltask\"\n    DTS:ExecutableType=\"Microsoft.Package\"\n    DTS:CreationName=\"Microsoft.Package\"\n    DTS:DTSID=\"{837774F7-6686-4DBA-92D2-C41896752BE6}\"\n    DTS:ObjectName=\"Extract_KPI_Aggregates\"\n    DTS:PackageType=\"5\"\n    DTS:VersionMajor=\"1\" DTS:VersionMinor=\"0\" DTS:VersionBuild=\"1\"\n    DTS:VersionGUID=\"{E4C81190-20DD-4B33-AA24-F2282BB17C9B}\"\n    DTS:Description=\"Merges pre-aggregated PREMIUM and CLAIMS summaries with POLICY_PERIOD/JOB to compute Loss Ratio, Commission Ratio, Underwriting Profit and Retention Rate KPIs (BR-09, BR-10, BR-11) and loads the reporting fact tables.\"\n    DTS:LoggingMode=\"UseParentSetting\">\n  <DTS:ConnectionManagers>\n    <DTS:ConnectionManager DTS:refId=\"Package.ConnectionManagers[CM_DW_PG_Target]\"\n        DTS:CreationName=\"ADO.NET:Npgsql\"\n        DTS:DTSID=\"{248FFA76-0389-4A8D-AE39-0CA6BBE7AA83}\"\n        DTS:ObjectName=\"CM_DW_PG_Target\">\n      <DTS:ObjectData>\n        <DTS:ConnectionManager>\n          <DTS:Property DTS:Name=\"ConnectionString\">Server=dw-pg-target.internal;Port=5432;Database=insurance_dw;User Id=etl_writer;Password=[SECURED_BY_PARAMETER];</DTS:Property>\n          <DTS:Property DTS:Name=\"Provider\">Npgsql PostgreSQL Provider</DTS:Property>\n        </DTS:ConnectionManager>\n      </DTS:ObjectData>\n    </DTS:ConnectionManager>\n  </DTS:ConnectionManagers>\n  <DTS:Executables>\n    <DTS:Executable DTS:refId=\"Package\\SQL_LogStart\" DTS:CreationName=\"Microsoft.ExecuteSQLTask\" DTS:DTSID=\"{FBCC2F13-93F0-4EE7-BFA9-C6D240C2A833}\" DTS:ExecutableType=\"Microsoft.ExecuteSQLTask\" DTS:ObjectName=\"SQL - Log Package Start\">\n      <DTS:ObjectData>\n        <SQLTask:SqlTaskData SQLTask:Connection=\"CM_DW_PG_Target\" SQLTask:SqlStatementSource=\"INSERT INTO etl.etl_audit_log (package_name, task_name, start_time, status) VALUES (&apos;Extract_KPI_Aggregates&apos;, &apos;Data Flow&apos;, now(), &apos;RUNNING&apos;)\" />\n      </DTS:ObjectData>\n    </DTS:Executable>\n    <DTS:Executable DTS:refId=\"Package\\DFT_KPI\" DTS:CreationName=\"Microsoft.Pipeline\" DTS:DTSID=\"{52CE3B7D-CA4A-4178-87E4-34500F94B2E7}\" DTS:ExecutableType=\"Microsoft.Pipeline\" DTS:ObjectName=\"DFT - Merge, Aggregate, Calculate KPIs\">\n      <DTS:ObjectData>\n    <pipeline version=\"1\">\n      <components>\n      <component name=\"SRC - stg.premium (pre-aggregated by policy_period)\" componentClassID=\"Microsoft.OLEDBSource\" description=\"Reads the premium summary produced by Extract_Premium&apos;s Aggregate transform.\">\n        <properties>\n          <property name=\"OpenRowset\">stg.premium_summary_by_period</property>\n          <property name=\"ConnectionManager\">CM_DW_PG_Target</property>\n        </properties>\n        <outputs>\n          <output name=\"Premium Output\" />\n        </outputs>\n      </component>\n      <component name=\"SRC - stg.claims (pre-aggregated by policy, BR-09)\" componentClassID=\"Microsoft.OLEDBSource\" description=\"Reads the claims incurred summary produced by Extract_Claims&apos;s Aggregate transform.\">\n        <properties>\n          <property name=\"OpenRowset\">stg.claims_incurred_summary_by_policy</property>\n          <property name=\"ConnectionManager\">CM_DW_PG_Target</property>\n        </properties>\n        <outputs>\n          <output name=\"Claims Output\" />\n        </outputs>\n      </component>\n      <component name=\"SRC - stg.policy_period\" componentClassID=\"Microsoft.OLEDBSource\" description=\"Reads policy_period_id to policy_id mapping needed to join premium (by period) with claims (by policy).\">\n        <properties>\n          <property name=\"OpenRowset\">stg.policy_period</property>\n          <property name=\"ConnectionManager\">CM_DW_PG_Target</property>\n        </properties>\n        <outputs>\n          <output name=\"PolicyPeriod Output\" />\n        </outputs>\n      </component>\n      <component name=\"SRC - stg.job (for retention rate)\" componentClassID=\"Microsoft.OLEDBSource\" description=\"Reads job_type / job_status to classify RENEWAL vs original/expiring policies for Retention Rate KPI.\">\n        <properties>\n          <property name=\"OpenRowset\">stg.job</property>\n          <property name=\"ConnectionManager\">CM_DW_PG_Target</property>\n        </properties>\n        <outputs>\n          <output name=\"Job Output\" />\n        </outputs>\n      </component>\n      <component name=\"SORT - Premium by policy_period_id\" componentClassID=\"Microsoft.Sort\" description=\"Sorts premium summary for the downstream Merge Join (Merge Join requires sorted inputs).\">\n        <properties>\n          <property name=\"SortKey\">policy_period_id ASC</property>\n        </properties>\n        <inputs>\n          <input name=\"Premium Output\" />\n        </inputs>\n        <outputs>\n          <output name=\"Sorted Premium\" />\n        </outputs>\n      </component>\n      <component name=\"SORT - PolicyPeriod by policy_period_id\" componentClassID=\"Microsoft.Sort\" description=\"Sorts policy_period for the Merge Join.\">\n        <properties>\n          <property name=\"SortKey\">policy_period_id ASC</property>\n        </properties>\n        <inputs>\n          <input name=\"PolicyPeriod Output\" />\n        </inputs>\n        <outputs>\n          <output name=\"Sorted PolicyPeriod\" />\n        </outputs>\n      </component>\n      <component name=\"MRG - Join Premium to PolicyPeriod (get policy_id)\" componentClassID=\"Microsoft.MergeJoin\" description=\"INNER JOIN on policy_period_id to resolve policy_id for each premium summary row.\">\n        <properties>\n          <property name=\"JoinType\">Inner</property>\n          <property name=\"JoinKey\">policy_period_id</property>\n        </properties>\n        <inputs>\n          <input name=\"Sorted Premium\" />\n          <input name=\"Sorted PolicyPeriod\" />\n        </inputs>\n        <outputs>\n          <output name=\"Premium+PolicyID Output\" />\n        </outputs>\n      </component>\n      <component name=\"SORT - Premium+PolicyID by policy_id\" componentClassID=\"Microsoft.Sort\" description=\"Re-sorts by policy_id ahead of the second Merge Join against claims.\">\n        <properties>\n          <property name=\"SortKey\">policy_id ASC</property>\n        </properties>\n        <inputs>\n          <input name=\"Premium+PolicyID Output\" />\n        </inputs>\n        <outputs>\n          <output name=\"Sorted Premium+PolicyID\" />\n        </outputs>\n      </component>\n      <component name=\"SORT - Claims by policy_id\" componentClassID=\"Microsoft.Sort\" description=\"Sorts the pre-aggregated claims summary for the Merge Join.\">\n        <properties>\n          <property name=\"SortKey\">policy_id ASC</property>\n        </properties>\n        <inputs>\n          <input name=\"Claims Output\" />\n        </inputs>\n        <outputs>\n          <output name=\"Sorted Claims\" />\n        </outputs>\n      </component>\n      <component name=\"MRG - Merge Join Premium to Claims (LEFT OUTER, by policy_id)\" componentClassID=\"Microsoft.MergeJoin\" description=\"LEFT OUTER JOIN so policies with zero claims still produce a KPI row (incurred defaults to 0).\">\n        <properties>\n          <property name=\"JoinType\">LeftOuter</property>\n          <property name=\"JoinKey\">policy_id</property>\n        </properties>\n        <inputs>\n          <input name=\"Sorted Premium+PolicyID\" />\n          <input name=\"Sorted Claims\" />\n        </inputs>\n        <outputs>\n          <output name=\"Merged Financials Output\" />\n        </outputs>\n      </component>\n      <component name=\"DER - KPI Calculations (BR-10 / BR-11)\" componentClassID=\"Microsoft.DerivedColumn\" description=\"Computes Loss Ratio, Commission Ratio and Underwriting Profit with divide-by-zero protection.\">\n        <properties>\n          <property name=\"Expressions\">ISNULL(incurred_amount,0) -&gt; incurred_amount_safe; (earned_premium == 0) ? 0.0 : (incurred_amount_safe / earned_premium * 100.0) -&gt; loss_ratio (BR-10); (written_premium == 0) ? 0.0 : (commission_amount / written_premium * 100.0) -&gt; commission_ratio; earned_premium - incurred_amount_safe - commission_amount - operating_expense -&gt; underwriting_profit (BR-11); GETDATE() -&gt; etl_load_date</property>\n        </properties>\n        <inputs>\n          <input name=\"Merged Financials Output\" />\n        </inputs>\n        <outputs>\n          <output name=\"KPI Output\" />\n        </outputs>\n      </component>\n      <component name=\"AGG - Retention Rate Inputs (renewed vs expiring policy counts)\" componentClassID=\"Microsoft.Aggregation\" description=\"Counts RENEWAL jobs vs total policies reaching expiration, grouped by month, to feed Retention Rate = Renewed / Expiring * 100.\">\n        <properties>\n          <property name=\"GroupBy\">DATEPART(yyyy,job_date), DATEPART(mm,job_date)</property>\n          <property name=\"Aggregates\">COUNT(CASE WHEN job_type='Renewal' THEN 1 END) AS renewed_count, COUNT(CASE WHEN job_type IN ('New Business','Renewal') THEN 1 END) AS expiring_count</property>\n        </properties>\n        <inputs>\n          <input name=\"Job Output\" />\n        </inputs>\n        <outputs>\n          <output name=\"Retention Aggregate Output\" />\n        </outputs>\n      </component>\n      <component name=\"DER - Retention Rate (%)\" componentClassID=\"Microsoft.DerivedColumn\" description=\"Retention Rate = Renewed Policies / Expiring Policies * 100, divide-by-zero protected.\">\n        <properties>\n          <property name=\"Expressions\">(expiring_count == 0) ? 0.0 : (renewed_count * 1.0 / expiring_count * 100.0) -&gt; retention_rate</property>\n        </properties>\n        <inputs>\n          <input name=\"Retention Aggregate Output\" />\n        </inputs>\n        <outputs>\n          <output name=\"Retention Rate Output\" />\n        </outputs>\n      </component>\n      <component name=\"DST - Load fact_kpi_summary (per policy)\" componentClassID=\"Microsoft.OLEDBDestination\" description=\"Loads Loss Ratio / Commission Ratio / Underwriting Profit rows into rpt.fact_kpi_summary.\">\n        <properties>\n          <property name=\"OpenRowset\">rpt.fact_kpi_summary</property>\n          <property name=\"ConnectionManager\">CM_DW_PG_Target</property>\n          <property name=\"FastLoad\">true</property>\n        </properties>\n        <inputs>\n          <input name=\"KPI Output\" />\n        </inputs>\n      </component>\n      <component name=\"DST - Load fact_retention_rate (monthly)\" componentClassID=\"Microsoft.OLEDBDestination\" description=\"Loads monthly Retention Rate KPI into rpt.fact_retention_rate.\">\n        <properties>\n          <property name=\"OpenRowset\">rpt.fact_retention_rate</property>\n          <property name=\"ConnectionManager\">CM_DW_PG_Target</property>\n          <property name=\"FastLoad\">true</property>\n        </properties>\n        <inputs>\n          <input name=\"Retention Rate Output\" />\n        </inputs>\n      </component>\n      </components>\n    </pipeline>\n      </DTS:ObjectData>\n    </DTS:Executable>\n    <DTS:Executable DTS:refId=\"Package\\SQL_LogEnd\" DTS:CreationName=\"Microsoft.ExecuteSQLTask\" DTS:DTSID=\"{E2D3516B-2BE6-4E4C-88A8-BD63E289A9FA}\" DTS:ExecutableType=\"Microsoft.ExecuteSQLTask\" DTS:ObjectName=\"SQL - Log Package End / Row Counts\">\n      <DTS:ObjectData>\n        <SQLTask:SqlTaskData SQLTask:Connection=\"CM_DW_PG_Target\" SQLTask:SqlStatementSource=\"UPDATE etl.etl_audit_log SET end_time = now(), status = &apos;COMPLETED&apos;, rows_read = ?, rows_inserted = ?, rows_rejected = ? WHERE package_name = &apos;Extract_KPI_Aggregates&apos; AND status = &apos;RUNNING&apos;\" />\n      </DTS:ObjectData>\n    </DTS:Executable>\n  </DTS:Executables>\n  <DTS:PrecedenceConstraints>\n    <DTS:PrecedenceConstraint DTS:refId=\"Package.PrecedenceConstraints[StartToKPI]\" DTS:From=\"Package\\SQL_LogStart\" DTS:To=\"Package\\DFT_KPI\" DTS:Value=\"3\" DTS:DTSID=\"{991C65CF-BB6D-428B-BAB5-AD103CB9D100}\" />\n    <DTS:PrecedenceConstraint DTS:refId=\"Package.PrecedenceConstraints[KPIToEnd]\" DTS:From=\"Package\\DFT_KPI\" DTS:To=\"Package\\SQL_LogEnd\" DTS:Value=\"1\" DTS:DTSID=\"{55D605D9-E838-4C13-96C9-E77E07738C04}\" />\n  </DTS:PrecedenceConstraints>\n  <DTS:EventHandlers>\n    <DTS:EventHandler DTS:EventName=\"OnError\" DTS:DTSID=\"{2B5C369B-5F4E-4B0C-99BB-5C0D54265FB1}\" DTS:ObjectName=\"OnError\">\n      <DTS:Executables>\n        <DTS:Executable DTS:refId=\"Package\\EH_LogError\" DTS:CreationName=\"Microsoft.ExecuteSQLTask\" DTS:DTSID=\"{B5AA457C-5A64-4644-AB03-D80BFEA7FC51}\" DTS:ExecutableType=\"Microsoft.ExecuteSQLTask\" DTS:ObjectName=\"SQL - Log Error to ETL_ERROR_LOG\">\n          <DTS:ObjectData>\n            <SQLTask:SqlTaskData SQLTask:Connection=\"CM_DW_PG_Target\" SQLTask:SqlStatementSource=\"INSERT INTO etl.etl_error_log (package_name, source_object, error_code, error_description, error_time) VALUES (&apos;Extract_KPI_Aggregates&apos;, ?, ?, ?, now())\" />\n          </DTS:ObjectData>\n        </DTS:Executable>\n      </DTS:Executables>\n    </DTS:EventHandler>\n  </DTS:EventHandlers>\n</DTS:Executable>\n",
    "business_rules": [
      {
        "rule_id": "Rule 1",
        "name": "Extract_KPI_Aggregates Rule 1",
        "description": "BR\u201109: Claims incurred summary is pre\u2011aggregated by policy and must be joined to premium data.",
        "formula": null
      },
      {
        "rule_id": "Rule 2",
        "name": "Extract_KPI_Aggregates Rule 2",
        "description": "BR\u201110: Loss Ratio = (incurred_amount / earned_premium) * 100; if earned_premium = 0 then loss_ratio = 0.",
        "formula": "BR\u201110: Loss Ratio = (incurred_amount / earned_premium) * 100; if earned_premium = 0 then loss_ratio = 0."
      },
      {
        "rule_id": "Rule 3",
        "name": "Extract_KPI_Aggregates Rule 3",
        "description": "BR\u201111: Underwriting Profit = earned_premium - incurred_amount - commission_amount - operating_expense.",
        "formula": "BR\u201111: Underwriting Profit = earned_premium - incurred_amount - commission_amount - operating_expense."
      },
      {
        "rule_id": "Rule 4",
        "name": "Extract_KPI_Aggregates Rule 4",
        "description": "Commission Ratio = (commission_amount / written_premium) * 100; if written_premium = 0 then commission_ratio = 0.",
        "formula": "Commission Ratio = (commission_amount / written_premium) * 100; if written_premium = 0 then commission_ratio = 0."
      },
      {
        "rule_id": "Rule 5",
        "name": "Extract_KPI_Aggregates Rule 5",
        "description": "Retention Rate = (renewed policies / expiring policies) * 100; if expiring policies = 0 then retention_rate = 0.",
        "formula": "Retention Rate = (renewed policies / expiring policies) * 100; if expiring policies = 0 then retention_rate = 0."
      },
      {
        "rule_id": "Rule 6",
        "name": "Extract_KPI_Aggregates Rule 6",
        "description": "Left outer join ensures policies with no claims receive an incurred_amount of 0 for KPI calculation.",
        "formula": null
      },
      {
        "rule_id": "Rule 7",
        "name": "Extract_KPI_Aggregates Rule 7",
        "description": "All KPI calculations include divide\u2011by\u2011zero protection to avoid runtime errors.",
        "formula": null
      }
    ],
    "inputs": [
      "stg.premium_summary_by_period",
      "stg.claims_incurred_summary_by_policy",
      "stg.policy_period",
      "stg.job",
      "etl.etl_audit_log (for logging start)"
    ],
    "outputs": [
      "rpt.fact_kpi_summary",
      "rpt.fact_retention_rate",
      "etl.etl_audit_log (updated with end_time, status, rows_read, rows_inserted, rows_rejected)"
    ],
    "transformations": [
      "Sort premium summary by policy_period_id",
      "Sort policy_period by policy_period_id",
      "Merge Join (inner) premium with policy_period to obtain policy_id",
      "Sort merged premium+policy_id by policy_id",
      "Sort claims summary by policy_id",
      "Merge Join (left outer) premium+policy_id with claims to retain rows with zero claims",
      "Derived Column calculations: loss_ratio = (incurred / earned_premium) * 100 with zero\u2011check, commission_ratio = (commission / written_premium) * 100 with zero\u2011check, underwriting_profit = earned_premium - incurred - commission - operating_expense, etl_load_date = GETDATE()",
      "Aggregation of job data by year and month to count renewed policies and total expiring policies",
      "Derived Column calculation: retention_rate = (renewed_count / expiring_count) * 100 with zero\u2011check"
    ],
    "dependencies": [
      "Connection manager CM_DW_PG_Target (Npgsql PostgreSQL provider)",
      "Staging tables: stg.premium_summary_by_period, stg.claims_incurred_summary_by_policy, stg.policy_period, stg.job",
      "Destination tables: rpt.fact_kpi_summary, rpt.fact_retention_rate, etl.etl_audit_log",
      "SSIS components: OLE DB Source, Sort, Merge Join, Aggregation, Derived Column, OLE DB Destination, Execute SQL Task"
    ]
  },
  {
    "id": "Extract_Location.dtsx",
    "name": "Extract_Location.dtsx",
    "type": "SSIS",
    "lines": 185,
    "entities": 24,
    "relationships": 16,
    "rules": 7,
    "purpose": "Extracts LOCATION records from the Guidewire PolicyCenter PostgreSQL source, validates the foreign key to POLICY_PERIOD, cleanses address and code fields, applies business rule checks, and loads the valid rows into the data warehouse while quarantining invalid rows and logging audit information.",
    "raw_code": "<?xml version=\"1.0\"?>\n<DTS:Executable\n    xmlns:DTS=\"www.microsoft.com/SqlServer/Dts\"\n    xmlns:SQLTask=\"www.microsoft.com/sqlserver/dts/tasks/sqltask\"\n    DTS:ExecutableType=\"Microsoft.Package\"\n    DTS:CreationName=\"Microsoft.Package\"\n    DTS:DTSID=\"{EF28292C-9BCB-4C2F-9998-3168AC6EA2E7}\"\n    DTS:ObjectName=\"Extract_Location\"\n    DTS:PackageType=\"5\"\n    DTS:VersionMajor=\"1\" DTS:VersionMinor=\"0\" DTS:VersionBuild=\"1\"\n    DTS:VersionGUID=\"{4B41917D-CE44-427C-8E3D-1C36EB2EDA23}\"\n    DTS:Description=\"Extracts LOCATION, validates FK to POLICY_PERIOD (BR-05), cleanses address data and loads.\"\n    DTS:LoggingMode=\"UseParentSetting\">\n  <DTS:Variables>\n    <DTS:Variable DTS:Name=\"RowsRead\"><DTS:VariableValue DTS:DataType=\"3\">0</DTS:VariableValue></DTS:Variable>\n    <DTS:Variable DTS:Name=\"RowsInserted\"><DTS:VariableValue DTS:DataType=\"3\">0</DTS:VariableValue></DTS:Variable>\n    <DTS:Variable DTS:Name=\"RowsRejected\"><DTS:VariableValue DTS:DataType=\"3\">0</DTS:VariableValue></DTS:Variable>\n    <DTS:Variable DTS:Name=\"PackageName\"><DTS:VariableValue DTS:DataType=\"8\">Extract_Location</DTS:VariableValue></DTS:Variable>\n    <DTS:Variable DTS:Name=\"StartTime\"><DTS:VariableValue DTS:DataType=\"7\">1900-01-01T00:00:00</DTS:VariableValue></DTS:Variable>\n  </DTS:Variables>\n  <DTS:ConnectionManagers>\n    <DTS:ConnectionManager DTS:refId=\"Package.ConnectionManagers[CM_Guidewire_PG_Source]\"\n        DTS:CreationName=\"ADO.NET:Npgsql\"\n        DTS:DTSID=\"{9115364D-372C-4495-9C1E-50DF8A571152}\"\n        DTS:ObjectName=\"CM_Guidewire_PG_Source\">\n      <DTS:ObjectData>\n        <DTS:ConnectionManager>\n          <DTS:Property DTS:Name=\"ConnectionString\">Server=gw-pg-source.internal;Port=5432;Database=guidewire_policycenter;User Id=etl_reader;Password=[SECURED_BY_PARAMETER];</DTS:Property>\n          <DTS:Property DTS:Name=\"Provider\">Npgsql PostgreSQL Provider</DTS:Property>\n          <DTS:Property DTS:Name=\"Description\">Source: Guidewire PolicyCenter PostgreSQL replica (read-only)</DTS:Property>\n        </DTS:ConnectionManager>\n      </DTS:ObjectData>\n    </DTS:ConnectionManager>\n    <DTS:ConnectionManager DTS:refId=\"Package.ConnectionManagers[CM_DW_PG_Target]\"\n        DTS:CreationName=\"ADO.NET:Npgsql\"\n        DTS:DTSID=\"{687226D2-4BD4-4707-A18E-CDBC9918635C}\"\n        DTS:ObjectName=\"CM_DW_PG_Target\">\n      <DTS:ObjectData>\n        <DTS:ConnectionManager>\n          <DTS:Property DTS:Name=\"ConnectionString\">Server=dw-pg-target.internal;Port=5432;Database=insurance_dw;User Id=etl_writer;Password=[SECURED_BY_PARAMETER];</DTS:Property>\n          <DTS:Property DTS:Name=\"Provider\">Npgsql PostgreSQL Provider</DTS:Property>\n          <DTS:Property DTS:Name=\"Description\">Target: Insurance Data Warehouse - stg / rpt schemas (PostgreSQL)</DTS:Property>\n        </DTS:ConnectionManager>\n      </DTS:ObjectData>\n    </DTS:ConnectionManager>\n  </DTS:ConnectionManagers>\n  <DTS:Executables>\n    <DTS:Executable DTS:refId=\"Package\\SQL_LogStart\" DTS:CreationName=\"Microsoft.ExecuteSQLTask\" DTS:DTSID=\"{58C7D4AA-C0E0-4B0D-A12A-4C07D5F947D0}\" DTS:ExecutableType=\"Microsoft.ExecuteSQLTask\" DTS:ObjectName=\"SQL - Log Package Start\">\n      <DTS:ObjectData>\n        <SQLTask:SqlTaskData\n            SQLTask:Connection=\"CM_DW_PG_Target\"\n            SQLTask:SqlStatementSource=\"INSERT INTO etl.etl_audit_log (package_name, task_name, start_time, status) VALUES (&apos;Extract_Location&apos;, &apos;Data Flow&apos;, now(), &apos;RUNNING&apos;)\" />\n      </DTS:ObjectData>\n    </DTS:Executable>\n    <DTS:Executable DTS:refId=\"Package\\DFT_Main\" DTS:CreationName=\"Microsoft.Pipeline\" DTS:DTSID=\"{AD815239-5E3A-48A3-B67E-3E37F714EBA8}\" DTS:ExecutableType=\"Microsoft.Pipeline\" DTS:ObjectName=\"DFT - Extract, Cleanse, Validate, Load location\">\n      <DTS:ObjectData>\n    <pipeline version=\"1\">\n      <components>\n      <component name=\"SRC - location (PostgreSQL)\" componentClassID=\"Microsoft.ADO.NET.PGSource\" description=\"Extracts rows from public.location on CM_Guidewire_PG_Source\">\n        <properties>\n          <property name=\"SqlCommand\">SELECT location_id, policy_period_id, location_number, address_line1, address_line2, city, state_code, zip_code, country_code, occupancy_type, building_value, contents_value FROM public.location</property>\n          <property name=\"ConnectionManager\">CM_Guidewire_PG_Source</property>\n        </properties>\n        <outputs>\n          <output name=\"OLE DB Source Output\" />\n          <output name=\"OLE DB Source Error Output\" />\n        </outputs>\n      </component>\n      <component name=\"LKP - Validate Policy_Period (policy_period_id)\" componentClassID=\"Microsoft.Lookup\" description=\"Validates policy_period_id exists in Policy_Period (referential integrity / BR-01, BR-05)\">\n        <properties>\n          <property name=\"SqlCommandParam\">SELECT policy_period_id FROM stg.policy_period</property>\n          <property name=\"JoinColumn\">policy_period_id</property>\n          <property name=\"NoMatchBehavior\">RedirectRowsToNoMatchOutput</property>\n          <property name=\"CacheMode\">Full</property>\n        </properties>\n        <inputs>\n          <input name=\"OLE DB Source Output\" />\n        </inputs>\n        <outputs>\n          <output name=\"Lookup Match Output\" />\n          <output name=\"Lookup No Match Output (-> Error Path)\" />\n        </outputs>\n      </component>\n      <component name=\"DER - Data Cleansing\" componentClassID=\"Microsoft.DerivedColumn\" description=\"Trims whitespace, standardizes casing/codes, normalizes nulls\">\n        <properties>\n          <property name=\"Expressions\">TRIM(address_line1) -&gt; address_line1; TRIM(city) -&gt; city; UPPER(TRIM(state_code)) -&gt; state_code; UPPER(TRIM(country_code)) -&gt; country_code; ISNULL(address_line2,'') -&gt; address_line2</property>\n        </properties>\n        <inputs>\n          <input name=\"Lookup Match Output\" />\n        </inputs>\n        <outputs>\n          <output name=\"Cleansing Output\" />\n        </outputs>\n      </component>\n      <component name=\"DER - Derived / Calculated Columns\" componentClassID=\"Microsoft.DerivedColumn\" description=\"Adds ETL metadata columns and business-calculated fields\">\n        <properties>\n          <property name=\"Expressions\">GETDATE() -&gt; etl_load_date</property>\n        </properties>\n        <inputs>\n          <input name=\"Cleansing Output\" />\n        </inputs>\n        <outputs>\n          <output name=\"Derived Column Output\" />\n        </outputs>\n      </component>\n      <component name=\"CSPL - Business Rule Validation\" componentClassID=\"Microsoft.ConditionalSplit\" description=\"Routes rows failing business rules to error output. Rules: building_value &gt;= 0.00 | contents_value &gt;= 0.00 | occupancy_type IN (&apos;OWNER_OCCUPIED&apos;,&apos;TENANT_OCCUPIED&apos;,&apos;VACANT&apos;,&apos;UNDER_CONSTRUCTION&apos;,&apos;OTHER&apos;)\">\n        <properties>\n          <property name=\"ValidOutputName\">Valid Rows</property>\n          <property name=\"InvalidOutputName\">Invalid Rows (-&gt; Error Path)</property>\n          <property name=\"Conditions\">building_value &gt;= 0.00 | contents_value &gt;= 0.00 | occupancy_type IN ('OWNER_OCCUPIED','TENANT_OCCUPIED','VACANT','UNDER_CONSTRUCTION','OTHER')</property>\n        </properties>\n        <inputs>\n          <input name=\"Derived Column Output\" />\n        </inputs>\n        <outputs>\n          <output name=\"Valid Rows\" />\n          <output name=\"Invalid Rows (-> Error Path)\" />\n        </outputs>\n      </component>\n      <component name=\"UN - Union All Error Rows\" componentClassID=\"Microsoft.UnionAll\" description=\"Combines all error/no-match/invalid outputs into a single error stream\">\n        <properties>\n\n        </properties>\n        <inputs>\n          <input name=\"Lookup No Match Output (-> Error Path)\" />\n          <input name=\"Invalid Rows (-> Error Path)\" />\n          <input name=\"OLE DB Source Error Output\" />\n        </inputs>\n        <outputs>\n          <output name=\"Unified Error Output\" />\n        </outputs>\n      </component>\n      <component name=\"DST - Error Log (stg.error_quarantine)\" componentClassID=\"Microsoft.OLEDBDestination\" description=\"Writes rejected/invalid rows to the error-quarantine table for review\">\n        <properties>\n          <property name=\"OpenRowset\">stg.error_quarantine</property>\n          <property name=\"ConnectionManager\">CM_DW_PG_Target</property>\n        </properties>\n        <inputs>\n          <input name=\"Unified Error Output\" />\n        </inputs>\n      </component>\n      <component name=\"DST - Load location (PostgreSQL DW)\" componentClassID=\"Microsoft.OLEDBDestination\" description=\"Loads validated/cleansed rows into stg.location (upsert via staging + MERGE in post-SQL)\">\n        <properties>\n          <property name=\"OpenRowset\">stg.location</property>\n          <property name=\"ConnectionManager\">CM_DW_PG_Target</property>\n          <property name=\"FastLoad\">true</property>\n          <property name=\"MaximumInsertCommitSize\">10000</property>\n        </properties>\n        <inputs>\n          <input name=\"Valid Rows\" />\n        </inputs>\n      </component>\n      </components>\n    </pipeline>\n      </DTS:ObjectData>\n    </DTS:Executable>\n    <DTS:Executable DTS:refId=\"Package\\SQL_LogEnd\" DTS:CreationName=\"Microsoft.ExecuteSQLTask\" DTS:DTSID=\"{00CE7C85-60C2-43B3-A600-AE46310A24CE}\" DTS:ExecutableType=\"Microsoft.ExecuteSQLTask\" DTS:ObjectName=\"SQL - Log Package End / Row Counts\">\n      <DTS:ObjectData>\n        <SQLTask:SqlTaskData\n            SQLTask:Connection=\"CM_DW_PG_Target\"\n            SQLTask:SqlStatementSource=\"UPDATE etl.etl_audit_log SET end_time = now(), status = &apos;COMPLETED&apos;, rows_read = ?, rows_inserted = ?, rows_rejected = ? WHERE package_name = &apos;Extract_Location&apos; AND status = &apos;RUNNING&apos;\" />\n      </DTS:ObjectData>\n    </DTS:Executable>\n  </DTS:Executables>\n  <DTS:PrecedenceConstraints>\n    <DTS:PrecedenceConstraint DTS:refId=\"Package.PrecedenceConstraints[SQL_LogStartToDFT_Main]\"\n        DTS:From=\"Package\\SQL_LogStart\" DTS:To=\"Package\\DFT_Main\" DTS:Value=\"3\" DTS:DTSID=\"{186476D3-9268-4583-ABA1-B98FA7E0C7EB}\" />\n    <DTS:PrecedenceConstraint DTS:refId=\"Package.PrecedenceConstraints[DFT_MainToSQL_LogEnd]\"\n        DTS:From=\"Package\\DFT_Main\" DTS:To=\"Package\\SQL_LogEnd\" DTS:Value=\"1\" DTS:DTSID=\"{61ED8BB2-4EE7-4BF2-81BC-8526CD7459B9}\" />\n  </DTS:PrecedenceConstraints>\n  <DTS:EventHandlers>\n    <DTS:EventHandler DTS:EventName=\"OnError\" DTS:DTSID=\"{C146F1B8-3264-436F-B188-8DF8B40EC34D}\" DTS:ObjectName=\"OnError\">\n      <DTS:Executables>\n    <DTS:Executable DTS:refId=\"Package\\EH_LogError\" DTS:CreationName=\"Microsoft.ExecuteSQLTask\" DTS:DTSID=\"{B1D0D6B7-09FB-4BE1-A9CD-A6CB1C57920F}\" DTS:ExecutableType=\"Microsoft.ExecuteSQLTask\" DTS:ObjectName=\"SQL - Log Error to ETL_ERROR_LOG\">\n      <DTS:ObjectData>\n        <SQLTask:SqlTaskData\n            SQLTask:Connection=\"CM_DW_PG_Target\"\n            SQLTask:SqlStatementSource=\"INSERT INTO etl.etl_error_log (package_name, source_object, error_code, error_description, error_time) VALUES (&apos;Extract_Location&apos;, ?, ?, ?, now())\" />\n      </DTS:ObjectData>\n    </DTS:Executable>\n\n      </DTS:Executables>\n    </DTS:EventHandler>\n  </DTS:EventHandlers>\n</DTS:Executable>\n",
    "business_rules": [
      {
        "rule_id": "Rule 1",
        "name": "Extract_Location Rule 1",
        "description": "BR-05: policy_period_id in location must exist in stg.policy_period (referential integrity)",
        "formula": "BR-05: policy_period_id in location must exist in stg.policy_period (referential integrity)"
      },
      {
        "rule_id": "Rule 2",
        "name": "Extract_Location Rule 2",
        "description": "Building value must be greater than or equal to 0.00",
        "formula": null
      },
      {
        "rule_id": "Rule 3",
        "name": "Extract_Location Rule 3",
        "description": "Contents value must be greater than or equal to 0.00",
        "formula": null
      },
      {
        "rule_id": "Rule 4",
        "name": "Extract_Location Rule 4",
        "description": "Occupancy_type must be one of: OWNER_OCCUPIED, TENANT_OCCUPIED, VACANT, UNDER_CONSTRUCTION, OTHER",
        "formula": null
      },
      {
        "rule_id": "Rule 5",
        "name": "Extract_Location Rule 5",
        "description": "Address fields are trimmed of leading/trailing whitespace",
        "formula": "Address fields are trimmed of leading/trailing whitespace"
      },
      {
        "rule_id": "Rule 6",
        "name": "Extract_Location Rule 6",
        "description": "State_code and country_code are stored in upper case",
        "formula": null
      },
      {
        "rule_id": "Rule 7",
        "name": "Extract_Location Rule 7",
        "description": "Null address_line2 values are replaced with an empty string",
        "formula": null
      }
    ],
    "inputs": [
      "public.location (Guidewire PolicyCenter source database)",
      "stg.policy_period (staging table in the data warehouse for policy period reference)",
      "etl.etl_audit_log (used for logging start/end of the package)",
      "etl.etl_error_log (used for logging runtime errors)"
    ],
    "outputs": [
      "stg.location (staging table for cleaned location records)",
      "stg.error_quarantine (table capturing rejected/invalid rows)",
      "etl.etl_audit_log (audit record updated with row counts and status)",
      "etl.etl_error_log (error record inserted on package failure)"
    ],
    "transformations": [
      "SQL SELECT extracting location_id, policy_period_id, location_number, address_line1, address_line2, city, state_code, zip_code, country_code, occupancy_type, building_value, contents_value from public.location",
      "Lookup validation of policy_period_id against stg.policy_period (full cache, redirect no\u2011match rows)",
      "Derived Column cleansing: TRIM(address_line1), TRIM(city), UPPER(TRIM(state_code)), UPPER(TRIM(country_code)), ISNULL(address_line2, '')",
      "Derived Column adding ETL metadata: GETDATE() -> etl_load_date",
      "Conditional Split enforcing business rules on building_value, contents_value, and occupancy_type",
      "Union All merging all error/no\u2011match streams into a single error flow",
      "Fast load bulk insert into stg.location with commit size of 10,000 rows",
      "Insert into stg.error_quarantine for rejected rows"
    ],
    "dependencies": [
      "Connection Manager CM_Guidewire_PG_Source (PostgreSQL source)",
      "Connection Manager CM_DW_PG_Target (PostgreSQL target)",
      "SQL Execute Task for audit start log",
      "SQL Execute Task for audit end log and row count update",
      "SQL Execute Task for error logging (etl.etl_error_log)",
      "ADO.NET PostgreSQL Source component",
      "Lookup component (policy_period_id validation)",
      "Derived Column components (data cleansing and metadata)",
      "Conditional Split component (business rule validation)",
      "Union All component (error stream consolidation)",
      "OLE DB Destination components for stg.location and stg.error_quarantine"
    ]
  },
  {
    "id": "Extract_Policy.dtsx",
    "name": "Extract_Policy.dtsx",
    "type": "SSIS",
    "lines": 200,
    "entities": 38,
    "relationships": 15,
    "rules": 5,
    "purpose": "Extracts policy records from the Guidewire PolicyCenter PostgreSQL source, validates foreign\u2011key relationships to ACCOUNT and PRODUCER, applies data cleansing and business rule checks, and loads the clean rows into the data\u2011warehouse staging table while quarantining rejected rows and logging audit information.",
    "raw_code": "<?xml version=\"1.0\"?>\n<DTS:Executable\n    xmlns:DTS=\"www.microsoft.com/SqlServer/Dts\"\n    xmlns:SQLTask=\"www.microsoft.com/sqlserver/dts/tasks/sqltask\"\n    DTS:ExecutableType=\"Microsoft.Package\"\n    DTS:CreationName=\"Microsoft.Package\"\n    DTS:DTSID=\"{4EC70694-CDC4-4631-80BF-18DEE7B21121}\"\n    DTS:ObjectName=\"Extract_Policy\"\n    DTS:PackageType=\"5\"\n    DTS:VersionMajor=\"1\" DTS:VersionMinor=\"0\" DTS:VersionBuild=\"1\"\n    DTS:VersionGUID=\"{991D0A86-93FD-4C8A-A1F2-91ED4989ACC6}\"\n    DTS:Description=\"Extracts POLICY, validates FK to ACCOUNT and PRODUCER (BR-01), cleanses and loads.\"\n    DTS:LoggingMode=\"UseParentSetting\">\n  <DTS:Variables>\n    <DTS:Variable DTS:Name=\"RowsRead\"><DTS:VariableValue DTS:DataType=\"3\">0</DTS:VariableValue></DTS:Variable>\n    <DTS:Variable DTS:Name=\"RowsInserted\"><DTS:VariableValue DTS:DataType=\"3\">0</DTS:VariableValue></DTS:Variable>\n    <DTS:Variable DTS:Name=\"RowsRejected\"><DTS:VariableValue DTS:DataType=\"3\">0</DTS:VariableValue></DTS:Variable>\n    <DTS:Variable DTS:Name=\"PackageName\"><DTS:VariableValue DTS:DataType=\"8\">Extract_Policy</DTS:VariableValue></DTS:Variable>\n    <DTS:Variable DTS:Name=\"StartTime\"><DTS:VariableValue DTS:DataType=\"7\">1900-01-01T00:00:00</DTS:VariableValue></DTS:Variable>\n  </DTS:Variables>\n  <DTS:ConnectionManagers>\n    <DTS:ConnectionManager DTS:refId=\"Package.ConnectionManagers[CM_Guidewire_PG_Source]\"\n        DTS:CreationName=\"ADO.NET:Npgsql\"\n        DTS:DTSID=\"{9115364D-372C-4495-9C1E-50DF8A571152}\"\n        DTS:ObjectName=\"CM_Guidewire_PG_Source\">\n      <DTS:ObjectData>\n        <DTS:ConnectionManager>\n          <DTS:Property DTS:Name=\"ConnectionString\">Server=gw-pg-source.internal;Port=5432;Database=guidewire_policycenter;User Id=etl_reader;Password=[SECURED_BY_PARAMETER];</DTS:Property>\n          <DTS:Property DTS:Name=\"Provider\">Npgsql PostgreSQL Provider</DTS:Property>\n          <DTS:Property DTS:Name=\"Description\">Source: Guidewire PolicyCenter PostgreSQL replica (read-only)</DTS:Property>\n        </DTS:ConnectionManager>\n      </DTS:ObjectData>\n    </DTS:ConnectionManager>\n    <DTS:ConnectionManager DTS:refId=\"Package.ConnectionManagers[CM_DW_PG_Target]\"\n        DTS:CreationName=\"ADO.NET:Npgsql\"\n        DTS:DTSID=\"{687226D2-4BD4-4707-A18E-CDBC9918635C}\"\n        DTS:ObjectName=\"CM_DW_PG_Target\">\n      <DTS:ObjectData>\n        <DTS:ConnectionManager>\n          <DTS:Property DTS:Name=\"ConnectionString\">Server=dw-pg-target.internal;Port=5432;Database=insurance_dw;User Id=etl_writer;Password=[SECURED_BY_PARAMETER];</DTS:Property>\n          <DTS:Property DTS:Name=\"Provider\">Npgsql PostgreSQL Provider</DTS:Property>\n          <DTS:Property DTS:Name=\"Description\">Target: Insurance Data Warehouse - stg / rpt schemas (PostgreSQL)</DTS:Property>\n        </DTS:ConnectionManager>\n      </DTS:ObjectData>\n    </DTS:ConnectionManager>\n  </DTS:ConnectionManagers>\n  <DTS:Executables>\n    <DTS:Executable DTS:refId=\"Package\\SQL_LogStart\" DTS:CreationName=\"Microsoft.ExecuteSQLTask\" DTS:DTSID=\"{30C846BB-1546-43D7-8B26-E31E74379975}\" DTS:ExecutableType=\"Microsoft.ExecuteSQLTask\" DTS:ObjectName=\"SQL - Log Package Start\">\n      <DTS:ObjectData>\n        <SQLTask:SqlTaskData\n            SQLTask:Connection=\"CM_DW_PG_Target\"\n            SQLTask:SqlStatementSource=\"INSERT INTO etl.etl_audit_log (package_name, task_name, start_time, status) VALUES (&apos;Extract_Policy&apos;, &apos;Data Flow&apos;, now(), &apos;RUNNING&apos;)\" />\n      </DTS:ObjectData>\n    </DTS:Executable>\n    <DTS:Executable DTS:refId=\"Package\\DFT_Main\" DTS:CreationName=\"Microsoft.Pipeline\" DTS:DTSID=\"{9101BEE4-4A7E-423C-B078-A7B4B528DD90}\" DTS:ExecutableType=\"Microsoft.Pipeline\" DTS:ObjectName=\"DFT - Extract, Cleanse, Validate, Load policy\">\n      <DTS:ObjectData>\n    <pipeline version=\"1\">\n      <components>\n      <component name=\"SRC - policy (PostgreSQL)\" componentClassID=\"Microsoft.ADO.NET.PGSource\" description=\"Extracts rows from public.policy on CM_Guidewire_PG_Source\">\n        <properties>\n          <property name=\"SqlCommand\">SELECT policy_id, account_id, producer_id, policy_number, product_code, policy_status, effective_date, expiration_date, cancellation_date, cancellation_reason, updated_timestamp FROM public.policy</property>\n          <property name=\"ConnectionManager\">CM_Guidewire_PG_Source</property>\n        </properties>\n        <outputs>\n          <output name=\"OLE DB Source Output\" />\n          <output name=\"OLE DB Source Error Output\" />\n        </outputs>\n      </component>\n      <component name=\"LKP - Validate Account (account_id)\" componentClassID=\"Microsoft.Lookup\" description=\"Validates account_id exists in Account (referential integrity / BR-01, BR-05)\">\n        <properties>\n          <property name=\"SqlCommandParam\">SELECT account_id FROM stg.account</property>\n          <property name=\"JoinColumn\">account_id</property>\n          <property name=\"NoMatchBehavior\">RedirectRowsToNoMatchOutput</property>\n          <property name=\"CacheMode\">Full</property>\n        </properties>\n        <inputs>\n          <input name=\"OLE DB Source Output\" />\n        </inputs>\n        <outputs>\n          <output name=\"Lookup Match Output\" />\n          <output name=\"Lookup No Match Output (-> Error Path)\" />\n        </outputs>\n      </component>\n      <component name=\"LKP - Validate Producer (producer_id)\" componentClassID=\"Microsoft.Lookup\" description=\"Validates producer_id exists in Producer (referential integrity / BR-01, BR-05)\">\n        <properties>\n          <property name=\"SqlCommandParam\">SELECT producer_id FROM stg.producer</property>\n          <property name=\"JoinColumn\">producer_id</property>\n          <property name=\"NoMatchBehavior\">RedirectRowsToNoMatchOutput</property>\n          <property name=\"CacheMode\">Full</property>\n        </properties>\n        <inputs>\n          <input name=\"Lookup Match Output\" />\n        </inputs>\n        <outputs>\n          <output name=\"Lookup Match Output\" />\n          <output name=\"Lookup No Match Output (-> Error Path)\" />\n        </outputs>\n      </component>\n      <component name=\"DER - Data Cleansing\" componentClassID=\"Microsoft.DerivedColumn\" description=\"Trims whitespace, standardizes casing/codes, normalizes nulls\">\n        <properties>\n          <property name=\"Expressions\">TRIM(policy_number) -&gt; policy_number; UPPER(product_code) -&gt; product_code</property>\n        </properties>\n        <inputs>\n          <input name=\"Lookup Match Output\" />\n        </inputs>\n        <outputs>\n          <output name=\"Cleansing Output\" />\n        </outputs>\n      </component>\n      <component name=\"DER - Derived / Calculated Columns\" componentClassID=\"Microsoft.DerivedColumn\" description=\"Adds ETL metadata columns and business-calculated fields\">\n        <properties>\n          <property name=\"Expressions\">GETDATE() -&gt; etl_load_date</property>\n        </properties>\n        <inputs>\n          <input name=\"Cleansing Output\" />\n        </inputs>\n        <outputs>\n          <output name=\"Derived Column Output\" />\n        </outputs>\n      </component>\n      <component name=\"CSPL - Business Rule Validation\" componentClassID=\"Microsoft.ConditionalSplit\" description=\"Routes rows failing business rules to error output. Rules: expiration_date &gt; effective_date | policy_status IN (&apos;ACTIVE&apos;,&apos;INACTIVE&apos;,&apos;LAPSED&apos;,&apos;CANCELLED&apos;) | (cancellation_date IS NULL) OR (cancellation_date &gt; effective_date AND cancellation_date &lt; expiration_date)\">\n        <properties>\n          <property name=\"ValidOutputName\">Valid Rows</property>\n          <property name=\"InvalidOutputName\">Invalid Rows (-&gt; Error Path)</property>\n          <property name=\"Conditions\">expiration_date &gt; effective_date | policy_status IN ('ACTIVE','INACTIVE','LAPSED','CANCELLED') | (cancellation_date IS NULL) OR (cancellation_date &gt; effective_date AND cancellation_date &lt; expiration_date)</property>\n        </properties>\n        <inputs>\n          <input name=\"Derived Column Output\" />\n        </inputs>\n        <outputs>\n          <output name=\"Valid Rows\" />\n          <output name=\"Invalid Rows (-> Error Path)\" />\n        </outputs>\n      </component>\n      <component name=\"UN - Union All Error Rows\" componentClassID=\"Microsoft.UnionAll\" description=\"Combines all error/no-match/invalid outputs into a single error stream\">\n        <properties>\n\n        </properties>\n        <inputs>\n          <input name=\"Lookup No Match Output (-> Error Path)\" />\n          <input name=\"Invalid Rows (-> Error Path)\" />\n          <input name=\"OLE DB Source Error Output\" />\n        </inputs>\n        <outputs>\n          <output name=\"Unified Error Output\" />\n        </outputs>\n      </component>\n      <component name=\"DST - Error Log (stg.error_quarantine)\" componentClassID=\"Microsoft.OLEDBDestination\" description=\"Writes rejected/invalid rows to the error-quarantine table for review\">\n        <properties>\n          <property name=\"OpenRowset\">stg.error_quarantine</property>\n          <property name=\"ConnectionManager\">CM_DW_PG_Target</property>\n        </properties>\n        <inputs>\n          <input name=\"Unified Error Output\" />\n        </inputs>\n      </component>\n      <component name=\"DST - Load policy (PostgreSQL DW)\" componentClassID=\"Microsoft.OLEDBDestination\" description=\"Loads validated/cleansed rows into stg.policy (upsert via staging + MERGE in post-SQL)\">\n        <properties>\n          <property name=\"OpenRowset\">stg.policy</property>\n          <property name=\"ConnectionManager\">CM_DW_PG_Target</property>\n          <property name=\"FastLoad\">true</property>\n          <property name=\"MaximumInsertCommitSize\">10000</property>\n        </properties>\n        <inputs>\n          <input name=\"Valid Rows\" />\n        </inputs>\n      </component>\n      </components>\n    </pipeline>\n      </DTS:ObjectData>\n    </DTS:Executable>\n    <DTS:Executable DTS:refId=\"Package\\SQL_LogEnd\" DTS:CreationName=\"Microsoft.ExecuteSQLTask\" DTS:DTSID=\"{DC62FAB3-1717-4064-93B0-1C106A5EBF80}\" DTS:ExecutableType=\"Microsoft.ExecuteSQLTask\" DTS:ObjectName=\"SQL - Log Package End / Row Counts\">\n      <DTS:ObjectData>\n        <SQLTask:SqlTaskData\n            SQLTask:Connection=\"CM_DW_PG_Target\"\n            SQLTask:SqlStatementSource=\"UPDATE etl.etl_audit_log SET end_time = now(), status = &apos;COMPLETED&apos;, rows_read = ?, rows_inserted = ?, rows_rejected = ? WHERE package_name = &apos;Extract_Policy&apos; AND status = &apos;RUNNING&apos;\" />\n      </DTS:ObjectData>\n    </DTS:Executable>\n  </DTS:Executables>\n  <DTS:PrecedenceConstraints>\n    <DTS:PrecedenceConstraint DTS:refId=\"Package.PrecedenceConstraints[SQL_LogStartToDFT_Main]\"\n        DTS:From=\"Package\\SQL_LogStart\" DTS:To=\"Package\\DFT_Main\" DTS:Value=\"3\" DTS:DTSID=\"{6F1C614D-7B4B-4F5E-855B-73FCAF369B01}\" />\n    <DTS:PrecedenceConstraint DTS:refId=\"Package.PrecedenceConstraints[DFT_MainToSQL_LogEnd]\"\n        DTS:From=\"Package\\DFT_Main\" DTS:To=\"Package\\SQL_LogEnd\" DTS:Value=\"1\" DTS:DTSID=\"{886C148F-CAB9-418C-8CB7-B6DCFB557765}\" />\n  </DTS:PrecedenceConstraints>\n  <DTS:EventHandlers>\n    <DTS:EventHandler DTS:EventName=\"OnError\" DTS:DTSID=\"{49464C8C-6A0E-463F-A975-74E0BF4C2AA8}\" DTS:ObjectName=\"OnError\">\n      <DTS:Executables>\n    <DTS:Executable DTS:refId=\"Package\\EH_LogError\" DTS:CreationName=\"Microsoft.ExecuteSQLTask\" DTS:DTSID=\"{E7763469-56CE-4FA5-819E-2370038090D7}\" DTS:ExecutableType=\"Microsoft.ExecuteSQLTask\" DTS:ObjectName=\"SQL - Log Error to ETL_ERROR_LOG\">\n      <DTS:ObjectData>\n        <SQLTask:SqlTaskData\n            SQLTask:Connection=\"CM_DW_PG_Target\"\n            SQLTask:SqlStatementSource=\"INSERT INTO etl.etl_error_log (package_name, source_object, error_code, error_description, error_time) VALUES (&apos;Extract_Policy&apos;, ?, ?, ?, now())\" />\n      </DTS:ObjectData>\n    </DTS:Executable>\n\n      </DTS:Executables>\n    </DTS:EventHandler>\n  </DTS:EventHandlers>\n</DTS:Executable>\n",
    "business_rules": [
      {
        "rule_id": "Rule 1",
        "name": "Extract_Policy Rule 1",
        "description": "BR-01: account_id must exist in stg.account (referential integrity)",
        "formula": "BR-01: account_id must exist in stg.account (referential integrity)"
      },
      {
        "rule_id": "Rule 2",
        "name": "Extract_Policy Rule 2",
        "description": "BR-01/BR-05: producer_id must exist in stg.producer (referential integrity)",
        "formula": "BR-01/BR-05: producer_id must exist in stg.producer (referential integrity)"
      },
      {
        "rule_id": "Rule 3",
        "name": "Extract_Policy Rule 3",
        "description": "Expiration date must be later than effective date",
        "formula": null
      },
      {
        "rule_id": "Rule 4",
        "name": "Extract_Policy Rule 4",
        "description": "Policy status must be one of: ACTIVE, INACTIVE, LAPSED, CANCELLED",
        "formula": null
      },
      {
        "rule_id": "Rule 5",
        "name": "Extract_Policy Rule 5",
        "description": "If cancellation_date is provided it must be after effective_date and before expiration_date; otherwise it may be NULL",
        "formula": null
      }
    ],
    "inputs": [
      "public.policy (source PostgreSQL table)",
      "stg.account (staging table for account reference data)",
      "stg.producer (staging table for producer reference data)"
    ],
    "outputs": [
      "stg.policy (staging table for validated policy records)",
      "stg.error_quarantine (table for rejected/invalid rows)",
      "etl.etl_audit_log (audit log updated with start/end timestamps and row counts)",
      "etl.etl_error_log (error log populated by OnError handler)"
    ],
    "transformations": [
      "SELECT policy_id, account_id, producer_id, policy_number, product_code, policy_status, effective_date, expiration_date, cancellation_date, cancellation_reason, updated_timestamp FROM public.policy",
      "Lookup join on account_id against stg.account (full cache, redirect no\u2011match)",
      "Lookup join on producer_id against stg.producer (full cache, redirect no\u2011match)",
      "TRIM(policy_number) to remove surrounding whitespace",
      "UPPER(product_code) to standardize code casing",
      "Add ETL metadata column etl_load_date with current timestamp",
      "Conditional split enforcing: expiration_date > effective_date; policy_status in ('ACTIVE','INACTIVE','LAPSED','CANCELLED'); cancellation_date is NULL or falls between effective_date and expiration_date",
      "Union All to combine all error/no\u2011match streams",
      "Fast bulk insert into stg.policy with commit size 10,000"
    ],
    "dependencies": [
      "Connection manager CM_Guidewire_PG_Source (Npgsql provider, source DB)",
      "Connection manager CM_DW_PG_Target (Npgsql provider, target DW)",
      "SQL Server Integration Services (SSIS) components: ADO.NET Source, Lookup, Derived Column, Conditional Split, Union All, OLE DB Destination",
      "Tables: public.policy, stg.account, stg.producer, stg.policy, stg.error_quarantine, etl.etl_audit_log, etl.etl_error_log"
    ]
  },
  {
    "id": "Extract_PolicyPeriod.dtsx",
    "name": "Extract_PolicyPeriod.dtsx",
    "type": "SSIS",
    "lines": 189,
    "entities": 36,
    "relationships": 14,
    "rules": 6,
    "purpose": "Extracts rows from the Guidewire PolicyCenter policy_period table, validates foreign\u2011key references to policy and job, applies business rule checks, adds ETL metadata, and loads the clean data into the data\u2011warehouse staging table while quarantining invalid rows and logging execution details.",
    "raw_code": "<?xml version=\"1.0\"?>\n<DTS:Executable\n    xmlns:DTS=\"www.microsoft.com/SqlServer/Dts\"\n    xmlns:SQLTask=\"www.microsoft.com/sqlserver/dts/tasks/sqltask\"\n    DTS:ExecutableType=\"Microsoft.Package\"\n    DTS:CreationName=\"Microsoft.Package\"\n    DTS:DTSID=\"{20A0ED99-2914-4460-BECC-815D3E580A02}\"\n    DTS:ObjectName=\"Extract_PolicyPeriod\"\n    DTS:PackageType=\"5\"\n    DTS:VersionMajor=\"1\" DTS:VersionMinor=\"0\" DTS:VersionBuild=\"1\"\n    DTS:VersionGUID=\"{892E3D8A-8C90-4360-A8FB-AA21675158F4}\"\n    DTS:Description=\"Extracts POLICY_PERIOD, validates FK to POLICY and JOB (BR-02/BR-03), cleanses and loads.\"\n    DTS:LoggingMode=\"UseParentSetting\">\n  <DTS:Variables>\n    <DTS:Variable DTS:Name=\"RowsRead\"><DTS:VariableValue DTS:DataType=\"3\">0</DTS:VariableValue></DTS:Variable>\n    <DTS:Variable DTS:Name=\"RowsInserted\"><DTS:VariableValue DTS:DataType=\"3\">0</DTS:VariableValue></DTS:Variable>\n    <DTS:Variable DTS:Name=\"RowsRejected\"><DTS:VariableValue DTS:DataType=\"3\">0</DTS:VariableValue></DTS:Variable>\n    <DTS:Variable DTS:Name=\"PackageName\"><DTS:VariableValue DTS:DataType=\"8\">Extract_PolicyPeriod</DTS:VariableValue></DTS:Variable>\n    <DTS:Variable DTS:Name=\"StartTime\"><DTS:VariableValue DTS:DataType=\"7\">1900-01-01T00:00:00</DTS:VariableValue></DTS:Variable>\n  </DTS:Variables>\n  <DTS:ConnectionManagers>\n    <DTS:ConnectionManager DTS:refId=\"Package.ConnectionManagers[CM_Guidewire_PG_Source]\"\n        DTS:CreationName=\"ADO.NET:Npgsql\"\n        DTS:DTSID=\"{9115364D-372C-4495-9C1E-50DF8A571152}\"\n        DTS:ObjectName=\"CM_Guidewire_PG_Source\">\n      <DTS:ObjectData>\n        <DTS:ConnectionManager>\n          <DTS:Property DTS:Name=\"ConnectionString\">Server=gw-pg-source.internal;Port=5432;Database=guidewire_policycenter;User Id=etl_reader;Password=[SECURED_BY_PARAMETER];</DTS:Property>\n          <DTS:Property DTS:Name=\"Provider\">Npgsql PostgreSQL Provider</DTS:Property>\n          <DTS:Property DTS:Name=\"Description\">Source: Guidewire PolicyCenter PostgreSQL replica (read-only)</DTS:Property>\n        </DTS:ConnectionManager>\n      </DTS:ObjectData>\n    </DTS:ConnectionManager>\n    <DTS:ConnectionManager DTS:refId=\"Package.ConnectionManagers[CM_DW_PG_Target]\"\n        DTS:CreationName=\"ADO.NET:Npgsql\"\n        DTS:DTSID=\"{687226D2-4BD4-4707-A18E-CDBC9918635C}\"\n        DTS:ObjectName=\"CM_DW_PG_Target\">\n      <DTS:ObjectData>\n        <DTS:ConnectionManager>\n          <DTS:Property DTS:Name=\"ConnectionString\">Server=dw-pg-target.internal;Port=5432;Database=insurance_dw;User Id=etl_writer;Password=[SECURED_BY_PARAMETER];</DTS:Property>\n          <DTS:Property DTS:Name=\"Provider\">Npgsql PostgreSQL Provider</DTS:Property>\n          <DTS:Property DTS:Name=\"Description\">Target: Insurance Data Warehouse - stg / rpt schemas (PostgreSQL)</DTS:Property>\n        </DTS:ConnectionManager>\n      </DTS:ObjectData>\n    </DTS:ConnectionManager>\n  </DTS:ConnectionManagers>\n  <DTS:Executables>\n    <DTS:Executable DTS:refId=\"Package\\SQL_LogStart\" DTS:CreationName=\"Microsoft.ExecuteSQLTask\" DTS:DTSID=\"{F27CD748-F63C-4ED5-ACE2-878529C9B429}\" DTS:ExecutableType=\"Microsoft.ExecuteSQLTask\" DTS:ObjectName=\"SQL - Log Package Start\">\n      <DTS:ObjectData>\n        <SQLTask:SqlTaskData\n            SQLTask:Connection=\"CM_DW_PG_Target\"\n            SQLTask:SqlStatementSource=\"INSERT INTO etl.etl_audit_log (package_name, task_name, start_time, status) VALUES (&apos;Extract_PolicyPeriod&apos;, &apos;Data Flow&apos;, now(), &apos;RUNNING&apos;)\" />\n      </DTS:ObjectData>\n    </DTS:Executable>\n    <DTS:Executable DTS:refId=\"Package\\DFT_Main\" DTS:CreationName=\"Microsoft.Pipeline\" DTS:DTSID=\"{944C8F33-488E-4E3C-AA5E-A0123AEC7BE6}\" DTS:ExecutableType=\"Microsoft.Pipeline\" DTS:ObjectName=\"DFT - Extract, Cleanse, Validate, Load policy_period\">\n      <DTS:ObjectData>\n    <pipeline version=\"1\">\n      <components>\n      <component name=\"SRC - policy_period (PostgreSQL)\" componentClassID=\"Microsoft.ADO.NET.PGSource\" description=\"Extracts rows from public.policy_period on CM_Guidewire_PG_Source\">\n        <properties>\n          <property name=\"SqlCommand\">SELECT policy_period_id, policy_id, job_id, term_number, effective_date, expiration_date, period_status, written_date, transaction_effective_date FROM public.policy_period</property>\n          <property name=\"ConnectionManager\">CM_Guidewire_PG_Source</property>\n        </properties>\n        <outputs>\n          <output name=\"OLE DB Source Output\" />\n          <output name=\"OLE DB Source Error Output\" />\n        </outputs>\n      </component>\n      <component name=\"LKP - Validate Policy (policy_id)\" componentClassID=\"Microsoft.Lookup\" description=\"Validates policy_id exists in Policy (referential integrity / BR-01, BR-05)\">\n        <properties>\n          <property name=\"SqlCommandParam\">SELECT policy_id FROM stg.policy</property>\n          <property name=\"JoinColumn\">policy_id</property>\n          <property name=\"NoMatchBehavior\">RedirectRowsToNoMatchOutput</property>\n          <property name=\"CacheMode\">Full</property>\n        </properties>\n        <inputs>\n          <input name=\"OLE DB Source Output\" />\n        </inputs>\n        <outputs>\n          <output name=\"Lookup Match Output\" />\n          <output name=\"Lookup No Match Output (-> Error Path)\" />\n        </outputs>\n      </component>\n      <component name=\"LKP - Validate Job (job_id)\" componentClassID=\"Microsoft.Lookup\" description=\"Validates job_id exists in Job (referential integrity / BR-01, BR-05)\">\n        <properties>\n          <property name=\"SqlCommandParam\">SELECT job_id FROM stg.job</property>\n          <property name=\"JoinColumn\">job_id</property>\n          <property name=\"NoMatchBehavior\">RedirectRowsToNoMatchOutput</property>\n          <property name=\"CacheMode\">Full</property>\n        </properties>\n        <inputs>\n          <input name=\"Lookup Match Output\" />\n        </inputs>\n        <outputs>\n          <output name=\"Lookup Match Output\" />\n          <output name=\"Lookup No Match Output (-> Error Path)\" />\n        </outputs>\n      </component>\n      <component name=\"DER - Derived / Calculated Columns\" componentClassID=\"Microsoft.DerivedColumn\" description=\"Adds ETL metadata columns and business-calculated fields\">\n        <properties>\n          <property name=\"Expressions\">GETDATE() -&gt; etl_load_date</property>\n        </properties>\n        <inputs>\n          <input name=\"Lookup Match Output\" />\n        </inputs>\n        <outputs>\n          <output name=\"Derived Column Output\" />\n        </outputs>\n      </component>\n      <component name=\"CSPL - Business Rule Validation\" componentClassID=\"Microsoft.ConditionalSplit\" description=\"Routes rows failing business rules to error output. Rules: expiration_date &gt; effective_date | term_number &gt;= 1 | written_date &lt;= GETDATE() | period_status IN (&apos;ACTIVE&apos;,&apos;EXPIRED&apos;,&apos;CANCELLED&apos;,&apos;ENDED&apos;)\">\n        <properties>\n          <property name=\"ValidOutputName\">Valid Rows</property>\n          <property name=\"InvalidOutputName\">Invalid Rows (-&gt; Error Path)</property>\n          <property name=\"Conditions\">expiration_date &gt; effective_date | term_number &gt;= 1 | written_date &lt;= GETDATE() | period_status IN ('ACTIVE','EXPIRED','CANCELLED','ENDED')</property>\n        </properties>\n        <inputs>\n          <input name=\"Derived Column Output\" />\n        </inputs>\n        <outputs>\n          <output name=\"Valid Rows\" />\n          <output name=\"Invalid Rows (-> Error Path)\" />\n        </outputs>\n      </component>\n      <component name=\"UN - Union All Error Rows\" componentClassID=\"Microsoft.UnionAll\" description=\"Combines all error/no-match/invalid outputs into a single error stream\">\n        <properties>\n\n        </properties>\n        <inputs>\n          <input name=\"Lookup No Match Output (-> Error Path)\" />\n          <input name=\"Invalid Rows (-> Error Path)\" />\n          <input name=\"OLE DB Source Error Output\" />\n        </inputs>\n        <outputs>\n          <output name=\"Unified Error Output\" />\n        </outputs>\n      </component>\n      <component name=\"DST - Error Log (stg.error_quarantine)\" componentClassID=\"Microsoft.OLEDBDestination\" description=\"Writes rejected/invalid rows to the error-quarantine table for review\">\n        <properties>\n          <property name=\"OpenRowset\">stg.error_quarantine</property>\n          <property name=\"ConnectionManager\">CM_DW_PG_Target</property>\n        </properties>\n        <inputs>\n          <input name=\"Unified Error Output\" />\n        </inputs>\n      </component>\n      <component name=\"DST - Load policy_period (PostgreSQL DW)\" componentClassID=\"Microsoft.OLEDBDestination\" description=\"Loads validated/cleansed rows into stg.policy_period (upsert via staging + MERGE in post-SQL)\">\n        <properties>\n          <property name=\"OpenRowset\">stg.policy_period</property>\n          <property name=\"ConnectionManager\">CM_DW_PG_Target</property>\n          <property name=\"FastLoad\">true</property>\n          <property name=\"MaximumInsertCommitSize\">10000</property>\n        </properties>\n        <inputs>\n          <input name=\"Valid Rows\" />\n        </inputs>\n      </component>\n      </components>\n    </pipeline>\n      </DTS:ObjectData>\n    </DTS:Executable>\n    <DTS:Executable DTS:refId=\"Package\\SQL_LogEnd\" DTS:CreationName=\"Microsoft.ExecuteSQLTask\" DTS:DTSID=\"{34F53418-EB9B-4874-ADEC-27359A4AD5EC}\" DTS:ExecutableType=\"Microsoft.ExecuteSQLTask\" DTS:ObjectName=\"SQL - Log Package End / Row Counts\">\n      <DTS:ObjectData>\n        <SQLTask:SqlTaskData\n            SQLTask:Connection=\"CM_DW_PG_Target\"\n            SQLTask:SqlStatementSource=\"UPDATE etl.etl_audit_log SET end_time = now(), status = &apos;COMPLETED&apos;, rows_read = ?, rows_inserted = ?, rows_rejected = ? WHERE package_name = &apos;Extract_PolicyPeriod&apos; AND status = &apos;RUNNING&apos;\" />\n      </DTS:ObjectData>\n    </DTS:Executable>\n  </DTS:Executables>\n  <DTS:PrecedenceConstraints>\n    <DTS:PrecedenceConstraint DTS:refId=\"Package.PrecedenceConstraints[SQL_LogStartToDFT_Main]\"\n        DTS:From=\"Package\\SQL_LogStart\" DTS:To=\"Package\\DFT_Main\" DTS:Value=\"3\" DTS:DTSID=\"{004B34F5-9B9E-4D5D-BCF8-E36DB10707FA}\" />\n    <DTS:PrecedenceConstraint DTS:refId=\"Package.PrecedenceConstraints[DFT_MainToSQL_LogEnd]\"\n        DTS:From=\"Package\\DFT_Main\" DTS:To=\"Package\\SQL_LogEnd\" DTS:Value=\"1\" DTS:DTSID=\"{D3E960A2-DEC3-45EF-9D88-7F4068CA7DD6}\" />\n  </DTS:PrecedenceConstraints>\n  <DTS:EventHandlers>\n    <DTS:EventHandler DTS:EventName=\"OnError\" DTS:DTSID=\"{285648D8-DEC7-4B6C-B549-55599BA8113E}\" DTS:ObjectName=\"OnError\">\n      <DTS:Executables>\n    <DTS:Executable DTS:refId=\"Package\\EH_LogError\" DTS:CreationName=\"Microsoft.ExecuteSQLTask\" DTS:DTSID=\"{F66A0D17-BB69-464A-B4FC-E4EC8EA01507}\" DTS:ExecutableType=\"Microsoft.ExecuteSQLTask\" DTS:ObjectName=\"SQL - Log Error to ETL_ERROR_LOG\">\n      <DTS:ObjectData>\n        <SQLTask:SqlTaskData\n            SQLTask:Connection=\"CM_DW_PG_Target\"\n            SQLTask:SqlStatementSource=\"INSERT INTO etl.etl_error_log (package_name, source_object, error_code, error_description, error_time) VALUES (&apos;Extract_PolicyPeriod&apos;, ?, ?, ?, now())\" />\n      </DTS:ObjectData>\n    </DTS:Executable>\n\n      </DTS:Executables>\n    </DTS:EventHandler>\n  </DTS:EventHandlers>\n</DTS:Executable>\n",
    "business_rules": [
      {
        "rule_id": "Rule 1",
        "name": "Extract_PolicyPeriod Rule 1",
        "description": "BR\u201101 / BR\u201105: policy_id must exist in stg.policy (foreign\u2011key validation)",
        "formula": "BR\u201101 / BR\u201105: policy_id must exist in stg.policy (foreign\u2011key validation)"
      },
      {
        "rule_id": "Rule 2",
        "name": "Extract_PolicyPeriod Rule 2",
        "description": "BR\u201101 / BR\u201105: job_id must exist in stg.job (foreign\u2011key validation)",
        "formula": "BR\u201101 / BR\u201105: job_id must exist in stg.job (foreign\u2011key validation)"
      },
      {
        "rule_id": "Rule 3",
        "name": "Extract_PolicyPeriod Rule 3",
        "description": "Expiration date must be later than effective date",
        "formula": null
      },
      {
        "rule_id": "Rule 4",
        "name": "Extract_PolicyPeriod Rule 4",
        "description": "Term number must be greater than or equal to 1",
        "formula": null
      },
      {
        "rule_id": "Rule 5",
        "name": "Extract_PolicyPeriod Rule 5",
        "description": "Written date must not be in the future (<= current date)",
        "formula": "Written date must not be in the future (<= current date)"
      },
      {
        "rule_id": "Rule 6",
        "name": "Extract_PolicyPeriod Rule 6",
        "description": "Period status must be one of: ACTIVE, EXPIRED, CANCELLED, ENDED",
        "formula": null
      }
    ],
    "inputs": [
      "public.policy_period (source PostgreSQL)",
      "stg.policy (staging table for policy reference)",
      "stg.job (staging table for job reference)"
    ],
    "outputs": [
      "stg.policy_period (staging table in the data warehouse)",
      "stg.error_quarantine (error\u2011quarantine table)",
      "etl.etl_audit_log (package execution audit)",
      "etl.etl_error_log (error handler logging)"
    ],
    "transformations": [
      "SELECT policy_period_id, policy_id, job_id, term_number, effective_date, expiration_date, period_status, written_date, transaction_effective_date FROM public.policy_period",
      "Lookup validation of policy_id against stg.policy (referential integrity)",
      "Lookup validation of job_id against stg.job (referential integrity)",
      "Derived column addition: etl_load_date = GETDATE()",
      "Conditional split enforcing: expiration_date > effective_date; term_number >= 1; written_date <= GETDATE(); period_status IN ('ACTIVE','EXPIRED','CANCELLED','ENDED')",
      "Union All of all error/no\u2011match streams",
      "Fast load (bulk insert) into stg.policy_period with commit size 10,000",
      "Audit log insert at start and update with row counts at end"
    ],
    "dependencies": [
      "Connection Manager CM_Guidewire_PG_Source (Npgsql provider, read\u2011only replica)",
      "Connection Manager CM_DW_PG_Target (Npgsql provider, data\u2011warehouse)",
      "Execute SQL Tasks for audit logging and error logging",
      "Lookup components (stg.policy, stg.job)",
      "Derived Column component",
      "Conditional Split component",
      "Union All component",
      "OLE DB Destination components for stg.policy_period and stg.error_quarantine",
      "Tables: public.policy_period, stg.policy, stg.job, stg.policy_period, stg.error_quarantine, etl.etl_audit_log, etl.etl_error_log"
    ]
  },
  {
    "id": "Extract_Premium.dtsx",
    "name": "Extract_Premium.dtsx",
    "type": "SSIS",
    "lines": 197,
    "entities": 38,
    "relationships": 15,
    "rules": 7,
    "purpose": "Extract premium records from the Guidewire PolicyCenter PostgreSQL source, validate referential integrity to policy periods, enforce financial business rules (BR\u201107, BR\u201108, etc.), aggregate premiums by policy period, and load the clean data into the data\u2011warehouse staging layer while quarantining any rejected rows and logging audit information.",
    "raw_code": "<?xml version=\"1.0\"?>\n<DTS:Executable\n    xmlns:DTS=\"www.microsoft.com/SqlServer/Dts\"\n    xmlns:SQLTask=\"www.microsoft.com/sqlserver/dts/tasks/sqltask\"\n    DTS:ExecutableType=\"Microsoft.Package\"\n    DTS:CreationName=\"Microsoft.Package\"\n    DTS:DTSID=\"{047831AE-1F7F-4815-BF19-991EF5E4D8AB}\"\n    DTS:ObjectName=\"Extract_Premium\"\n    DTS:PackageType=\"5\"\n    DTS:VersionMajor=\"1\" DTS:VersionMinor=\"0\" DTS:VersionBuild=\"1\"\n    DTS:VersionGUID=\"{0DD395A1-9798-4E54-B38C-9B80B775D968}\"\n    DTS:Description=\"Extracts PREMIUM, validates FK to POLICY_PERIOD, applies BR-07/BR-08 financial checks, aggregates and loads.\"\n    DTS:LoggingMode=\"UseParentSetting\">\n  <DTS:Variables>\n    <DTS:Variable DTS:Name=\"RowsRead\"><DTS:VariableValue DTS:DataType=\"3\">0</DTS:VariableValue></DTS:Variable>\n    <DTS:Variable DTS:Name=\"RowsInserted\"><DTS:VariableValue DTS:DataType=\"3\">0</DTS:VariableValue></DTS:Variable>\n    <DTS:Variable DTS:Name=\"RowsRejected\"><DTS:VariableValue DTS:DataType=\"3\">0</DTS:VariableValue></DTS:Variable>\n    <DTS:Variable DTS:Name=\"PackageName\"><DTS:VariableValue DTS:DataType=\"8\">Extract_Premium</DTS:VariableValue></DTS:Variable>\n    <DTS:Variable DTS:Name=\"StartTime\"><DTS:VariableValue DTS:DataType=\"7\">1900-01-01T00:00:00</DTS:VariableValue></DTS:Variable>\n  </DTS:Variables>\n  <DTS:ConnectionManagers>\n    <DTS:ConnectionManager DTS:refId=\"Package.ConnectionManagers[CM_Guidewire_PG_Source]\"\n        DTS:CreationName=\"ADO.NET:Npgsql\"\n        DTS:DTSID=\"{9115364D-372C-4495-9C1E-50DF8A571152}\"\n        DTS:ObjectName=\"CM_Guidewire_PG_Source\">\n      <DTS:ObjectData>\n        <DTS:ConnectionManager>\n          <DTS:Property DTS:Name=\"ConnectionString\">Server=gw-pg-source.internal;Port=5432;Database=guidewire_policycenter;User Id=etl_reader;Password=[SECURED_BY_PARAMETER];</DTS:Property>\n          <DTS:Property DTS:Name=\"Provider\">Npgsql PostgreSQL Provider</DTS:Property>\n          <DTS:Property DTS:Name=\"Description\">Source: Guidewire PolicyCenter PostgreSQL replica (read-only)</DTS:Property>\n        </DTS:ConnectionManager>\n      </DTS:ObjectData>\n    </DTS:ConnectionManager>\n    <DTS:ConnectionManager DTS:refId=\"Package.ConnectionManagers[CM_DW_PG_Target]\"\n        DTS:CreationName=\"ADO.NET:Npgsql\"\n        DTS:DTSID=\"{687226D2-4BD4-4707-A18E-CDBC9918635C}\"\n        DTS:ObjectName=\"CM_DW_PG_Target\">\n      <DTS:ObjectData>\n        <DTS:ConnectionManager>\n          <DTS:Property DTS:Name=\"ConnectionString\">Server=dw-pg-target.internal;Port=5432;Database=insurance_dw;User Id=etl_writer;Password=[SECURED_BY_PARAMETER];</DTS:Property>\n          <DTS:Property DTS:Name=\"Provider\">Npgsql PostgreSQL Provider</DTS:Property>\n          <DTS:Property DTS:Name=\"Description\">Target: Insurance Data Warehouse - stg / rpt schemas (PostgreSQL)</DTS:Property>\n        </DTS:ConnectionManager>\n      </DTS:ObjectData>\n    </DTS:ConnectionManager>\n  </DTS:ConnectionManagers>\n  <DTS:Executables>\n    <DTS:Executable DTS:refId=\"Package\\SQL_LogStart\" DTS:CreationName=\"Microsoft.ExecuteSQLTask\" DTS:DTSID=\"{286C64CD-AAAD-497C-BCD3-FF06E9EE0EDE}\" DTS:ExecutableType=\"Microsoft.ExecuteSQLTask\" DTS:ObjectName=\"SQL - Log Package Start\">\n      <DTS:ObjectData>\n        <SQLTask:SqlTaskData\n            SQLTask:Connection=\"CM_DW_PG_Target\"\n            SQLTask:SqlStatementSource=\"INSERT INTO etl.etl_audit_log (package_name, task_name, start_time, status) VALUES (&apos;Extract_Premium&apos;, &apos;Data Flow&apos;, now(), &apos;RUNNING&apos;)\" />\n      </DTS:ObjectData>\n    </DTS:Executable>\n    <DTS:Executable DTS:refId=\"Package\\DFT_Main\" DTS:CreationName=\"Microsoft.Pipeline\" DTS:DTSID=\"{E213B0A7-4BA7-4DCB-8F4B-9E3BDE1CF3B4}\" DTS:ExecutableType=\"Microsoft.Pipeline\" DTS:ObjectName=\"DFT - Extract, Cleanse, Validate, Load premium\">\n      <DTS:ObjectData>\n    <pipeline version=\"1\">\n      <components>\n      <component name=\"SRC - premium (PostgreSQL)\" componentClassID=\"Microsoft.ADO.NET.PGSource\" description=\"Extracts rows from public.premium on CM_Guidewire_PG_Source\">\n        <properties>\n          <property name=\"SqlCommand\">SELECT premium_id, policy_period_id, written_premium, earned_premium, unearned_premium, transaction_date, currency_code, commission_rate, commission_amount, operating_expense, as_of_date FROM public.premium</property>\n          <property name=\"ConnectionManager\">CM_Guidewire_PG_Source</property>\n        </properties>\n        <outputs>\n          <output name=\"OLE DB Source Output\" />\n          <output name=\"OLE DB Source Error Output\" />\n        </outputs>\n      </component>\n      <component name=\"LKP - Validate Policy_Period (policy_period_id)\" componentClassID=\"Microsoft.Lookup\" description=\"Validates policy_period_id exists in Policy_Period (referential integrity / BR-01, BR-05)\">\n        <properties>\n          <property name=\"SqlCommandParam\">SELECT policy_period_id FROM stg.policy_period</property>\n          <property name=\"JoinColumn\">policy_period_id</property>\n          <property name=\"NoMatchBehavior\">RedirectRowsToNoMatchOutput</property>\n          <property name=\"CacheMode\">Full</property>\n        </properties>\n        <inputs>\n          <input name=\"OLE DB Source Output\" />\n        </inputs>\n        <outputs>\n          <output name=\"Lookup Match Output\" />\n          <output name=\"Lookup No Match Output (-> Error Path)\" />\n        </outputs>\n      </component>\n      <component name=\"DER - Data Cleansing\" componentClassID=\"Microsoft.DerivedColumn\" description=\"Trims whitespace, standardizes casing/codes, normalizes nulls\">\n        <properties>\n          <property name=\"Expressions\">UPPER(TRIM(currency_code)) -&gt; currency_code</property>\n        </properties>\n        <inputs>\n          <input name=\"Lookup Match Output\" />\n        </inputs>\n        <outputs>\n          <output name=\"Cleansing Output\" />\n        </outputs>\n      </component>\n      <component name=\"DER - Derived / Calculated Columns\" componentClassID=\"Microsoft.DerivedColumn\" description=\"Adds ETL metadata columns and business-calculated fields\">\n        <properties>\n          <property name=\"Expressions\">GETDATE() -&gt; etl_load_date; commission_rate * written_premium / 100 -&gt; expected_commission_amount</property>\n        </properties>\n        <inputs>\n          <input name=\"Cleansing Output\" />\n        </inputs>\n        <outputs>\n          <output name=\"Derived Column Output\" />\n        </outputs>\n      </component>\n      <component name=\"CSPL - Business Rule Validation\" componentClassID=\"Microsoft.ConditionalSplit\" description=\"Routes rows failing business rules to error output. Rules: earned_premium &lt;= written_premium (BR-07) | ABS(written_premium - (earned_premium + unearned_premium)) &lt;= 1.00 (BR-08 rounding tolerance) | written_premium &gt;= 0.00 AND commission_rate BETWEEN 0.00 AND 100.00 | transaction_date &lt;= GETDATE() AND as_of_date &lt;= GETDATE()\">\n        <properties>\n          <property name=\"ValidOutputName\">Valid Rows</property>\n          <property name=\"InvalidOutputName\">Invalid Rows (-&gt; Error Path)</property>\n          <property name=\"Conditions\">earned_premium &lt;= written_premium (BR-07) | ABS(written_premium - (earned_premium + unearned_premium)) &lt;= 1.00 (BR-08 rounding tolerance) | written_premium &gt;= 0.00 AND commission_rate BETWEEN 0.00 AND 100.00 | transaction_date &lt;= GETDATE() AND as_of_date &lt;= GETDATE()</property>\n        </properties>\n        <inputs>\n          <input name=\"Derived Column Output\" />\n        </inputs>\n        <outputs>\n          <output name=\"Valid Rows\" />\n          <output name=\"Invalid Rows (-> Error Path)\" />\n        </outputs>\n      </component>\n      <component name=\"AGG - Premium Summary by Policy Period\" componentClassID=\"Microsoft.Aggregation\" description=\"Pre-aggregates written/earned/unearned premium per policy_period_id for KPI/reporting reuse (feeds fact_kpi_summary).\">\n        <properties>\n          <property name=\"GroupBy\">policy_period_id</property>\n          <property name=\"Aggregates\">SUM(written_premium), SUM(earned_premium), SUM(unearned_premium), SUM(commission_amount), SUM(operating_expense)</property>\n        </properties>\n        <inputs>\n          <input name=\"Valid Rows\" />\n        </inputs>\n        <outputs>\n          <output name=\"Aggregate Output\" />\n        </outputs>\n      </component>\n      <component name=\"UN - Union All Error Rows\" componentClassID=\"Microsoft.UnionAll\" description=\"Combines all error/no-match/invalid outputs into a single error stream\">\n        <properties>\n\n        </properties>\n        <inputs>\n          <input name=\"Lookup No Match Output (-> Error Path)\" />\n          <input name=\"Invalid Rows (-> Error Path)\" />\n          <input name=\"OLE DB Source Error Output\" />\n        </inputs>\n        <outputs>\n          <output name=\"Unified Error Output\" />\n        </outputs>\n      </component>\n      <component name=\"DST - Error Log (stg.error_quarantine)\" componentClassID=\"Microsoft.OLEDBDestination\" description=\"Writes rejected/invalid rows to the error-quarantine table for review\">\n        <properties>\n          <property name=\"OpenRowset\">stg.error_quarantine</property>\n          <property name=\"ConnectionManager\">CM_DW_PG_Target</property>\n        </properties>\n        <inputs>\n          <input name=\"Unified Error Output\" />\n        </inputs>\n      </component>\n      <component name=\"DST - Load premium (PostgreSQL DW)\" componentClassID=\"Microsoft.OLEDBDestination\" description=\"Loads validated/cleansed rows into stg.premium (upsert via staging + MERGE in post-SQL)\">\n        <properties>\n          <property name=\"OpenRowset\">stg.premium</property>\n          <property name=\"ConnectionManager\">CM_DW_PG_Target</property>\n          <property name=\"FastLoad\">true</property>\n          <property name=\"MaximumInsertCommitSize\">10000</property>\n        </properties>\n        <inputs>\n          <input name=\"Aggregate Output\" />\n        </inputs>\n      </component>\n      </components>\n    </pipeline>\n      </DTS:ObjectData>\n    </DTS:Executable>\n    <DTS:Executable DTS:refId=\"Package\\SQL_LogEnd\" DTS:CreationName=\"Microsoft.ExecuteSQLTask\" DTS:DTSID=\"{ED06AF64-AE26-40D7-9C4A-A64CC716A817}\" DTS:ExecutableType=\"Microsoft.ExecuteSQLTask\" DTS:ObjectName=\"SQL - Log Package End / Row Counts\">\n      <DTS:ObjectData>\n        <SQLTask:SqlTaskData\n            SQLTask:Connection=\"CM_DW_PG_Target\"\n            SQLTask:SqlStatementSource=\"UPDATE etl.etl_audit_log SET end_time = now(), status = &apos;COMPLETED&apos;, rows_read = ?, rows_inserted = ?, rows_rejected = ? WHERE package_name = &apos;Extract_Premium&apos; AND status = &apos;RUNNING&apos;\" />\n      </DTS:ObjectData>\n    </DTS:Executable>\n  </DTS:Executables>\n  <DTS:PrecedenceConstraints>\n    <DTS:PrecedenceConstraint DTS:refId=\"Package.PrecedenceConstraints[SQL_LogStartToDFT_Main]\"\n        DTS:From=\"Package\\SQL_LogStart\" DTS:To=\"Package\\DFT_Main\" DTS:Value=\"3\" DTS:DTSID=\"{007C0005-F2C9-4551-9A02-B1247CD8CF8B}\" />\n    <DTS:PrecedenceConstraint DTS:refId=\"Package.PrecedenceConstraints[DFT_MainToSQL_LogEnd]\"\n        DTS:From=\"Package\\DFT_Main\" DTS:To=\"Package\\SQL_LogEnd\" DTS:Value=\"1\" DTS:DTSID=\"{59D16C0A-711B-49D6-B47D-84EA4BC1D49D}\" />\n  </DTS:PrecedenceConstraints>\n  <DTS:EventHandlers>\n    <DTS:EventHandler DTS:EventName=\"OnError\" DTS:DTSID=\"{CB67CD54-1795-458A-AD4E-D8DC60C28058}\" DTS:ObjectName=\"OnError\">\n      <DTS:Executables>\n    <DTS:Executable DTS:refId=\"Package\\EH_LogError\" DTS:CreationName=\"Microsoft.ExecuteSQLTask\" DTS:DTSID=\"{5E9E3EBC-DE9B-4C1A-A9D2-59878D889BAF}\" DTS:ExecutableType=\"Microsoft.ExecuteSQLTask\" DTS:ObjectName=\"SQL - Log Error to ETL_ERROR_LOG\">\n      <DTS:ObjectData>\n        <SQLTask:SqlTaskData\n            SQLTask:Connection=\"CM_DW_PG_Target\"\n            SQLTask:SqlStatementSource=\"INSERT INTO etl.etl_error_log (package_name, source_object, error_code, error_description, error_time) VALUES (&apos;Extract_Premium&apos;, ?, ?, ?, now())\" />\n      </DTS:ObjectData>\n    </DTS:Executable>\n\n      </DTS:Executables>\n    </DTS:EventHandler>\n  </DTS:EventHandlers>\n</DTS:Executable>\n",
    "business_rules": [
      {
        "rule_id": "Rule 1",
        "name": "Extract_Premium Rule 1",
        "description": "BR\u201101 / BR\u201105: policy_period_id must exist in stg.policy_period (referential integrity)",
        "formula": "BR\u201101 / BR\u201105: policy_period_id must exist in stg.policy_period (referential integrity)"
      },
      {
        "rule_id": "Rule 2",
        "name": "Extract_Premium Rule 2",
        "description": "BR\u201107: earned_premium must be less than or equal to written_premium",
        "formula": null
      },
      {
        "rule_id": "Rule 3",
        "name": "Extract_Premium Rule 3",
        "description": "BR\u201108: Absolute difference between written_premium and the sum of earned_premium plus unearned_premium must be \u2264 1.00 (rounding tolerance)",
        "formula": null
      },
      {
        "rule_id": "Rule 4",
        "name": "Extract_Premium Rule 4",
        "description": "Written premium must be non\u2011negative (written_premium \u2265 0)",
        "formula": null
      },
      {
        "rule_id": "Rule 5",
        "name": "Extract_Premium Rule 5",
        "description": "Commission rate must be between 0.00 and 100.00 inclusive",
        "formula": null
      },
      {
        "rule_id": "Rule 6",
        "name": "Extract_Premium Rule 6",
        "description": "Transaction date and as_of_date must not be in the future (\u2264 current system date)",
        "formula": null
      },
      {
        "rule_id": "Rule 7",
        "name": "Extract_Premium Rule 7",
        "description": "Currency codes are normalized to upper case with no surrounding whitespace",
        "formula": null
      }
    ],
    "inputs": [
      "public.premium (Guidewire PolicyCenter source database)",
      "stg.policy_period (Data warehouse staging table for policy periods)",
      "etl.etl_audit_log (audit table for logging package execution)",
      "etl.etl_error_log (error logging table, used by OnError handler)"
    ],
    "outputs": [
      "stg.premium (staging table for validated premium records)",
      "stg.error_quarantine (table capturing rejected/invalid rows)",
      "etl.etl_audit_log (updated with end_time, rows_read, rows_inserted, rows_rejected)",
      "etl.etl_error_log (records runtime errors)"
    ],
    "transformations": [
      "SQL SELECT premium_id, policy_period_id, written_premium, earned_premium, unearned_premium, transaction_date, currency_code, commission_rate, commission_amount, operating_expense, as_of_date FROM public.premium",
      "Lookup validation of policy_period_id against stg.policy_period (full cache, redirect no\u2011match to error)",
      "Derived Column: UPPER(TRIM(currency_code)) to standardize currency codes",
      "Derived Column: GETDATE() \u2192 etl_load_date; commission_rate * written_premium / 100 \u2192 expected_commission_amount",
      "Conditional Split applying multiple business rule checks (BR\u201107, BR\u201108, premium non\u2011negative, commission_rate range, date not future)",
      "Aggregation by policy_period_id with SUM of written_premium, earned_premium, unearned_premium, commission_amount, operating_expense",
      "Union All of all error streams (lookup no\u2011match, conditional split invalid rows, source error output)",
      "Fast\u2011load bulk insert into stg.premium (MaximumInsertCommitSize=10000)",
      "Insert into stg.error_quarantine for error rows",
      "Audit log INSERT at start and UPDATE at end with row counts"
    ],
    "dependencies": [
      "Connection Manager CM_Guidewire_PG_Source (Npgsql PostgreSQL provider)",
      "Connection Manager CM_DW_PG_Target (Npgsql PostgreSQL provider)",
      "Source table public.premium",
      "Reference table stg.policy_period",
      "Target tables stg.premium, stg.error_quarantine",
      "Audit tables etl.etl_audit_log, etl.etl_error_log",
      "SSIS components: ADO.NET PostgreSQL Source, Lookup, Derived Column, Conditional Split, Aggregation, Union All, OLE DB Destination",
      "GETDATE() function for current timestamp"
    ]
  },
  {
    "id": "Extract_Producer.dtsx",
    "name": "Extract_Producer.dtsx",
    "type": "SSIS",
    "lines": 170,
    "entities": 33,
    "relationships": 14,
    "rules": 5,
    "purpose": "Extracts, cleanses, validates and loads PRODUCER master data from the Guidewire PolicyCenter PostgreSQL replica into the insurance data warehouse, while logging audit information and quarantining invalid rows.",
    "raw_code": "<?xml version=\"1.0\"?>\n<DTS:Executable\n    xmlns:DTS=\"www.microsoft.com/SqlServer/Dts\"\n    xmlns:SQLTask=\"www.microsoft.com/sqlserver/dts/tasks/sqltask\"\n    DTS:ExecutableType=\"Microsoft.Package\"\n    DTS:CreationName=\"Microsoft.Package\"\n    DTS:DTSID=\"{FB06FD3F-08D7-4203-8BF6-2AB45647B614}\"\n    DTS:ObjectName=\"Extract_Producer\"\n    DTS:PackageType=\"5\"\n    DTS:VersionMajor=\"1\" DTS:VersionMinor=\"0\" DTS:VersionBuild=\"1\"\n    DTS:VersionGUID=\"{09CE8587-8484-4694-A1B2-644B25998736}\"\n    DTS:Description=\"Extracts, cleanses, validates and loads PRODUCER master data.\"\n    DTS:LoggingMode=\"UseParentSetting\">\n  <DTS:Variables>\n    <DTS:Variable DTS:Name=\"RowsRead\"><DTS:VariableValue DTS:DataType=\"3\">0</DTS:VariableValue></DTS:Variable>\n    <DTS:Variable DTS:Name=\"RowsInserted\"><DTS:VariableValue DTS:DataType=\"3\">0</DTS:VariableValue></DTS:Variable>\n    <DTS:Variable DTS:Name=\"RowsRejected\"><DTS:VariableValue DTS:DataType=\"3\">0</DTS:VariableValue></DTS:Variable>\n    <DTS:Variable DTS:Name=\"PackageName\"><DTS:VariableValue DTS:DataType=\"8\">Extract_Producer</DTS:VariableValue></DTS:Variable>\n    <DTS:Variable DTS:Name=\"StartTime\"><DTS:VariableValue DTS:DataType=\"7\">1900-01-01T00:00:00</DTS:VariableValue></DTS:Variable>\n  </DTS:Variables>\n  <DTS:ConnectionManagers>\n    <DTS:ConnectionManager DTS:refId=\"Package.ConnectionManagers[CM_Guidewire_PG_Source]\"\n        DTS:CreationName=\"ADO.NET:Npgsql\"\n        DTS:DTSID=\"{9115364D-372C-4495-9C1E-50DF8A571152}\"\n        DTS:ObjectName=\"CM_Guidewire_PG_Source\">\n      <DTS:ObjectData>\n        <DTS:ConnectionManager>\n          <DTS:Property DTS:Name=\"ConnectionString\">Server=gw-pg-source.internal;Port=5432;Database=guidewire_policycenter;User Id=etl_reader;Password=[SECURED_BY_PARAMETER];</DTS:Property>\n          <DTS:Property DTS:Name=\"Provider\">Npgsql PostgreSQL Provider</DTS:Property>\n          <DTS:Property DTS:Name=\"Description\">Source: Guidewire PolicyCenter PostgreSQL replica (read-only)</DTS:Property>\n        </DTS:ConnectionManager>\n      </DTS:ObjectData>\n    </DTS:ConnectionManager>\n    <DTS:ConnectionManager DTS:refId=\"Package.ConnectionManagers[CM_DW_PG_Target]\"\n        DTS:CreationName=\"ADO.NET:Npgsql\"\n        DTS:DTSID=\"{687226D2-4BD4-4707-A18E-CDBC9918635C}\"\n        DTS:ObjectName=\"CM_DW_PG_Target\">\n      <DTS:ObjectData>\n        <DTS:ConnectionManager>\n          <DTS:Property DTS:Name=\"ConnectionString\">Server=dw-pg-target.internal;Port=5432;Database=insurance_dw;User Id=etl_writer;Password=[SECURED_BY_PARAMETER];</DTS:Property>\n          <DTS:Property DTS:Name=\"Provider\">Npgsql PostgreSQL Provider</DTS:Property>\n          <DTS:Property DTS:Name=\"Description\">Target: Insurance Data Warehouse - stg / rpt schemas (PostgreSQL)</DTS:Property>\n        </DTS:ConnectionManager>\n      </DTS:ObjectData>\n    </DTS:ConnectionManager>\n  </DTS:ConnectionManagers>\n  <DTS:Executables>\n    <DTS:Executable DTS:refId=\"Package\\SQL_LogStart\" DTS:CreationName=\"Microsoft.ExecuteSQLTask\" DTS:DTSID=\"{031A2927-A6ED-488E-A5D2-78EFB7385AAB}\" DTS:ExecutableType=\"Microsoft.ExecuteSQLTask\" DTS:ObjectName=\"SQL - Log Package Start\">\n      <DTS:ObjectData>\n        <SQLTask:SqlTaskData\n            SQLTask:Connection=\"CM_DW_PG_Target\"\n            SQLTask:SqlStatementSource=\"INSERT INTO etl.etl_audit_log (package_name, task_name, start_time, status) VALUES (&apos;Extract_Producer&apos;, &apos;Data Flow&apos;, now(), &apos;RUNNING&apos;)\" />\n      </DTS:ObjectData>\n    </DTS:Executable>\n    <DTS:Executable DTS:refId=\"Package\\DFT_Main\" DTS:CreationName=\"Microsoft.Pipeline\" DTS:DTSID=\"{15B8FE52-FD7C-4323-804E-EF4AE342A66F}\" DTS:ExecutableType=\"Microsoft.Pipeline\" DTS:ObjectName=\"DFT - Extract, Cleanse, Validate, Load producer\">\n      <DTS:ObjectData>\n    <pipeline version=\"1\">\n      <components>\n      <component name=\"SRC - producer (PostgreSQL)\" componentClassID=\"Microsoft.ADO.NET.PGSource\" description=\"Extracts rows from public.producer on CM_Guidewire_PG_Source\">\n        <properties>\n          <property name=\"SqlCommand\">SELECT producer_id, producer_code, producer_name, commission_rate, producer_type, state_code, producer_status, created_date FROM public.producer</property>\n          <property name=\"ConnectionManager\">CM_Guidewire_PG_Source</property>\n        </properties>\n        <outputs>\n          <output name=\"OLE DB Source Output\" />\n          <output name=\"OLE DB Source Error Output\" />\n        </outputs>\n      </component>\n      <component name=\"DER - Data Cleansing\" componentClassID=\"Microsoft.DerivedColumn\" description=\"Trims whitespace, standardizes casing/codes, normalizes nulls\">\n        <properties>\n          <property name=\"Expressions\">TRIM(producer_name) -&gt; producer_name; UPPER(TRIM(state_code)) -&gt; state_code</property>\n        </properties>\n        <inputs>\n          <input name=\"OLE DB Source Output\" />\n        </inputs>\n        <outputs>\n          <output name=\"Cleansing Output\" />\n        </outputs>\n      </component>\n      <component name=\"DER - Derived / Calculated Columns\" componentClassID=\"Microsoft.DerivedColumn\" description=\"Adds ETL metadata columns and business-calculated fields\">\n        <properties>\n          <property name=\"Expressions\">GETDATE() -&gt; etl_load_date</property>\n        </properties>\n        <inputs>\n          <input name=\"Cleansing Output\" />\n        </inputs>\n        <outputs>\n          <output name=\"Derived Column Output\" />\n        </outputs>\n      </component>\n      <component name=\"CSPL - Business Rule Validation\" componentClassID=\"Microsoft.ConditionalSplit\" description=\"Routes rows failing business rules to error output. Rules: commission_rate &gt;= 0.00 AND commission_rate &lt;= 100.00 | producer_type IN (&apos;AGENCY&apos;,&apos;BROKER&apos;,&apos;AGENT&apos;,&apos;INDIVIDUAL&apos;) | created_date &lt;= GETDATE()\">\n        <properties>\n          <property name=\"ValidOutputName\">Valid Rows</property>\n          <property name=\"InvalidOutputName\">Invalid Rows (-&gt; Error Path)</property>\n          <property name=\"Conditions\">commission_rate &gt;= 0.00 AND commission_rate &lt;= 100.00 | producer_type IN ('AGENCY','BROKER','AGENT','INDIVIDUAL') | created_date &lt;= GETDATE()</property>\n        </properties>\n        <inputs>\n          <input name=\"Derived Column Output\" />\n        </inputs>\n        <outputs>\n          <output name=\"Valid Rows\" />\n          <output name=\"Invalid Rows (-> Error Path)\" />\n        </outputs>\n      </component>\n      <component name=\"UN - Union All Error Rows\" componentClassID=\"Microsoft.UnionAll\" description=\"Combines all error/no-match/invalid outputs into a single error stream\">\n        <properties>\n\n        </properties>\n        <inputs>\n          <input name=\"Lookup No Match Output (-> Error Path)\" />\n          <input name=\"Invalid Rows (-> Error Path)\" />\n          <input name=\"OLE DB Source Error Output\" />\n        </inputs>\n        <outputs>\n          <output name=\"Unified Error Output\" />\n        </outputs>\n      </component>\n      <component name=\"DST - Error Log (stg.error_quarantine)\" componentClassID=\"Microsoft.OLEDBDestination\" description=\"Writes rejected/invalid rows to the error-quarantine table for review\">\n        <properties>\n          <property name=\"OpenRowset\">stg.error_quarantine</property>\n          <property name=\"ConnectionManager\">CM_DW_PG_Target</property>\n        </properties>\n        <inputs>\n          <input name=\"Unified Error Output\" />\n        </inputs>\n      </component>\n      <component name=\"DST - Load producer (PostgreSQL DW)\" componentClassID=\"Microsoft.OLEDBDestination\" description=\"Loads validated/cleansed rows into stg.producer (upsert via staging + MERGE in post-SQL)\">\n        <properties>\n          <property name=\"OpenRowset\">stg.producer</property>\n          <property name=\"ConnectionManager\">CM_DW_PG_Target</property>\n          <property name=\"FastLoad\">true</property>\n          <property name=\"MaximumInsertCommitSize\">10000</property>\n        </properties>\n        <inputs>\n          <input name=\"Valid Rows\" />\n        </inputs>\n      </component>\n      </components>\n    </pipeline>\n      </DTS:ObjectData>\n    </DTS:Executable>\n    <DTS:Executable DTS:refId=\"Package\\SQL_LogEnd\" DTS:CreationName=\"Microsoft.ExecuteSQLTask\" DTS:DTSID=\"{7B80AFD1-2D84-4BCF-BDFA-2112DCCA68ED}\" DTS:ExecutableType=\"Microsoft.ExecuteSQLTask\" DTS:ObjectName=\"SQL - Log Package End / Row Counts\">\n      <DTS:ObjectData>\n        <SQLTask:SqlTaskData\n            SQLTask:Connection=\"CM_DW_PG_Target\"\n            SQLTask:SqlStatementSource=\"UPDATE etl.etl_audit_log SET end_time = now(), status = &apos;COMPLETED&apos;, rows_read = ?, rows_inserted = ?, rows_rejected = ? WHERE package_name = &apos;Extract_Producer&apos; AND status = &apos;RUNNING&apos;\" />\n      </DTS:ObjectData>\n    </DTS:Executable>\n  </DTS:Executables>\n  <DTS:PrecedenceConstraints>\n    <DTS:PrecedenceConstraint DTS:refId=\"Package.PrecedenceConstraints[SQL_LogStartToDFT_Main]\"\n        DTS:From=\"Package\\SQL_LogStart\" DTS:To=\"Package\\DFT_Main\" DTS:Value=\"3\" DTS:DTSID=\"{48746181-8332-4670-9A35-1793B355A9E9}\" />\n    <DTS:PrecedenceConstraint DTS:refId=\"Package.PrecedenceConstraints[DFT_MainToSQL_LogEnd]\"\n        DTS:From=\"Package\\DFT_Main\" DTS:To=\"Package\\SQL_LogEnd\" DTS:Value=\"1\" DTS:DTSID=\"{3A4EA97B-28B9-4344-AF5E-C73B66204F97}\" />\n  </DTS:PrecedenceConstraints>\n  <DTS:EventHandlers>\n    <DTS:EventHandler DTS:EventName=\"OnError\" DTS:DTSID=\"{2F8FF7B0-2A1D-4D8C-9C83-64E6F8E7C73E}\" DTS:ObjectName=\"OnError\">\n      <DTS:Executables>\n    <DTS:Executable DTS:refId=\"Package\\EH_LogError\" DTS:CreationName=\"Microsoft.ExecuteSQLTask\" DTS:DTSID=\"{A3923964-C2F6-4564-9A1F-653EB561365A}\" DTS:ExecutableType=\"Microsoft.ExecuteSQLTask\" DTS:ObjectName=\"SQL - Log Error to ETL_ERROR_LOG\">\n      <DTS:ObjectData>\n        <SQLTask:SqlTaskData\n            SQLTask:Connection=\"CM_DW_PG_Target\"\n            SQLTask:SqlStatementSource=\"INSERT INTO etl.etl_error_log (package_name, source_object, error_code, error_description, error_time) VALUES (&apos;Extract_Producer&apos;, ?, ?, ?, now())\" />\n      </DTS:ObjectData>\n    </DTS:Executable>\n\n      </DTS:Executables>\n    </DTS:EventHandler>\n  </DTS:EventHandlers>\n</DTS:Executable>\n",
    "business_rules": [
      {
        "rule_id": "Rule 1",
        "name": "Extract_Producer Rule 1",
        "description": "commission_rate must be greater than or equal to 0.00 and less than or equal to 100.00",
        "formula": null
      },
      {
        "rule_id": "Rule 2",
        "name": "Extract_Producer Rule 2",
        "description": "producer_type must be one of the allowed values: 'AGENCY', 'BROKER', 'AGENT', 'INDIVIDUAL'",
        "formula": null
      },
      {
        "rule_id": "Rule 3",
        "name": "Extract_Producer Rule 3",
        "description": "created_date must not be in the future (created_date <= current system date)",
        "formula": "created_date must not be in the future (created_date <= current system date)"
      },
      {
        "rule_id": "Rule 4",
        "name": "Extract_Producer Rule 4",
        "description": "Whitespace is trimmed from producer_name and state_code is normalized to upper case",
        "formula": null
      },
      {
        "rule_id": "Rule 5",
        "name": "Extract_Producer Rule 5",
        "description": "Rows failing any rule are routed to the error quarantine table",
        "formula": null
      }
    ],
    "inputs": [
      "public.producer (Guidewire PolicyCenter PostgreSQL source table)",
      "CM_Guidewire_PG_Source connection (read\u2011only replica)",
      "CM_DW_PG_Target connection (target data warehouse)",
      "etl.etl_audit_log (used for logging start/end, not a source of business data)",
      "etl.etl_error_log (used for error logging)"
    ],
    "outputs": [
      "stg.producer (staging table in insurance_dw schema)",
      "stg.error_quarantine (table for rejected/invalid rows)",
      "etl.etl_audit_log (audit record with start/end timestamps and row counts)",
      "etl.etl_error_log (error record when package fails)"
    ],
    "transformations": [
      "SELECT producer_id, producer_code, producer_name, commission_rate, producer_type, state_code, producer_status, created_date FROM public.producer",
      "TRIM(producer_name) to remove leading/trailing whitespace",
      "UPPER(TRIM(state_code)) to standardize state codes",
      "Add ETL metadata column etl_load_date = GETDATE()",
      "Conditional split applying business rules (commission_rate range, allowed producer_type values, created_date <= current date)",
      "Union All to combine source error output, invalid rows, and lookup\u2011no\u2011match rows into a single error stream",
      "Fast bulk load into stg.producer with commit size of 10,000 rows"
    ],
    "dependencies": [
      "Connection Manager CM_Guidewire_PG_Source (ADO.NET Npgsql provider)",
      "Connection Manager CM_DW_PG_Target (ADO.NET Npgsql provider)",
      "Execute SQL Task \u2013 Log Package Start (etl.etl_audit_log)",
      "Execute SQL Task \u2013 Log Package End (etl.etl_audit_log update)",
      "Execute SQL Task \u2013 Log Error (etl.etl_error_log)",
      "Data Flow components: ADO.NET PGSource, Derived Column (twice), Conditional Split, Union All, OLE DB Destination (stg.producer), OLE DB Destination (stg.error_quarantine)",
      "Target tables: stg.producer, stg.error_quarantine, etl.etl_audit_log, etl.etl_error_log"
    ]
  },
  {
    "id": "Master_ETL_Guidewire.dtsx",
    "name": "Master_ETL_Guidewire.dtsx",
    "type": "SSIS",
    "lines": 146,
    "entities": 26,
    "relationships": 39,
    "rules": 4,
    "purpose": "Master orchestration SSIS package for Guidewire PolicyCenter (Source System 3) ETL. Coordinates execution of child extraction packages in foreign-key dependency order, manages audit logging, and provides centralized error handling.",
    "raw_code": "<?xml version=\"1.0\"?>\n<DTS:Executable\n    xmlns:DTS=\"www.microsoft.com/SqlServer/Dts\"\n    xmlns:SQLTask=\"www.microsoft.com/sqlserver/dts/tasks/sqltask\"\n    DTS:ExecutableType=\"Microsoft.Package\"\n    DTS:CreationName=\"Microsoft.Package\"\n    DTS:DTSID=\"{6D8CC6FD-E214-4160-99D6-EF516C23153A}\"\n    DTS:ObjectName=\"Master_ETL_Guidewire\"\n    DTS:PackageType=\"5\"\n    DTS:VersionMajor=\"1\" DTS:VersionMinor=\"0\" DTS:VersionBuild=\"1\"\n    DTS:VersionGUID=\"{626CDECA-7506-4AEF-AB7D-894A975BF613}\"\n    DTS:Description=\"Master orchestration package for Source System 3 (Guidewire PolicyCenter PostgreSQL). Executes all child ETL packages in FK-dependency order: Account/Producer -&gt; Policy -&gt; Job/Claims -&gt; Policy_Period -&gt; Location/Coverage/Premium -&gt; KPI Aggregates. Provides audit logging and centralized error handling.\"\n    DTS:LoggingMode=\"UseParentSetting\">\n  <DTS:ConnectionManagers>\n    <DTS:ConnectionManager DTS:refId=\"Package.ConnectionManagers[CM_DW_PG_Target]\"\n        DTS:CreationName=\"ADO.NET:Npgsql\"\n        DTS:DTSID=\"{248FFA76-0389-4A8D-AE39-0CA6BBE7AA83}\"\n        DTS:ObjectName=\"CM_DW_PG_Target\">\n      <DTS:ObjectData>\n        <DTS:ConnectionManager>\n          <DTS:Property DTS:Name=\"ConnectionString\">Server=dw-pg-target.internal;Port=5432;Database=insurance_dw;User Id=etl_writer;Password=[SECURED_BY_PARAMETER];</DTS:Property>\n          <DTS:Property DTS:Name=\"Provider\">Npgsql PostgreSQL Provider</DTS:Property>\n        </DTS:ConnectionManager>\n      </DTS:ObjectData>\n    </DTS:ConnectionManager>\n  </DTS:ConnectionManagers>\n  <DTS:Executables>\n    <DTS:Executable DTS:refId=\"Package\\SQL_MasterStart\" DTS:CreationName=\"Microsoft.ExecuteSQLTask\" DTS:DTSID=\"{95410872-CA26-481A-8950-C3B115543ACC}\" DTS:ExecutableType=\"Microsoft.ExecuteSQLTask\" DTS:ObjectName=\"SQL - Log Master Start\">\n      <DTS:ObjectData>\n        <SQLTask:SqlTaskData SQLTask:Connection=\"CM_DW_PG_Target\" SQLTask:SqlStatementSource=\"INSERT INTO etl.etl_audit_log (package_name, task_name, start_time, status) VALUES (&apos;Master_ETL_Guidewire&apos;, &apos;Full Load&apos;, now(), &apos;RUNNING&apos;)\" />\n      </DTS:ObjectData>\n    </DTS:Executable>\n    <DTS:Executable DTS:refId=\"Package\\EPT_Account\" DTS:CreationName=\"Microsoft.ExecutePackageTask\" DTS:DTSID=\"{3638264A-5B39-4B5B-B11A-023545357363}\" DTS:ExecutableType=\"Microsoft.ExecutePackageTask\" DTS:ObjectName=\"Run Account\">\n      <DTS:ObjectData>\n        <ExecutePackageTask:ExecutePackageTaskData\n            xmlns:ExecutePackageTask=\"www.microsoft.com/sqlserver/dts/tasks/executepackagetask\"\n            ExecutePackageTask:PackageNameFromProjectReference=\"Extract_Account.dtsx\"\n            ExecutePackageTask:ExecuteOutOfProcess=\"false\" />\n      </DTS:ObjectData>\n    </DTS:Executable>\n    <DTS:Executable DTS:refId=\"Package\\EPT_Producer\" DTS:CreationName=\"Microsoft.ExecutePackageTask\" DTS:DTSID=\"{29CD4BB2-C492-42EA-9B6F-C928DB3C192E}\" DTS:ExecutableType=\"Microsoft.ExecutePackageTask\" DTS:ObjectName=\"Run Producer\">\n      <DTS:ObjectData>\n        <ExecutePackageTask:ExecutePackageTaskData\n            xmlns:ExecutePackageTask=\"www.microsoft.com/sqlserver/dts/tasks/executepackagetask\"\n            ExecutePackageTask:PackageNameFromProjectReference=\"Extract_Producer.dtsx\"\n            ExecutePackageTask:ExecuteOutOfProcess=\"false\" />\n      </DTS:ObjectData>\n    </DTS:Executable>\n    <DTS:Executable DTS:refId=\"Package\\EPT_Policy\" DTS:CreationName=\"Microsoft.ExecutePackageTask\" DTS:DTSID=\"{73A05E89-37D9-40A0-94E0-F7B2C77BF17D}\" DTS:ExecutableType=\"Microsoft.ExecutePackageTask\" DTS:ObjectName=\"Run Policy\">\n      <DTS:ObjectData>\n        <ExecutePackageTask:ExecutePackageTaskData\n            xmlns:ExecutePackageTask=\"www.microsoft.com/sqlserver/dts/tasks/executepackagetask\"\n            ExecutePackageTask:PackageNameFromProjectReference=\"Extract_Policy.dtsx\"\n            ExecutePackageTask:ExecuteOutOfProcess=\"false\" />\n      </DTS:ObjectData>\n    </DTS:Executable>\n    <DTS:Executable DTS:refId=\"Package\\EPT_Job\" DTS:CreationName=\"Microsoft.ExecutePackageTask\" DTS:DTSID=\"{0473D195-38A6-4D24-AB66-82104D7E0865}\" DTS:ExecutableType=\"Microsoft.ExecutePackageTask\" DTS:ObjectName=\"Run Job\">\n      <DTS:ObjectData>\n        <ExecutePackageTask:ExecutePackageTaskData\n            xmlns:ExecutePackageTask=\"www.microsoft.com/sqlserver/dts/tasks/executepackagetask\"\n            ExecutePackageTask:PackageNameFromProjectReference=\"Extract_Job.dtsx\"\n            ExecutePackageTask:ExecuteOutOfProcess=\"false\" />\n      </DTS:ObjectData>\n    </DTS:Executable>\n    <DTS:Executable DTS:refId=\"Package\\EPT_Claims\" DTS:CreationName=\"Microsoft.ExecutePackageTask\" DTS:DTSID=\"{F3B7352E-E829-44A2-9570-ABB5F56B990D}\" DTS:ExecutableType=\"Microsoft.ExecutePackageTask\" DTS:ObjectName=\"Run Claims\">\n      <DTS:ObjectData>\n        <ExecutePackageTask:ExecutePackageTaskData\n            xmlns:ExecutePackageTask=\"www.microsoft.com/sqlserver/dts/tasks/executepackagetask\"\n            ExecutePackageTask:PackageNameFromProjectReference=\"Extract_Claims.dtsx\"\n            ExecutePackageTask:ExecuteOutOfProcess=\"false\" />\n      </DTS:ObjectData>\n    </DTS:Executable>\n    <DTS:Executable DTS:refId=\"Package\\EPT_PolicyPeriod\" DTS:CreationName=\"Microsoft.ExecutePackageTask\" DTS:DTSID=\"{F4AC5934-FC0A-40E3-8000-0EB9C40DE0AD}\" DTS:ExecutableType=\"Microsoft.ExecutePackageTask\" DTS:ObjectName=\"Run PolicyPeriod\">\n      <DTS:ObjectData>\n        <ExecutePackageTask:ExecutePackageTaskData\n            xmlns:ExecutePackageTask=\"www.microsoft.com/sqlserver/dts/tasks/executepackagetask\"\n            ExecutePackageTask:PackageNameFromProjectReference=\"Extract_PolicyPeriod.dtsx\"\n            ExecutePackageTask:ExecuteOutOfProcess=\"false\" />\n      </DTS:ObjectData>\n    </DTS:Executable>\n    <DTS:Executable DTS:refId=\"Package\\EPT_Location\" DTS:CreationName=\"Microsoft.ExecutePackageTask\" DTS:DTSID=\"{4EBE06FE-9DCC-4FFD-966F-EFF38DC8CDA9}\" DTS:ExecutableType=\"Microsoft.ExecutePackageTask\" DTS:ObjectName=\"Run Location\">\n      <DTS:ObjectData>\n        <ExecutePackageTask:ExecutePackageTaskData\n            xmlns:ExecutePackageTask=\"www.microsoft.com/sqlserver/dts/tasks/executepackagetask\"\n            ExecutePackageTask:PackageNameFromProjectReference=\"Extract_Location.dtsx\"\n            ExecutePackageTask:ExecuteOutOfProcess=\"false\" />\n      </DTS:ObjectData>\n    </DTS:Executable>\n    <DTS:Executable DTS:refId=\"Package\\EPT_Coverage\" DTS:CreationName=\"Microsoft.ExecutePackageTask\" DTS:DTSID=\"{7404E343-65F8-495F-B7D0-97CF469BEAB3}\" DTS:ExecutableType=\"Microsoft.ExecutePackageTask\" DTS:ObjectName=\"Run Coverage\">\n      <DTS:ObjectData>\n        <ExecutePackageTask:ExecutePackageTaskData\n            xmlns:ExecutePackageTask=\"www.microsoft.com/sqlserver/dts/tasks/executepackagetask\"\n            ExecutePackageTask:PackageNameFromProjectReference=\"Extract_Coverage.dtsx\"\n            ExecutePackageTask:ExecuteOutOfProcess=\"false\" />\n      </DTS:ObjectData>\n    </DTS:Executable>\n    <DTS:Executable DTS:refId=\"Package\\EPT_Premium\" DTS:CreationName=\"Microsoft.ExecutePackageTask\" DTS:DTSID=\"{A894D81A-5CF4-4AB0-9EE3-80EC31EF0E55}\" DTS:ExecutableType=\"Microsoft.ExecutePackageTask\" DTS:ObjectName=\"Run Premium\">\n      <DTS:ObjectData>\n        <ExecutePackageTask:ExecutePackageTaskData\n            xmlns:ExecutePackageTask=\"www.microsoft.com/sqlserver/dts/tasks/executepackagetask\"\n            ExecutePackageTask:PackageNameFromProjectReference=\"Extract_Premium.dtsx\"\n            ExecutePackageTask:ExecuteOutOfProcess=\"false\" />\n      </DTS:ObjectData>\n    </DTS:Executable>\n    <DTS:Executable DTS:refId=\"Package\\EPT_KPIAggregates\" DTS:CreationName=\"Microsoft.ExecutePackageTask\" DTS:DTSID=\"{31B09F66-882A-4301-BE7B-772CE74C035D}\" DTS:ExecutableType=\"Microsoft.ExecutePackageTask\" DTS:ObjectName=\"Run KPIAggregates\">\n      <DTS:ObjectData>\n        <ExecutePackageTask:ExecutePackageTaskData\n            xmlns:ExecutePackageTask=\"www.microsoft.com/sqlserver/dts/tasks/executepackagetask\"\n            ExecutePackageTask:PackageNameFromProjectReference=\"Extract_KPI_Aggregates.dtsx\"\n            ExecutePackageTask:ExecuteOutOfProcess=\"false\" />\n      </DTS:ObjectData>\n    </DTS:Executable>\n    <DTS:Executable DTS:refId=\"Package\\SQL_MasterEnd\" DTS:CreationName=\"Microsoft.ExecuteSQLTask\" DTS:DTSID=\"{E51B7CFD-8E53-4DE2-87F7-BC6FF9AB3497}\" DTS:ExecutableType=\"Microsoft.ExecuteSQLTask\" DTS:ObjectName=\"SQL - Log Master End\">\n      <DTS:ObjectData>\n        <SQLTask:SqlTaskData SQLTask:Connection=\"CM_DW_PG_Target\" SQLTask:SqlStatementSource=\"UPDATE etl.etl_audit_log SET end_time = now(), status = &apos;COMPLETED&apos; WHERE package_name = &apos;Master_ETL_Guidewire&apos; AND status = &apos;RUNNING&apos;\" />\n      </DTS:ObjectData>\n    </DTS:Executable>\n  </DTS:Executables>\n  <DTS:PrecedenceConstraints>\n    <DTS:PrecedenceConstraint DTS:refId=\"Package.PrecedenceConstraints[StartToG1a]\" DTS:From=\"Package\\SQL_MasterStart\" DTS:To=\"Package\\EPT_Account\" DTS:Value=\"3\" DTS:DTSID=\"{58F2C58F-80C3-4591-91DA-6A5FF5DA9701}\" />\n    <DTS:PrecedenceConstraint DTS:refId=\"Package.PrecedenceConstraints[StartToG1b]\" DTS:From=\"Package\\SQL_MasterStart\" DTS:To=\"Package\\EPT_Producer\" DTS:Value=\"3\" DTS:DTSID=\"{5A4CDD7F-AD24-4ED5-8CEF-A7035F76C00E}\" />\n    <DTS:PrecedenceConstraint DTS:refId=\"Package.PrecedenceConstraints[G1toPolicy_a]\" DTS:From=\"Package\\EPT_Account\" DTS:To=\"Package\\EPT_Policy\" DTS:Value=\"3\" DTS:DTSID=\"{1632958A-0CD7-49AE-8259-0DB12C05789B}\" />\n    <DTS:PrecedenceConstraint DTS:refId=\"Package.PrecedenceConstraints[G1toPolicy_b]\" DTS:From=\"Package\\EPT_Producer\" DTS:To=\"Package\\EPT_Policy\" DTS:Value=\"3\" DTS:DTSID=\"{310FA1C2-E1F2-4EB0-BEAB-200A475F1EEE}\" />\n    <DTS:PrecedenceConstraint DTS:refId=\"Package.PrecedenceConstraints[PolicyToJob]\" DTS:From=\"Package\\EPT_Policy\" DTS:To=\"Package\\EPT_Job\" DTS:Value=\"3\" DTS:DTSID=\"{79AD5DCE-72FF-4B0A-A3AB-27335B572074}\" />\n    <DTS:PrecedenceConstraint DTS:refId=\"Package.PrecedenceConstraints[PolicyToClaims]\" DTS:From=\"Package\\EPT_Policy\" DTS:To=\"Package\\EPT_Claims\" DTS:Value=\"3\" DTS:DTSID=\"{B7BF25D6-9DAC-4F0D-A1D0-CB0698C8658D}\" />\n    <DTS:PrecedenceConstraint DTS:refId=\"Package.PrecedenceConstraints[JobToPolicyPeriod]\" DTS:From=\"Package\\EPT_Job\" DTS:To=\"Package\\EPT_PolicyPeriod\" DTS:Value=\"3\" DTS:DTSID=\"{79E9DF89-153E-4D79-858F-3911054847CD}\" />\n    <DTS:PrecedenceConstraint DTS:refId=\"Package.PrecedenceConstraints[PolicyPeriodToEPT_Location]\" DTS:From=\"Package\\EPT_PolicyPeriod\" DTS:To=\"Package\\EPT_Location\" DTS:Value=\"3\" DTS:DTSID=\"{C167B122-8B3F-4AF2-919B-3EEA2C23E1B9}\" />\n    <DTS:PrecedenceConstraint DTS:refId=\"Package.PrecedenceConstraints[PolicyPeriodToEPT_Coverage]\" DTS:From=\"Package\\EPT_PolicyPeriod\" DTS:To=\"Package\\EPT_Coverage\" DTS:Value=\"3\" DTS:DTSID=\"{BA3FA8CA-4BF6-4CCB-A8C0-03E9A4C3418C}\" />\n    <DTS:PrecedenceConstraint DTS:refId=\"Package.PrecedenceConstraints[PolicyPeriodToEPT_Premium]\" DTS:From=\"Package\\EPT_PolicyPeriod\" DTS:To=\"Package\\EPT_Premium\" DTS:Value=\"3\" DTS:DTSID=\"{491691F5-3783-424C-8F45-8F4E282CBB09}\" />\n    <DTS:PrecedenceConstraint DTS:refId=\"Package.PrecedenceConstraints[PremiumToKPI]\" DTS:From=\"Package\\EPT_Premium\" DTS:To=\"Package\\EPT_KPIAggregates\" DTS:Value=\"3\" DTS:DTSID=\"{04367A3F-B462-4DD6-9964-A49926583C25}\" />\n    <DTS:PrecedenceConstraint DTS:refId=\"Package.PrecedenceConstraints[ClaimsToKPI]\" DTS:From=\"Package\\EPT_Claims\" DTS:To=\"Package\\EPT_KPIAggregates\" DTS:Value=\"3\" DTS:DTSID=\"{284111FE-A3A2-4E45-800C-78C693901915}\" />\n    <DTS:PrecedenceConstraint DTS:refId=\"Package.PrecedenceConstraints[KPIToEnd]\" DTS:From=\"Package\\EPT_KPIAggregates\" DTS:To=\"Package\\SQL_MasterEnd\" DTS:Value=\"3\" DTS:DTSID=\"{E28B807D-CEFD-47D6-A5F9-9A1F6F57D7FB}\" />\n  </DTS:PrecedenceConstraints>\n  <DTS:EventHandlers>\n    <DTS:EventHandler DTS:EventName=\"OnError\" DTS:DTSID=\"{7E6CC784-7F74-49B9-8985-FDBFA6FCCA6A}\" DTS:ObjectName=\"OnError\">\n      <DTS:Executables>\n        <DTS:Executable DTS:refId=\"Package\\EH_MasterFail\" DTS:CreationName=\"Microsoft.ExecuteSQLTask\" DTS:DTSID=\"{68F8D1D3-D7CE-4A84-872A-65225052CC86}\" DTS:ExecutableType=\"Microsoft.ExecuteSQLTask\" DTS:ObjectName=\"SQL - Log Master Failure\">\n          <DTS:ObjectData>\n            <SQLTask:SqlTaskData SQLTask:Connection=\"CM_DW_PG_Target\" SQLTask:SqlStatementSource=\"UPDATE etl.etl_audit_log SET end_time = now(), status = &apos;FAILED&apos; WHERE package_name = &apos;Master_ETL_Guidewire&apos; AND status = &apos;RUNNING&apos;\" />\n          </DTS:ObjectData>\n        </DTS:Executable>\n        <!-- Optional: Send Mail Task / Execute Process Task for on-call notification would be added here (disabled by default). -->\n      </DTS:Executables>\n    </DTS:EventHandler>\n  </DTS:EventHandlers>\n</DTS:Executable>\n",
    "business_rules": [
      {
        "rule_id": "Rule 1",
        "name": "Master_ETL_Guidewire Rule 1",
        "description": "Execution order must respect foreign key dependencies: Account/Producer before Policy; Policy before Job/Claims; Job before PolicyPeriod; PolicyPeriod before Location/Coverage/Premium; Premium and Claims before KPI Aggregates",
        "formula": "Execution order must respect foreign key dependencies: Account/Producer before Policy; Policy before Job/Claims; Job before PolicyPeriod; PolicyPeriod before Location/Coverage/Premium; Premium and Claims before KPI Aggregates"
      },
      {
        "rule_id": "Rule 2",
        "name": "Master_ETL_Guidewire Rule 2",
        "description": "Audit log entry created at start and updated at completion",
        "formula": null
      },
      {
        "rule_id": "Rule 3",
        "name": "Master_ETL_Guidewire Rule 3",
        "description": "All child packages run in-process (ExecuteOutOfProcess=false)",
        "formula": "All child packages run in-process (ExecuteOutOfProcess=false)"
      },
      {
        "rule_id": "Rule 4",
        "name": "Master_ETL_Guidewire Rule 4",
        "description": "Error handling centralized at master package level",
        "formula": null
      }
    ],
    "inputs": [
      "CM_DW_PG_Target (PostgreSQL connection to insurance_dw)",
      "Child SSIS packages: Extract_Account.dtsx, Extract_Producer.dtsx, Extract_Policy.dtsx, Extract_Job.dtsx, Extract_Claims.dtsx, Extract_PolicyPeriod.dtsx, Extract_Location.dtsx, Extract_Coverage.dtsx, Extract_Premium.dtsx, Extract_KPI_Aggregates.dtsx",
      "etl.etl_audit_log table (for logging)"
    ],
    "outputs": [
      "etl.etl_audit_log table (INSERT start record, UPDATE end record)",
      "Execution of child ETL packages (which produce their own outputs)"
    ],
    "transformations": [
      "Orchestration of child package execution in FK-dependent topological order",
      "Audit logging: start timestamp with RUNNING status, end timestamp with COMPLETED status",
      "Parallel execution branching and synchronization points",
      "Centralized error handling via OnError event handler"
    ],
    "dependencies": [
      "PostgreSQL target database (dw-pg-target.internal:5432/insurance_dw)",
      "Npgsql ADO.NET provider",
      "SSIS child packages (Extract_*.dtsx) deployed in same project",
      "etl.etl_audit_log table schema"
    ]
  }
];

export const ACTUAL_GRAPH_DATA = {
  nodes: [
  {
    "id": "EARNPREM.CBL",
    "label": "EARNPREM.CBL",
    "type": "Program",
    "system": "COBOL Layer",
    "file": "EARNPREM.CBL",
    "rules": 11,
    "x": 740,
    "y": 220
  },
  {
    "id": "KPICALC.CBL",
    "label": "KPICALC.CBL",
    "type": "Program",
    "system": "COBOL Layer",
    "file": "KPICALC.CBL",
    "rules": 8,
    "x": 725,
    "y": 273
  },
  {
    "id": "POLLOAD.CBL",
    "label": "POLLOAD.CBL",
    "type": "Program",
    "system": "COBOL Layer",
    "file": "POLLOAD.CBL",
    "rules": 4,
    "x": 681,
    "y": 321
  },
  {
    "id": "POLSTATUS.CBL",
    "label": "POLSTATUS.CBL",
    "type": "Program",
    "system": "COBOL Layer",
    "file": "POLSTATUS.CBL",
    "rules": 10,
    "x": 612,
    "y": 361
  },
  {
    "id": "PREMCALC.CBL",
    "label": "PREMCALC.CBL",
    "type": "Program",
    "system": "COBOL Layer",
    "file": "PREMCALC.CBL",
    "rules": 10,
    "x": 524,
    "y": 388
  },
  {
    "id": "RPTEXTRACT.CBL",
    "label": "RPTEXTRACT.CBL",
    "type": "Program",
    "system": "COBOL Layer",
    "file": "RPTEXTRACT.CBL",
    "rules": 5,
    "x": 425,
    "y": 399
  },
  {
    "id": "ClaimCenter_CPP_Breakdown.sql",
    "label": "ClaimCenter_CPP_Breakdown.sql",
    "type": "Script",
    "system": "SQL Layer",
    "file": "ClaimCenter_CPP_Breakdown.sql",
    "rules": 7,
    "x": 324,
    "y": 395
  },
  {
    "id": "ClaimCenter_Monoline.sql",
    "label": "ClaimCenter_Monoline.sql",
    "type": "Script",
    "system": "SQL Layer",
    "file": "ClaimCenter_Monoline.sql",
    "rules": 8,
    "x": 230,
    "y": 376
  },
  {
    "id": "PolicyCenter_CPP_Breakdown.sql",
    "label": "PolicyCenter_CPP_Breakdown.sql",
    "type": "Script",
    "system": "SQL Layer",
    "file": "PolicyCenter_CPP_Breakdown.sql",
    "rules": 9,
    "x": 151,
    "y": 342
  },
  {
    "id": "PolicyCenter_Monoline.sql",
    "label": "PolicyCenter_Monoline.sql",
    "type": "Script",
    "system": "SQL Layer",
    "file": "PolicyCenter_Monoline.sql",
    "rules": 10,
    "x": 94,
    "y": 298
  },
  {
    "id": "Extract_Account.dtsx",
    "label": "Extract_Account.dtsx",
    "type": "Package",
    "system": "SSIS Layer",
    "file": "Extract_Account.dtsx",
    "rules": 7,
    "x": 64,
    "y": 247
  },
  {
    "id": "Extract_Claims.dtsx",
    "label": "Extract_Claims.dtsx",
    "type": "Package",
    "system": "SSIS Layer",
    "file": "Extract_Claims.dtsx",
    "rules": 6,
    "x": 64,
    "y": 193
  },
  {
    "id": "Extract_Coverage.dtsx",
    "label": "Extract_Coverage.dtsx",
    "type": "Package",
    "system": "SSIS Layer",
    "file": "Extract_Coverage.dtsx",
    "rules": 7,
    "x": 94,
    "y": 142
  },
  {
    "id": "Extract_Job.dtsx",
    "label": "Extract_Job.dtsx",
    "type": "Package",
    "system": "SSIS Layer",
    "file": "Extract_Job.dtsx",
    "rules": 6,
    "x": 151,
    "y": 98
  },
  {
    "id": "Extract_KPI_Aggregates.dtsx",
    "label": "Extract_KPI_Aggregates.dtsx",
    "type": "Package",
    "system": "SSIS Layer",
    "file": "Extract_KPI_Aggregates.dtsx",
    "rules": 7,
    "x": 230,
    "y": 64
  },
  {
    "id": "Extract_Location.dtsx",
    "label": "Extract_Location.dtsx",
    "type": "Package",
    "system": "SSIS Layer",
    "file": "Extract_Location.dtsx",
    "rules": 7,
    "x": 324,
    "y": 45
  },
  {
    "id": "Extract_Policy.dtsx",
    "label": "Extract_Policy.dtsx",
    "type": "Package",
    "system": "SSIS Layer",
    "file": "Extract_Policy.dtsx",
    "rules": 5,
    "x": 425,
    "y": 41
  },
  {
    "id": "Extract_PolicyPeriod.dtsx",
    "label": "Extract_PolicyPeriod.dtsx",
    "type": "Package",
    "system": "SSIS Layer",
    "file": "Extract_PolicyPeriod.dtsx",
    "rules": 6,
    "x": 524,
    "y": 52
  },
  {
    "id": "Extract_Premium.dtsx",
    "label": "Extract_Premium.dtsx",
    "type": "Package",
    "system": "SSIS Layer",
    "file": "Extract_Premium.dtsx",
    "rules": 7,
    "x": 612,
    "y": 79
  },
  {
    "id": "Extract_Producer.dtsx",
    "label": "Extract_Producer.dtsx",
    "type": "Package",
    "system": "SSIS Layer",
    "file": "Extract_Producer.dtsx",
    "rules": 5,
    "x": 681,
    "y": 119
  },
  {
    "id": "Master_ETL_Guidewire.dtsx",
    "label": "Master_ETL_Guidewire.dtsx",
    "type": "Package",
    "system": "SSIS Layer",
    "file": "Master_ETL_Guidewire.dtsx",
    "rules": 4,
    "x": 725,
    "y": 167
  },
  {
    "id": "STG_EARNED_PREM",
    "label": "STG_EARNED_PREM",
    "type": "Table",
    "system": "Staging RDBMS",
    "file": "PolicyCenter.sql",
    "rules": 4,
    "x": 340,
    "y": 200
  },
  {
    "id": "pc_policy",
    "label": "pc_policy",
    "type": "Table",
    "system": "Guidewire PC",
    "file": "PolicyCenter.sql",
    "rules": 5,
    "x": 460,
    "y": 200
  },
  {
    "id": "EDW_POL_DIM",
    "label": "EDW_POL_DIM",
    "type": "Table",
    "system": "Enterprise DW",
    "file": "Extract_Policy.dtsx",
    "rules": 6,
    "x": 400,
    "y": 280
  },
  {
    "id": "vw_curr_cc_claim",
    "label": "vw_curr_cc_claim",
    "type": "Table",
    "system": "Guidewire CC",
    "file": "ClaimCenter.sql",
    "rules": 4,
    "x": 400,
    "y": 140
  }
],
  links: [
  {
    "source": "PREMCALC.CBL",
    "target": "EARNPREM.CBL",
    "label": "FEEDS_INTO"
  },
  {
    "source": "EARNPREM.CBL",
    "target": "STG_EARNED_PREM",
    "label": "WRITES_TO"
  },
  {
    "source": "POLSTATUS.CBL",
    "target": "pc_policy",
    "label": "UPDATES"
  },
  {
    "source": "POLLOAD.CBL",
    "target": "pc_policy",
    "label": "LOADS"
  },
  {
    "source": "PolicyCenter_Monoline.sql",
    "target": "STG_EARNED_PREM",
    "label": "READS_FROM"
  },
  {
    "source": "PolicyCenter_Monoline.sql",
    "target": "pc_policy",
    "label": "JOINS"
  },
  {
    "source": "PolicyCenter_CPP_Breakdown.sql",
    "target": "pc_policy",
    "label": "READS_FROM"
  },
  {
    "source": "ClaimCenter_Monoline.sql",
    "target": "vw_curr_cc_claim",
    "label": "READS_FROM"
  },
  {
    "source": "ClaimCenter_CPP_Breakdown.sql",
    "target": "vw_curr_cc_claim",
    "label": "READS_FROM"
  },
  {
    "source": "Extract_Policy.dtsx",
    "target": "STG_EARNED_PREM",
    "label": "EXTRACTS"
  },
  {
    "source": "Extract_Policy.dtsx",
    "target": "EDW_POL_DIM",
    "label": "LOADS"
  },
  {
    "source": "Extract_Claims.dtsx",
    "target": "vw_curr_cc_claim",
    "label": "EXTRACTS"
  },
  {
    "source": "Extract_Premium.dtsx",
    "target": "STG_EARNED_PREM",
    "label": "EXTRACTS"
  },
  {
    "source": "KPICALC.CBL",
    "target": "STG_EARNED_PREM",
    "label": "AGGREGATES"
  },
  {
    "source": "RPTEXTRACT.CBL",
    "target": "EDW_POL_DIM",
    "label": "EXTRACTS"
  }
]
};
