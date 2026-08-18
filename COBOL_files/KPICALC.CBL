       IDENTIFICATION DIVISION.

       PROGRAM-ID. KPIREPORT.

      ******************************************************************

      * TASK 9 - REPORTING KPI CALCULATIONS

      * INPUTS:

      *   POLICY-IN  - TASK 8 STATUS-UPDATED POLICY EXTRACT

      *   PREMIUM-IN - TASK 7 EARNED PREMIUM EXTRACT

      *

      * BOTH INPUTS MUST BE SORTED BY POLICY-NO.

      * PROGRAM DETECTS OUT-OF-ORDER RECORDS.

      *

      * KPIS:

      * TOTAL/AC/PN/EX/CN POLICY COUNTS

      * HO/AU POLICY COUNTS

      * WRITTEN/EARNED/UNEARNED PREMIUM TOTALS

      * HO/AU PREMIUM TOTALS

      * RECONCILIATION: WRITTEN = EARNED + UNEARNED

      ******************************************************************

       ENVIRONMENT DIVISION.

       INPUT-OUTPUT SECTION.

       FILE-CONTROL.

           SELECT POLICY-IN ASSIGN TO POLIN

             ORGANIZATION IS SEQUENTIAL FILE STATUS IS WS-PI-ST.

           SELECT PREMIUM-IN ASSIGN TO PREMIN

             ORGANIZATION IS SEQUENTIAL FILE STATUS IS WS-PR-ST.

           SELECT KPI-OUT ASSIGN TO KPIOUT

             ORGANIZATION IS SEQUENTIAL FILE STATUS IS WS-KO-ST.

           SELECT ERROR-OUT ASSIGN TO ERROUT

             ORGANIZATION IS SEQUENTIAL FILE STATUS IS WS-ER-ST.
 
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
 
       FD PREMIUM-IN RECORD CONTAINS 65 CHARACTERS.

       01 PRI-REC.

          05 PRI-PREMIUM-ID       PIC X(12).

          05 PRI-POLICY-NO        PIC X(12).

          05 PRI-WRITTEN-PREMIUM  PIC 9(9)V99.

          05 PRI-EARNED-PREMIUM   PIC 9(9)V99.

          05 PRI-UNEARNED-PREMIUM PIC 9(9)V99.

          05 PRI-CALCULATION-DATE PIC 9(8).
 
       FD KPI-OUT RECORD CONTAINS 80 CHARACTERS.

       01 KPI-REC PIC X(80).
 
       FD ERROR-OUT RECORD CONTAINS 80 CHARACTERS.

       01 ER-REC.

          05 ER-POLICY-NO PIC X(12).

          05 ER-CODE      PIC X(4).

          05 ER-MESSAGE   PIC X(64).
 
       WORKING-STORAGE SECTION.

       01 WS-STATUS.

          05 WS-PI-ST PIC XX VALUE SPACES.

          05 WS-PR-ST PIC XX VALUE SPACES.

          05 WS-KO-ST PIC XX VALUE SPACES.

          05 WS-ER-ST PIC XX VALUE SPACES.
 
       01 WS-SWITCHES.

          05 WS-PI-EOF PIC X VALUE 'N'.

             88 PI-EOF VALUE 'Y'.

          05 WS-PR-EOF PIC X VALUE 'N'.

             88 PR-EOF VALUE 'Y'.

          05 WS-FATAL PIC X VALUE 'N'.

             88 FATAL-ERROR VALUE 'Y'.

          05 WS-PI-OPEN PIC X VALUE 'N'.

          05 WS-PR-OPEN PIC X VALUE 'N'.

          05 WS-KO-OPEN PIC X VALUE 'N'.

          05 WS-ER-OPEN PIC X VALUE 'N'.
 
       01 WS-SEQUENCE.

          05 WS-PREV-PI-POLICY PIC X(12) VALUE LOW-VALUES.

          05 WS-PREV-PR-POLICY PIC X(12) VALUE LOW-VALUES.
 
       01 WS-COUNTS.

          05 WS-TOTAL-POLICIES PIC 9(9) VALUE ZERO.

          05 WS-ACTIVE         PIC 9(9) VALUE ZERO.

          05 WS-PENDING        PIC 9(9) VALUE ZERO.

          05 WS-EXPIRED        PIC 9(9) VALUE ZERO.

          05 WS-CANCELLED      PIC 9(9) VALUE ZERO.

          05 WS-HO-COUNT       PIC 9(9) VALUE ZERO.

          05 WS-AU-COUNT       PIC 9(9) VALUE ZERO.

          05 WS-UNKNOWN-STATUS PIC 9(9) VALUE ZERO.

          05 WS-UNKNOWN-PROD   PIC 9(9) VALUE ZERO.

          05 WS-MISSING-PREM   PIC 9(9) VALUE ZERO.

          05 WS-ORPHAN-PREM    PIC 9(9) VALUE ZERO.

          05 WS-RECON-ERRORS   PIC 9(9) VALUE ZERO.

          05 WS-DQ-ERRORS      PIC 9(9) VALUE ZERO.

          05 WS-IO-ERRORS      PIC 9(9) VALUE ZERO.
 
       01 WS-TOTALS.

          05 WS-WRITTEN        PIC 9(15)V99 VALUE ZERO.

          05 WS-EARNED         PIC 9(15)V99 VALUE ZERO.

          05 WS-UNEARNED       PIC 9(15)V99 VALUE ZERO.

          05 WS-HO-WRITTEN     PIC 9(15)V99 VALUE ZERO.

          05 WS-HO-EARNED      PIC 9(15)V99 VALUE ZERO.

          05 WS-HO-UNEARNED    PIC 9(15)V99 VALUE ZERO.

          05 WS-AU-WRITTEN     PIC 9(15)V99 VALUE ZERO.

          05 WS-AU-EARNED      PIC 9(15)V99 VALUE ZERO.

          05 WS-AU-UNEARNED    PIC 9(15)V99 VALUE ZERO.

          05 WS-RECON-DIFF     PIC S9(15)V99 VALUE ZERO.

          05 WS-ABS-DIFF       PIC 9(15)V99 VALUE ZERO.

          05 WS-TOLERANCE      PIC 9V99 VALUE 0.01.
 
       01 WS-EDIT.

          05 WS-COUNT-EDIT PIC ZZZ,ZZZ,ZZ9.

          05 WS-AMT-EDIT   PIC ZZZ,ZZZ,ZZZ,ZZZ,ZZ9.99.

          05 WS-SIGNED-AMT-EDIT PIC -ZZZ,ZZZ,ZZZ,ZZZ,ZZ9.99.

          05 WS-LINE       PIC X(80).
 
       PROCEDURE DIVISION.

       MAIN.

           PERFORM OPEN-FILES

           IF FATAL-ERROR

              PERFORM CLOSE-FILES

              MOVE 12 TO RETURN-CODE

              GOBACK

           END-IF
 
           PERFORM READ-POLICY

           PERFORM READ-PREMIUM
 
           PERFORM UNTIL (PI-EOF AND PR-EOF) OR FATAL-ERROR

              IF PI-EOF

                 PERFORM HANDLE-ORPHAN-PREMIUM

              ELSE

                 IF PR-EOF

                    PERFORM HANDLE-MISSING-PREMIUM

                 ELSE

                    EVALUATE TRUE

                       WHEN PI-POLICY-NO = PRI-POLICY-NO

                          PERFORM PROCESS-MATCHED

                          PERFORM READ-POLICY

                          PERFORM READ-PREMIUM

                       WHEN PI-POLICY-NO < PRI-POLICY-NO

                          PERFORM HANDLE-MISSING-PREMIUM

                          PERFORM READ-POLICY

                       WHEN OTHER

                          PERFORM HANDLE-ORPHAN-PREMIUM

                          PERFORM READ-PREMIUM

                    END-EVALUATE

                 END-IF

              END-IF

           END-PERFORM
 
           IF NOT FATAL-ERROR

              PERFORM WRITE-KPI-REPORT

           END-IF

           PERFORM CLOSE-FILES
 
           DISPLAY 'KPI TOTAL POLICIES : ' WS-TOTAL-POLICIES

           DISPLAY 'KPI RECON ERRORS   : ' WS-RECON-ERRORS

           DISPLAY 'KPI DATA QUALITY    : ' WS-DQ-ERRORS

           DISPLAY 'KPI I/O ERRORS      : ' WS-IO-ERRORS
 
           IF FATAL-ERROR

              MOVE 12 TO RETURN-CODE

           ELSE

              IF WS-DQ-ERRORS > ZERO

                 MOVE 4 TO RETURN-CODE

              END-IF

           END-IF

           GOBACK.
 
       OPEN-FILES.

           OPEN INPUT POLICY-IN

           IF WS-PI-ST = '00'

              MOVE 'Y' TO WS-PI-OPEN

           ELSE

              DISPLAY 'POLICY OPEN ERROR ' WS-PI-ST

              SET FATAL-ERROR TO TRUE

           END-IF

           OPEN INPUT PREMIUM-IN

           IF WS-PR-ST = '00'

              MOVE 'Y' TO WS-PR-OPEN

           ELSE

              DISPLAY 'PREMIUM OPEN ERROR ' WS-PR-ST

              SET FATAL-ERROR TO TRUE

           END-IF

           OPEN OUTPUT KPI-OUT

           IF WS-KO-ST = '00'

              MOVE 'Y' TO WS-KO-OPEN

           ELSE

              DISPLAY 'KPI OUTPUT OPEN ERROR ' WS-KO-ST

              SET FATAL-ERROR TO TRUE

           END-IF

           OPEN OUTPUT ERROR-OUT

           IF WS-ER-ST = '00'

              MOVE 'Y' TO WS-ER-OPEN

           ELSE

              DISPLAY 'ERROR OUTPUT OPEN ERROR ' WS-ER-ST

              SET FATAL-ERROR TO TRUE

           END-IF.
 
       READ-POLICY.

           IF NOT PI-EOF

              READ POLICY-IN

                 AT END MOVE 'Y' TO WS-PI-EOF

                 NOT AT END

                    IF WS-PI-ST NOT = '00'

                       DISPLAY 'POLICY READ ERROR ' WS-PI-ST

                       ADD 1 TO WS-IO-ERRORS

                       SET FATAL-ERROR TO TRUE

                    ELSE

                       IF WS-PREV-PI-POLICY NOT = LOW-VALUES

                          AND PI-POLICY-NO < WS-PREV-PI-POLICY

                          DISPLAY 'POLICY INPUT OUT OF ORDER'

                          ADD 1 TO WS-IO-ERRORS

                          SET FATAL-ERROR TO TRUE

                       ELSE

                          MOVE PI-POLICY-NO TO WS-PREV-PI-POLICY

                       END-IF

                    END-IF

              END-READ

           END-IF.
 
       READ-PREMIUM.

           IF NOT PR-EOF

              READ PREMIUM-IN

                 AT END MOVE 'Y' TO WS-PR-EOF

                 NOT AT END

                    IF WS-PR-ST NOT = '00'

                       DISPLAY 'PREMIUM READ ERROR ' WS-PR-ST

                       ADD 1 TO WS-IO-ERRORS

                       SET FATAL-ERROR TO TRUE

                    ELSE

                       IF WS-PREV-PR-POLICY NOT = LOW-VALUES

                          AND PRI-POLICY-NO < WS-PREV-PR-POLICY

                          DISPLAY 'PREMIUM INPUT OUT OF ORDER'

                          ADD 1 TO WS-IO-ERRORS

                          SET FATAL-ERROR TO TRUE

                       ELSE

                          MOVE PRI-POLICY-NO TO WS-PREV-PR-POLICY

                       END-IF

                    END-IF

              END-READ

           END-IF.
 
       PROCESS-MATCHED.

           ADD 1 TO WS-TOTAL-POLICIES

           EVALUATE PI-POLICY-STATUS

              WHEN 'AC' ADD 1 TO WS-ACTIVE

              WHEN 'PN' ADD 1 TO WS-PENDING

              WHEN 'EX' ADD 1 TO WS-EXPIRED

              WHEN 'CN' ADD 1 TO WS-CANCELLED

              WHEN OTHER

                 ADD 1 TO WS-UNKNOWN-STATUS

                 ADD 1 TO WS-DQ-ERRORS

                 MOVE PI-POLICY-NO TO ER-POLICY-NO

                 MOVE 'K003' TO ER-CODE

                 MOVE 'UNKNOWN POLICY STATUS' TO ER-MESSAGE

                 PERFORM WRITE-ERROR

           END-EVALUATE
 
           ADD PRI-WRITTEN-PREMIUM TO WS-WRITTEN

           ADD PRI-EARNED-PREMIUM TO WS-EARNED

           ADD PRI-UNEARNED-PREMIUM TO WS-UNEARNED
 
           EVALUATE PI-PRODUCT-TYPE

              WHEN 'HO'

                 ADD 1 TO WS-HO-COUNT

                 ADD PRI-WRITTEN-PREMIUM TO WS-HO-WRITTEN

                 ADD PRI-EARNED-PREMIUM TO WS-HO-EARNED

                 ADD PRI-UNEARNED-PREMIUM TO WS-HO-UNEARNED

              WHEN 'AU'

                 ADD 1 TO WS-AU-COUNT

                 ADD PRI-WRITTEN-PREMIUM TO WS-AU-WRITTEN

                 ADD PRI-EARNED-PREMIUM TO WS-AU-EARNED

                 ADD PRI-UNEARNED-PREMIUM TO WS-AU-UNEARNED

              WHEN OTHER

                 ADD 1 TO WS-UNKNOWN-PROD

                 ADD 1 TO WS-DQ-ERRORS

                 MOVE PI-POLICY-NO TO ER-POLICY-NO

                 MOVE 'K004' TO ER-CODE

                 MOVE 'UNKNOWN PRODUCT TYPE' TO ER-MESSAGE

                 PERFORM WRITE-ERROR

           END-EVALUATE
 
           COMPUTE WS-RECON-DIFF =

              PRI-WRITTEN-PREMIUM -

              (PRI-EARNED-PREMIUM + PRI-UNEARNED-PREMIUM)

           COMPUTE WS-ABS-DIFF = FUNCTION ABS(WS-RECON-DIFF)

           IF WS-ABS-DIFF > WS-TOLERANCE

              ADD 1 TO WS-RECON-ERRORS

              ADD 1 TO WS-DQ-ERRORS

              MOVE PI-POLICY-NO TO ER-POLICY-NO

              MOVE 'K005' TO ER-CODE

              MOVE 'WRITTEN DOES NOT EQUAL EARNED PLUS UNEARNED'

                TO ER-MESSAGE

              PERFORM WRITE-ERROR

           END-IF.
 
       HANDLE-MISSING-PREMIUM.

           ADD 1 TO WS-MISSING-PREM

           ADD 1 TO WS-DQ-ERRORS

           MOVE PI-POLICY-NO TO ER-POLICY-NO

           MOVE 'K001' TO ER-CODE

           MOVE 'POLICY HAS NO MATCHING PREMIUM RECORD' TO ER-MESSAGE

           PERFORM WRITE-ERROR.
 
       HANDLE-ORPHAN-PREMIUM.

           ADD 1 TO WS-ORPHAN-PREM

           ADD 1 TO WS-DQ-ERRORS

           MOVE PRI-POLICY-NO TO ER-POLICY-NO

           MOVE 'K002' TO ER-CODE

           MOVE 'PREMIUM HAS NO MATCHING POLICY RECORD' TO ER-MESSAGE

           PERFORM WRITE-ERROR.
 
       WRITE-ERROR.

           IF ER-POLICY-NO = SPACES

              MOVE PI-POLICY-NO TO ER-POLICY-NO

           END-IF

           WRITE ER-REC

           IF WS-ER-ST NOT = '00'

              DISPLAY 'ERROR WRITE ERROR ' WS-ER-ST

              ADD 1 TO WS-IO-ERRORS

              SET FATAL-ERROR TO TRUE

           END-IF

           MOVE SPACES TO ER-REC.
 
       WRITE-KPI-REPORT.

           MOVE SPACES TO KPI-REC

           MOVE 'TFG PERSONAL LINES - TASK 9 KPI SUMMARY' TO KPI-REC

           PERFORM WRITE-KPI-LINE

           MOVE SPACES TO KPI-REC

           PERFORM WRITE-KPI-LINE
 
           MOVE WS-TOTAL-POLICIES TO WS-COUNT-EDIT

           STRING 'TOTAL POLICIES      |' WS-COUNT-EDIT

             DELIMITED BY SIZE INTO KPI-REC

           PERFORM WRITE-KPI-LINE

           MOVE WS-ACTIVE TO WS-COUNT-EDIT

           STRING 'ACTIVE POLICIES     |' WS-COUNT-EDIT

             DELIMITED BY SIZE INTO KPI-REC

           PERFORM WRITE-KPI-LINE

           MOVE WS-PENDING TO WS-COUNT-EDIT

           STRING 'PENDING POLICIES    |' WS-COUNT-EDIT

             DELIMITED BY SIZE INTO KPI-REC

           PERFORM WRITE-KPI-LINE

           MOVE WS-EXPIRED TO WS-COUNT-EDIT

           STRING 'EXPIRED POLICIES    |' WS-COUNT-EDIT

             DELIMITED BY SIZE INTO KPI-REC

           PERFORM WRITE-KPI-LINE

           MOVE WS-CANCELLED TO WS-COUNT-EDIT

           STRING 'CANCELLED POLICIES  |' WS-COUNT-EDIT

             DELIMITED BY SIZE INTO KPI-REC

           PERFORM WRITE-KPI-LINE
 
           MOVE WS-WRITTEN TO WS-AMT-EDIT

           STRING 'WRITTEN PREMIUM     |' WS-AMT-EDIT

             DELIMITED BY SIZE INTO KPI-REC

           PERFORM WRITE-KPI-LINE

           MOVE WS-EARNED TO WS-AMT-EDIT

           STRING 'EARNED PREMIUM      |' WS-AMT-EDIT

             DELIMITED BY SIZE INTO KPI-REC

           PERFORM WRITE-KPI-LINE

           MOVE WS-UNEARNED TO WS-AMT-EDIT

           STRING 'UNEARNED PREMIUM    |' WS-AMT-EDIT

             DELIMITED BY SIZE INTO KPI-REC

           PERFORM WRITE-KPI-LINE
 
           MOVE WS-HO-COUNT TO WS-COUNT-EDIT

           STRING 'HO POLICY COUNT     |' WS-COUNT-EDIT

             DELIMITED BY SIZE INTO KPI-REC

           PERFORM WRITE-KPI-LINE

           MOVE WS-HO-WRITTEN TO WS-AMT-EDIT

           STRING 'HO WRITTEN PREMIUM  |' WS-AMT-EDIT

             DELIMITED BY SIZE INTO KPI-REC

           PERFORM WRITE-KPI-LINE

           MOVE WS-HO-EARNED TO WS-AMT-EDIT

           STRING 'HO EARNED PREMIUM   |' WS-AMT-EDIT

             DELIMITED BY SIZE INTO KPI-REC

           PERFORM WRITE-KPI-LINE

           MOVE WS-HO-UNEARNED TO WS-AMT-EDIT

           STRING 'HO UNEARNED PREMIUM |' WS-AMT-EDIT

             DELIMITED BY SIZE INTO KPI-REC

           PERFORM WRITE-KPI-LINE
 
           MOVE WS-AU-COUNT TO WS-COUNT-EDIT

           STRING 'AU POLICY COUNT     |' WS-COUNT-EDIT

             DELIMITED BY SIZE INTO KPI-REC

           PERFORM WRITE-KPI-LINE

           MOVE WS-AU-WRITTEN TO WS-AMT-EDIT

           STRING 'AU WRITTEN PREMIUM  |' WS-AMT-EDIT

             DELIMITED BY SIZE INTO KPI-REC

           PERFORM WRITE-KPI-LINE

           MOVE WS-AU-EARNED TO WS-AMT-EDIT

           STRING 'AU EARNED PREMIUM   |' WS-AMT-EDIT

             DELIMITED BY SIZE INTO KPI-REC

           PERFORM WRITE-KPI-LINE

           MOVE WS-AU-UNEARNED TO WS-AMT-EDIT

           STRING 'AU UNEARNED PREMIUM |' WS-AMT-EDIT

             DELIMITED BY SIZE INTO KPI-REC

           PERFORM WRITE-KPI-LINE
 
           COMPUTE WS-RECON-DIFF =

              WS-WRITTEN - (WS-EARNED + WS-UNEARNED)

           MOVE WS-RECON-DIFF TO WS-SIGNED-AMT-EDIT

           STRING 'TOTAL RECON DIFF    |' WS-SIGNED-AMT-EDIT

             DELIMITED BY SIZE INTO KPI-REC

           PERFORM WRITE-KPI-LINE.
 
       WRITE-KPI-LINE.

           WRITE KPI-REC

           IF WS-KO-ST NOT = '00'

              DISPLAY 'KPI WRITE ERROR ' WS-KO-ST

              ADD 1 TO WS-IO-ERRORS

              SET FATAL-ERROR TO TRUE

           END-IF

           MOVE SPACES TO KPI-REC.
 
       CLOSE-FILES.

           IF WS-PI-OPEN = 'Y'

              CLOSE POLICY-IN

              IF WS-PI-ST NOT = '00'

                 DISPLAY 'POLICY CLOSE ERROR ' WS-PI-ST

                 ADD 1 TO WS-IO-ERRORS

                 SET FATAL-ERROR TO TRUE

              ELSE

                 MOVE 'N' TO WS-PI-OPEN

              END-IF

           END-IF

           IF WS-PR-OPEN = 'Y'

              CLOSE PREMIUM-IN

              IF WS-PR-ST NOT = '00'

                 DISPLAY 'PREMIUM CLOSE ERROR ' WS-PR-ST

                 ADD 1 TO WS-IO-ERRORS

                 SET FATAL-ERROR TO TRUE

              ELSE

                 MOVE 'N' TO WS-PR-OPEN

              END-IF

           END-IF

           IF WS-KO-OPEN = 'Y'

              CLOSE KPI-OUT

              IF WS-KO-ST NOT = '00'

                 DISPLAY 'KPI CLOSE ERROR ' WS-KO-ST

                 ADD 1 TO WS-IO-ERRORS

                 SET FATAL-ERROR TO TRUE

              ELSE

                 MOVE 'N' TO WS-KO-OPEN

              END-IF

           END-IF

           IF WS-ER-OPEN = 'Y'

              CLOSE ERROR-OUT

              IF WS-ER-ST NOT = '00'

                 DISPLAY 'ERROR CLOSE ERROR ' WS-ER-ST

                 ADD 1 TO WS-IO-ERRORS

                 SET FATAL-ERROR TO TRUE

              ELSE

                 MOVE 'N' TO WS-ER-OPEN

              END-IF

           END-IF.

 