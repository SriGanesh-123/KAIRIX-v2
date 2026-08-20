IDENTIFICATION DIVISION.
       PROGRAM-ID. PREMCALC.
      ******************************************************************
      * TASK 6 - PREMIUM CALCULATION
      *
      * DEPENDENCY:
      *   RUNS AFTER TASK 5 POLLOAD. POLICY-IN MUST CONTAIN VALIDATED
      *   POLICIES FROM THE TASK-5 PROCESSING FLOW.
      *
      * RATING RULE STATUS:
      *   PROJECT/DEMO RULES ONLY. OFFICIAL TFG RATING TABLES WERE NOT
      *   PROVIDED. ALL RATES ARE ISOLATED IN WS-RATING-CONSTANTS.
      *
      * MULTIPLE COVERAGES:
      *   ALL COVERAGE RECORDS FOR A POLICY ARE ACCUMULATED.
      *
      * PREMIUM ID:
      *   12 BYTES = FIRST 6 BYTES OF POLICY-NO + YYMMDD CALC DATE.
      *   THIS SUPPORTS DATE-BASED PREMIUM HISTORY WITHOUT CHANGING THE
      *   TASK-2/TASK-3 PREMFILE 12-BYTE PREMIUM-ID.
      *   ASSUMPTION: ONE PREMIUM CALCULATION PER POLICY PER DAY.
      *
      * INPUT ACCESS:
      *   POLICY, PROPERTY, VEHICLE AND COVERAGE CALCULATION EXTRACTS
      *   MUST BE SORTED BY POLICY-NO. TASK-4 KSDS PRIMARY KEYS FOR
      *   PROPERTY/VEHICLE/COVERAGE ARE NOT POLICY-NO.
      ******************************************************************
 
       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT POLICY-IN ASSIGN TO POLIN
             ORGANIZATION IS SEQUENTIAL
             FILE STATUS IS WS-PI-ST.
           SELECT PROPERTY-IN ASSIGN TO PROPIN
             ORGANIZATION IS SEQUENTIAL
             FILE STATUS IS WS-PR-ST.
           SELECT VEHICLE-IN ASSIGN TO VEHIN
             ORGANIZATION IS SEQUENTIAL
             FILE STATUS IS WS-VE-ST.
           SELECT COVERAGE-IN ASSIGN TO COVGIN
             ORGANIZATION IS SEQUENTIAL
             FILE STATUS IS WS-CO-ST.
           SELECT PREMIUM-OUT ASSIGN TO PREMOUT
             ORGANIZATION IS SEQUENTIAL
             FILE STATUS IS WS-PO-ST.
           SELECT ERROR-OUT ASSIGN TO ERROUT
             ORGANIZATION IS SEQUENTIAL
             FILE STATUS IS WS-ER-ST.
 
       DATA DIVISION.
       FILE SECTION.
 
       FD POLICY-IN RECORD CONTAINS 77 CHARACTERS.
       01 PI-REC.
          05 PI-POLICY-NO       PIC X(12).
          05 PI-CUSTOMER-ID     PIC X(9).
          05 PI-AGENT-ID        PIC X(9).
          05 PI-PRODUCT-TYPE    PIC X(2).
          05 PI-POLICY-STATUS   PIC X(2).
          05 PI-EFFECTIVE-DATE  PIC 9(8).
          05 PI-EXPIRY-DATE     PIC 9(8).
          05 PI-WRITTEN-PREMIUM PIC 9(9)V99.
          05 PI-CREATE-DT       PIC 9(8).
          05 PI-UPDATE-DT       PIC 9(8).
 
       FD PROPERTY-IN RECORD CONTAINS 172 CHARACTERS.
       01 PR-REC.
          05 PR-PROPERTY-ID       PIC X(12).
          05 PR-POLICY-NO         PIC X(12).
          05 PR-PROPERTY-TYPE     PIC X(2).
          05 PR-ADDRESS           PIC X(100).
          05 PR-CONSTRUCTION-TYPE PIC X(30).
          05 PR-YEAR-BUILT        PIC 9(4).
          05 PR-PROPERTY-VALUE    PIC 9(10)V99.
 
       FD VEHICLE-IN RECORD CONTAINS 117 CHARACTERS.
       01 VE-REC.
          05 VE-VEHICLE-ID        PIC X(12).
          05 VE-POLICY-NO         PIC X(12).
          05 VE-VIN               PIC X(17).
          05 VE-MAKE              PIC X(30).
          05 VE-MODEL             PIC X(30).
          05 VE-YEAR              PIC 9(4).
          05 VE-VEHICLE-VALUE     PIC 9(10)V99.
 
       FD COVERAGE-IN RECORD CONTAINS 66 CHARACTERS.
       01 CO-REC.
          05 CO-COVERAGE-ID       PIC X(12).
          05 CO-POLICY-NO         PIC X(12).
          05 CO-COVERAGE-TYPE     PIC X(4).
          05 CO-COVERAGE-LIMIT    PIC 9(10)V99.
          05 CO-DEDUCTIBLE        PIC 9(8)V99.
          05 CO-EFFECTIVE-DATE    PIC 9(8).
          05 CO-EXPIRY-DATE       PIC 9(8).
 
       FD PREMIUM-OUT RECORD CONTAINS 65 CHARACTERS.
       01 PO-REC.
          05 PO-PREMIUM-ID        PIC X(12).
          05 PO-POLICY-NO         PIC X(12).
          05 PO-WRITTEN-PREMIUM   PIC 9(9)V99.
          05 PO-EARNED-PREMIUM    PIC 9(9)V99.
          05 PO-UNEARNED-PREMIUM  PIC 9(9)V99.
          05 PO-CALCULATION-DATE  PIC 9(8).
 
       FD ERROR-OUT RECORD CONTAINS 70 CHARACTERS.
       01 ER-REC.
          05 ER-POLICY-NO         PIC X(12).
          05 ER-CODE              PIC X(4).
          05 ER-MESSAGE           PIC X(54).
 
       WORKING-STORAGE SECTION.
       01 WS-FILE-STATUS.
          05 WS-PI-ST PIC XX VALUE SPACES.
          05 WS-PR-ST PIC XX VALUE SPACES.
          05 WS-VE-ST PIC XX VALUE SPACES.
          05 WS-CO-ST PIC XX VALUE SPACES.
          05 WS-PO-ST PIC XX VALUE SPACES.
          05 WS-ER-ST PIC XX VALUE SPACES.
 
       01 WS-SWITCHES.
          05 WS-POL-EOF PIC X VALUE 'N'.
             88 POL-EOF VALUE 'Y'.
          05 WS-PR-EOF PIC X VALUE 'N'.
             88 PR-EOF VALUE 'Y'.
          05 WS-VE-EOF PIC X VALUE 'N'.
             88 VE-EOF VALUE 'Y'.
          05 WS-CO-EOF PIC X VALUE 'N'.
             88 CO-EOF VALUE 'Y'.
          05 WS-PR-FOUND PIC X VALUE 'N'.
          05 WS-VE-FOUND PIC X VALUE 'N'.
          05 WS-CO-FOUND PIC X VALUE 'N'.
          05 WS-FATAL PIC X VALUE 'N'.
             88 FATAL-ERROR VALUE 'Y'.
 
      * PROJECT/DEMO CONSTANTS - REPLACE WITH APPROVED TFG RATES.
       01 WS-RATING-CONSTANTS.
          05 WS-HO-BASE       PIC 9(5)V99 VALUE 100.00.
          05 WS-HO-RISK-RATE  PIC 9V9(6) VALUE 0.002000.
          05 WS-HO-COV-RATE   PIC 9V9(6) VALUE 0.001000.
          05 WS-HO-DED-RATE   PIC 9V9(6) VALUE 0.050000.
          05 WS-HO-MIN        PIC 9(5)V99 VALUE 150.00.
          05 WS-HO-MAX-DISC   PIC 9(5)V99 VALUE 100.00.
          05 WS-AU-BASE       PIC 9(5)V99 VALUE 75.00.
          05 WS-AU-RISK-RATE  PIC 9V9(6) VALUE 0.015000.
          05 WS-AU-COV-RATE   PIC 9V9(6) VALUE 0.000800.
          05 WS-AU-DED-RATE   PIC 9V9(6) VALUE 0.030000.
          05 WS-AU-MIN        PIC 9(5)V99 VALUE 125.00.
          05 WS-AU-MAX-DISC   PIC 9(5)V99 VALUE 75.00.
 
       01 WS-CALC.
          05 WS-RISK-VALUE       PIC 9(12)V99 VALUE ZERO.
          05 WS-COV-LIMIT-TOTAL  PIC 9(12)V99 VALUE ZERO.
          05 WS-DEDUCT-TOTAL     PIC 9(12)V99 VALUE ZERO.
          05 WS-DISCOUNT         PIC 9(9)V99 VALUE ZERO.
          05 WS-PREMIUM          PIC 9(9)V99 VALUE ZERO.
          05 WS-CURRENT-DATE     PIC 9(8).
          05 WS-COVERAGE-COUNT   PIC 9(5) VALUE ZERO.
 
       01 WS-COUNTERS.
          05 WS-READ             PIC 9(9) VALUE ZERO.
          05 WS-CALCULATED       PIC 9(9) VALUE ZERO.
          05 WS-ERRORS           PIC 9(9) VALUE ZERO.
          05 WS-IO-ERRORS        PIC 9(9) VALUE ZERO.
 
       PROCEDURE DIVISION.
       MAIN.
           MOVE FUNCTION CURRENT-DATE(1:8) TO WS-CURRENT-DATE
           PERFORM OPEN-FILES
           IF FATAL-ERROR GOBACK END-IF
 
           PERFORM READ-PROPERTY
           PERFORM READ-VEHICLE
           PERFORM READ-COVERAGE
 
           PERFORM UNTIL POL-EOF OR FATAL-ERROR
              PERFORM READ-POLICY
              IF NOT POL-EOF AND NOT FATAL-ERROR
                 ADD 1 TO WS-READ
                 PERFORM PROCESS-POLICY
              END-IF
           END-PERFORM
 
           PERFORM CLOSE-FILES
           DISPLAY 'PREMCALC READ       : ' WS-READ
           DISPLAY 'PREMCALC CALCULATED : ' WS-CALCULATED
           DISPLAY 'PREMCALC ERRORS     : ' WS-ERRORS
           DISPLAY 'PREMCALC I/O ERRORS : ' WS-IO-ERRORS
           IF FATAL-ERROR MOVE 12 TO RETURN-CODE END-IF
           GOBACK.
 
       OPEN-FILES.
           OPEN INPUT POLICY-IN PROPERTY-IN VEHICLE-IN COVERAGE-IN
                OUTPUT PREMIUM-OUT ERROR-OUT
           IF WS-PI-ST NOT = '00'
              DISPLAY 'POLICY OPEN ERROR ' WS-PI-ST
              SET FATAL-ERROR TO TRUE
           END-IF
           IF WS-PR-ST NOT = '00'
              DISPLAY 'PROPERTY OPEN ERROR ' WS-PR-ST
              SET FATAL-ERROR TO TRUE
           END-IF
           IF WS-VE-ST NOT = '00'
              DISPLAY 'VEHICLE OPEN ERROR ' WS-VE-ST
              SET FATAL-ERROR TO TRUE
           END-IF
           IF WS-CO-ST NOT = '00'
              DISPLAY 'COVERAGE OPEN ERROR ' WS-CO-ST
              SET FATAL-ERROR TO TRUE
           END-IF
           IF WS-PO-ST NOT = '00'
              DISPLAY 'PREMIUM OUTPUT OPEN ERROR ' WS-PO-ST
              SET FATAL-ERROR TO TRUE
           END-IF
           IF WS-ER-ST NOT = '00'
              DISPLAY 'ERROR OUTPUT OPEN ERROR ' WS-ER-ST
              SET FATAL-ERROR TO TRUE
           END-IF.
 
       READ-POLICY.
           READ POLICY-IN
              AT END
                 MOVE 'Y' TO WS-POL-EOF
              NOT AT END
                 IF WS-PI-ST NOT = '00'
                    DISPLAY 'POLICY READ ERROR ' WS-PI-ST
                    ADD 1 TO WS-IO-ERRORS
                    SET FATAL-ERROR TO TRUE
                 END-IF
           END-READ.
 
       READ-PROPERTY.
           IF NOT PR-EOF
              READ PROPERTY-IN
                 AT END
                    MOVE 'Y' TO WS-PR-EOF
                 NOT AT END
                    IF WS-PR-ST NOT = '00'
                       DISPLAY 'PROPERTY READ ERROR ' WS-PR-ST
                       ADD 1 TO WS-IO-ERRORS
                       SET FATAL-ERROR TO TRUE
                    END-IF
              END-READ
           END-IF.
 
       READ-VEHICLE.
           IF NOT VE-EOF
              READ VEHICLE-IN
                 AT END
                    MOVE 'Y' TO WS-VE-EOF
                 NOT AT END
                    IF WS-VE-ST NOT = '00'
                       DISPLAY 'VEHICLE READ ERROR ' WS-VE-ST
                       ADD 1 TO WS-IO-ERRORS
                       SET FATAL-ERROR TO TRUE
                    END-IF
              END-READ
           END-IF.
 
       READ-COVERAGE.
           IF NOT CO-EOF
              READ COVERAGE-IN
                 AT END
                    MOVE 'Y' TO WS-CO-EOF
                 NOT AT END
                    IF WS-CO-ST NOT = '00'
                       DISPLAY 'COVERAGE READ ERROR ' WS-CO-ST
                       ADD 1 TO WS-IO-ERRORS
                       SET FATAL-ERROR TO TRUE
                    END-IF
              END-READ
           END-IF.
 
       PROCESS-POLICY.
           MOVE ZERO TO WS-RISK-VALUE
                        WS-COV-LIMIT-TOTAL
                        WS-DEDUCT-TOTAL
                        WS-DISCOUNT
                        WS-PREMIUM
                        WS-COVERAGE-COUNT
 
           IF PI-PRODUCT-TYPE = 'HO'
              PERFORM GET-PROPERTY
              IF WS-PR-FOUND = 'Y'
                 PERFORM GET-ALL-COVERAGES
                 IF WS-CO-FOUND = 'Y'
                    PERFORM CALC-HO
                    PERFORM WRITE-PREMIUM
                 ELSE
                    MOVE 'P003' TO ER-CODE
                    MOVE 'NO COVERAGE RECORDS FOR POLICY' TO ER-MESSAGE
                    PERFORM WRITE-ERROR
                 END-IF
              ELSE
                 MOVE 'P001' TO ER-CODE
                 MOVE 'HOMEOWNERS PROPERTY RECORD NOT FOUND'
                   TO ER-MESSAGE
                 PERFORM WRITE-ERROR
              END-IF
           ELSE
              IF PI-PRODUCT-TYPE = 'AU'
                 PERFORM GET-VEHICLE
                 IF WS-VE-FOUND = 'Y'
                    PERFORM GET-ALL-COVERAGES
                    IF WS-CO-FOUND = 'Y'
                       PERFORM CALC-AU
                       PERFORM WRITE-PREMIUM
                    ELSE
                       MOVE 'P003' TO ER-CODE
                       MOVE 'NO COVERAGE RECORDS FOR POLICY'
                         TO ER-MESSAGE
                       PERFORM WRITE-ERROR
                    END-IF
                 ELSE
                    MOVE 'P002' TO ER-CODE
                    MOVE 'AUTO VEHICLE RECORD NOT FOUND' TO ER-MESSAGE
                    PERFORM WRITE-ERROR
                 END-IF
              ELSE
                 MOVE 'P004' TO ER-CODE
                 MOVE 'PRODUCT TYPE MUST BE HO OR AU' TO ER-MESSAGE
                 PERFORM WRITE-ERROR
              END-IF
           END-IF.
 
       GET-PROPERTY.
           MOVE 'N' TO WS-PR-FOUND
           PERFORM UNTIL PR-EOF OR FATAL-ERROR
              IF PR-POLICY-NO < PI-POLICY-NO
                 PERFORM READ-PROPERTY
              ELSE
                 IF PR-POLICY-NO = PI-POLICY-NO
                    MOVE PR-PROPERTY-VALUE TO WS-RISK-VALUE
                    MOVE 'Y' TO WS-PR-FOUND
                 END-IF
                 EXIT PERFORM
              END-IF
           END-PERFORM.
 
       GET-VEHICLE.
           MOVE 'N' TO WS-VE-FOUND
           PERFORM UNTIL VE-EOF OR FATAL-ERROR
              IF VE-POLICY-NO < PI-POLICY-NO
                 PERFORM READ-VEHICLE
              ELSE
                 IF VE-POLICY-NO = PI-POLICY-NO
                    MOVE VE-VEHICLE-VALUE TO WS-RISK-VALUE
                    MOVE 'Y' TO WS-VE-FOUND
                 END-IF
                 EXIT PERFORM
              END-IF
           END-PERFORM.
 
       GET-ALL-COVERAGES.
           MOVE 'N' TO WS-CO-FOUND
           PERFORM UNTIL CO-EOF OR FATAL-ERROR
              IF CO-POLICY-NO < PI-POLICY-NO
                 PERFORM READ-COVERAGE
              ELSE
                 IF CO-POLICY-NO = PI-POLICY-NO
                    MOVE 'Y' TO WS-CO-FOUND
                    ADD CO-COVERAGE-LIMIT TO WS-COV-LIMIT-TOTAL
                    ADD CO-DEDUCTIBLE TO WS-DEDUCT-TOTAL
                    ADD 1 TO WS-COVERAGE-COUNT
                    PERFORM READ-COVERAGE
                 ELSE
                    EXIT PERFORM
                 END-IF
              END-IF
           END-PERFORM.
 
       CALC-HO.
           COMPUTE WS-DISCOUNT ROUNDED =
              WS-DEDUCT-TOTAL * WS-HO-DED-RATE
           IF WS-DISCOUNT > WS-HO-MAX-DISC
              MOVE WS-HO-MAX-DISC TO WS-DISCOUNT
           END-IF
           COMPUTE WS-PREMIUM ROUNDED =
              WS-HO-BASE
              + (WS-RISK-VALUE * WS-HO-RISK-RATE)
              + (WS-COV-LIMIT-TOTAL * WS-HO-COV-RATE)
              - WS-DISCOUNT
           IF WS-PREMIUM < WS-HO-MIN
              MOVE WS-HO-MIN TO WS-PREMIUM
           END-IF.
 
       CALC-AU.
           COMPUTE WS-DISCOUNT ROUNDED =
              WS-DEDUCT-TOTAL * WS-AU-DED-RATE
           IF WS-DISCOUNT > WS-AU-MAX-DISC
              MOVE WS-AU-MAX-DISC TO WS-DISCOUNT
           END-IF
           COMPUTE WS-PREMIUM ROUNDED =
              WS-AU-BASE
              + (WS-RISK-VALUE * WS-AU-RISK-RATE)
              + (WS-COV-LIMIT-TOTAL * WS-AU-COV-RATE)
              - WS-DISCOUNT
           IF WS-PREMIUM < WS-AU-MIN
              MOVE WS-AU-MIN TO WS-PREMIUM
           END-IF.
 
       WRITE-PREMIUM.
           MOVE PI-POLICY-NO(1:6) TO PO-PREMIUM-ID(1:6)
           MOVE WS-CURRENT-DATE(3:6) TO PO-PREMIUM-ID(7:6)
           MOVE PI-POLICY-NO TO PO-POLICY-NO
           MOVE WS-PREMIUM TO PO-WRITTEN-PREMIUM
           MOVE ZERO TO PO-EARNED-PREMIUM
           MOVE WS-PREMIUM TO PO-UNEARNED-PREMIUM
           MOVE WS-CURRENT-DATE TO PO-CALCULATION-DATE
           WRITE PO-REC
           IF WS-PO-ST = '00'
              ADD 1 TO WS-CALCULATED
           ELSE
              ADD 1 TO WS-IO-ERRORS
              MOVE 'P901' TO ER-CODE
              MOVE 'PREMIUM OUTPUT WRITE FAILED' TO ER-MESSAGE
              PERFORM WRITE-ERROR
           END-IF.
 
       WRITE-ERROR.
           MOVE PI-POLICY-NO TO ER-POLICY-NO
           WRITE ER-REC
           IF WS-ER-ST = '00'
              ADD 1 TO WS-ERRORS
           ELSE
              DISPLAY 'ERROR OUTPUT WRITE FAILED ' WS-ER-ST
              ADD 1 TO WS-IO-ERRORS
              SET FATAL-ERROR TO TRUE
           END-IF.
 
       CLOSE-FILES.
           CLOSE POLICY-IN PROPERTY-IN VEHICLE-IN COVERAGE-IN
                 PREMIUM-OUT ERROR-OUT.