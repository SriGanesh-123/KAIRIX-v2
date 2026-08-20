       IDENTIFICATION DIVISION.

       PROGRAM-ID. EARNPREM.

      ******************************************************************

      * TASK 7 - CORRECTED EARNED PREMIUM CALCULATION

      * DEPENDS ON TASK 5 POLLOAD AND TASK 6 PREMCALC.

      *

      * PROJECT ASSUMPTION:

      * EARNED = WRITTEN * EARNED-DAYS / TERM-DAYS.

      * TERM AND EARNED DAYS ARE INCLUSIVE (+1).

      *

      * CANCELLATION/ENDORSEMENT RULES ARE NOT INVENTED. THE CURRENT

      * TASK-2/3 LAYOUT HAS NO CANCELLATION DATE OR ENDORSEMENT PREMIUM

      * TRANSACTION FIELDS. ADD THEM WHEN APPROVED RULES ARE PROVIDED.

      ******************************************************************

       ENVIRONMENT DIVISION.

       INPUT-OUTPUT SECTION.

       FILE-CONTROL.

           SELECT POLICY-IN ASSIGN TO POLIN

             ORGANIZATION IS SEQUENTIAL FILE STATUS IS WS-PI-ST.

           SELECT PREMIUM-IN ASSIGN TO PREMIN

             ORGANIZATION IS SEQUENTIAL FILE STATUS IS WS-PR-ST.

           SELECT PREMIUM-OUT ASSIGN TO PREMOUT

             ORGANIZATION IS SEQUENTIAL FILE STATUS IS WS-PO-ST.

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
 
       FD PREMIUM-OUT RECORD CONTAINS 65 CHARACTERS.

       01 PRO-REC.

          05 PRO-PREMIUM-ID       PIC X(12).

          05 PRO-POLICY-NO        PIC X(12).

          05 PRO-WRITTEN-PREMIUM  PIC 9(9)V99.

          05 PRO-EARNED-PREMIUM   PIC 9(9)V99.

          05 PRO-UNEARNED-PREMIUM PIC 9(9)V99.

          05 PRO-CALCULATION-DATE PIC 9(8).
 
       FD ERROR-OUT RECORD CONTAINS 70 CHARACTERS.

       01 ER-REC.

          05 ER-POLICY-NO PIC X(12).

          05 ER-CODE PIC X(4).

          05 ER-MESSAGE PIC X(54).
 
       WORKING-STORAGE SECTION.

       01 WS-STATUS.

          05 WS-PI-ST PIC XX VALUE SPACES.

          05 WS-PR-ST PIC XX VALUE SPACES.

          05 WS-PO-ST PIC XX VALUE SPACES.

          05 WS-ER-ST PIC XX VALUE SPACES.

       01 WS-SW.

          05 WS-POL-EOF PIC X VALUE 'N'.

             88 POL-EOF VALUE 'Y'.

          05 WS-PREM-EOF PIC X VALUE 'N'.

             88 PREM-EOF VALUE 'Y'.

          05 WS-POL-FOUND PIC X VALUE 'N'.

          05 WS-FATAL PIC X VALUE 'N'.

             88 FATAL-ERROR VALUE 'Y'.

          05 WS-DATE-VALID PIC X VALUE 'N'.

       01 WS-SEQUENCE.

          05 WS-PREV-POLICY PIC X(12) VALUE LOW-VALUES.

          05 WS-PREV-PREMIUM-POLICY PIC X(12) VALUE LOW-VALUES.

       01 WS-DATE-WORK.

          05 WS-DATE-IN PIC 9(8).

          05 WS-YEAR PIC 9(4).

          05 WS-MONTH PIC 99.

          05 WS-DAY PIC 99.

          05 WS-MAX-DAY PIC 99.

          05 WS-LEAP PIC X.

          05 WS-REM4 PIC 9(4).

          05 WS-REM100 PIC 9(4).

          05 WS-REM400 PIC 9(4).

          05 WS-EFF-INT PIC 9(9).

          05 WS-EXP-INT PIC 9(9).

          05 WS-CALC-INT PIC 9(9).

          05 WS-TERM-DAYS PIC 9(9).

          05 WS-EARNED-DAYS PIC 9(9).

       01 WS-AMOUNTS.

          05 WS-EARNED PIC 9(9)V99.

          05 WS-UNEARNED PIC 9(9)V99.

       01 WS-COUNTERS.

          05 WS-READ PIC 9(9) VALUE ZERO.

          05 WS-CALCULATED PIC 9(9) VALUE ZERO.

          05 WS-ERRORS PIC 9(9) VALUE ZERO.

          05 WS-IO-ERRORS PIC 9(9) VALUE ZERO.
 
       PROCEDURE DIVISION.

       MAIN.

           PERFORM OPEN-FILES

           IF FATAL-ERROR GOBACK END-IF

           PERFORM READ-POLICY

           PERFORM UNTIL PREM-EOF OR FATAL-ERROR

              PERFORM READ-PREMIUM

              IF NOT PREM-EOF AND NOT FATAL-ERROR

                 ADD 1 TO WS-READ

                 PERFORM PROCESS-PREMIUM

              END-IF

           END-PERFORM

           PERFORM CLOSE-FILES

           DISPLAY 'EARNPREM READ       : ' WS-READ

           DISPLAY 'EARNPREM CALCULATED : ' WS-CALCULATED

           DISPLAY 'EARNPREM ERRORS     : ' WS-ERRORS

           DISPLAY 'EARNPREM I/O ERRORS : ' WS-IO-ERRORS

           IF FATAL-ERROR MOVE 12 TO RETURN-CODE END-IF

           GOBACK.
 
       OPEN-FILES.

           OPEN INPUT POLICY-IN PREMIUM-IN

                OUTPUT PREMIUM-OUT ERROR-OUT

           IF WS-PI-ST NOT = '00'

              DISPLAY 'POLICY OPEN ERROR ' WS-PI-ST

              SET FATAL-ERROR TO TRUE

           END-IF

           IF WS-PR-ST NOT = '00'

              DISPLAY 'PREMIUM OPEN ERROR ' WS-PR-ST

              SET FATAL-ERROR TO TRUE

           END-IF

           IF WS-PO-ST NOT = '00'

              DISPLAY 'OUTPUT OPEN ERROR ' WS-PO-ST

              SET FATAL-ERROR TO TRUE

           END-IF

           IF WS-ER-ST NOT = '00'

              DISPLAY 'ERROR FILE OPEN ERROR ' WS-ER-ST

              SET FATAL-ERROR TO TRUE

           END-IF.
 
       READ-POLICY.

           IF NOT POL-EOF

              READ POLICY-IN

                AT END MOVE 'Y' TO WS-POL-EOF

                NOT AT END

                  IF WS-PI-ST NOT = '00'

                     DISPLAY 'POLICY READ ERROR ' WS-PI-ST

                     ADD 1 TO WS-IO-ERRORS

                     SET FATAL-ERROR TO TRUE

                  ELSE

                     IF WS-PREV-POLICY NOT = LOW-VALUES

                        AND PI-POLICY-NO < WS-PREV-POLICY

                        DISPLAY 'POLICY INPUT OUT OF ORDER: '

                          PI-POLICY-NO

                        ADD 1 TO WS-IO-ERRORS

                        SET FATAL-ERROR TO TRUE

                     ELSE

                        MOVE PI-POLICY-NO TO WS-PREV-POLICY

                     END-IF

                  END-IF

              END-READ

           END-IF.
 
       READ-PREMIUM.

           IF NOT PREM-EOF

              READ PREMIUM-IN

                AT END MOVE 'Y' TO WS-PREM-EOF

                NOT AT END

                  IF WS-PR-ST NOT = '00'

                     DISPLAY 'PREMIUM READ ERROR ' WS-PR-ST

                     ADD 1 TO WS-IO-ERRORS

                     SET FATAL-ERROR TO TRUE

                  ELSE

                     IF WS-PREV-PREMIUM-POLICY NOT = LOW-VALUES

                        AND PRI-POLICY-NO < WS-PREV-PREMIUM-POLICY

                        DISPLAY 'PREMIUM INPUT OUT OF ORDER: '

                          PRI-POLICY-NO

                        ADD 1 TO WS-IO-ERRORS

                        SET FATAL-ERROR TO TRUE

                     ELSE

                        MOVE PRI-POLICY-NO

                          TO WS-PREV-PREMIUM-POLICY

                     END-IF

                  END-IF

              END-READ

           END-IF.
 
       PROCESS-PREMIUM.

           MOVE 'N' TO WS-POL-FOUND

           PERFORM FIND-POLICY

           IF WS-POL-FOUND = 'Y'

              PERFORM VALIDATE-DATES

           ELSE

              MOVE 'E001' TO ER-CODE

              MOVE 'POLICY NOT FOUND FOR PREMIUM RECORD' TO ER-MESSAGE

              PERFORM WRITE-ERROR

           END-IF.
 
       FIND-POLICY.

           PERFORM UNTIL POL-EOF OR FATAL-ERROR

              IF PI-POLICY-NO < PRI-POLICY-NO

                 PERFORM READ-POLICY

              ELSE

                 IF PI-POLICY-NO = PRI-POLICY-NO

                    MOVE 'Y' TO WS-POL-FOUND

                 END-IF

                 EXIT PERFORM

              END-IF

           END-PERFORM.
 
       VALIDATE-DATES.

           MOVE PI-EFFECTIVE-DATE TO WS-DATE-IN

           PERFORM VALIDATE-CALENDAR-DATE

           IF WS-DATE-VALID NOT = 'Y'

              MOVE 'E002' TO ER-CODE

              MOVE 'INVALID POLICY EFFECTIVE DATE' TO ER-MESSAGE

              PERFORM WRITE-ERROR

           ELSE

              MOVE PI-EXPIRY-DATE TO WS-DATE-IN

              PERFORM VALIDATE-CALENDAR-DATE

              IF WS-DATE-VALID NOT = 'Y'

                 MOVE 'E003' TO ER-CODE

                 MOVE 'INVALID POLICY EXPIRY DATE' TO ER-MESSAGE

                 PERFORM WRITE-ERROR

              ELSE

                 MOVE PRI-CALCULATION-DATE TO WS-DATE-IN

                 PERFORM VALIDATE-CALENDAR-DATE

                 IF WS-DATE-VALID NOT = 'Y'

                    MOVE 'E006' TO ER-CODE

                    MOVE 'INVALID PREMIUM CALCULATION DATE'

                      TO ER-MESSAGE

                    PERFORM WRITE-ERROR

                 ELSE

                    IF PI-EXPIRY-DATE < PI-EFFECTIVE-DATE

                       MOVE 'E004' TO ER-CODE

                       MOVE 'EXPIRY DATE BEFORE EFFECTIVE DATE'

                         TO ER-MESSAGE

                       PERFORM WRITE-ERROR

                    ELSE

                       PERFORM CALCULATE-EARNED

                    END-IF

                 END-IF

              END-IF

           END-IF.
 
       VALIDATE-CALENDAR-DATE.

           MOVE 'N' TO WS-DATE-VALID

           IF WS-DATE-IN NUMERIC

              MOVE WS-DATE-IN(1:4) TO WS-YEAR

              MOVE WS-DATE-IN(5:2) TO WS-MONTH

              MOVE WS-DATE-IN(7:2) TO WS-DAY

              IF WS-YEAR > ZERO

                 AND WS-MONTH >= 1 AND WS-MONTH <= 12

                 PERFORM SET-MAX-DAY

                 IF WS-DAY >= 1 AND WS-DAY <= WS-MAX-DAY

                    MOVE 'Y' TO WS-DATE-VALID

                 END-IF

              END-IF

           END-IF.
 
       SET-MAX-DAY.

           EVALUATE WS-MONTH

             WHEN 1 WHEN 3 WHEN 5 WHEN 7 WHEN 8 WHEN 10 WHEN 12

               MOVE 31 TO WS-MAX-DAY

             WHEN 4 WHEN 6 WHEN 9 WHEN 11

               MOVE 30 TO WS-MAX-DAY

             WHEN 2

               PERFORM CHECK-LEAP-YEAR

               IF WS-LEAP = 'Y'

                  MOVE 29 TO WS-MAX-DAY

               ELSE

                  MOVE 28 TO WS-MAX-DAY

               END-IF

           END-EVALUATE.
 
       CHECK-LEAP-YEAR.

           MOVE 'N' TO WS-LEAP

           COMPUTE WS-REM4 = FUNCTION MOD(WS-YEAR, 4)

           COMPUTE WS-REM100 = FUNCTION MOD(WS-YEAR, 100)

           COMPUTE WS-REM400 = FUNCTION MOD(WS-YEAR, 400)

           IF WS-REM400 = ZERO

              MOVE 'Y' TO WS-LEAP

           ELSE

              IF WS-REM4 = ZERO AND WS-REM100 NOT = ZERO

                 MOVE 'Y' TO WS-LEAP

              END-IF

           END-IF.
 
       CALCULATE-EARNED.

      * INTEGER-OF-DATE IS CALLED ONLY AFTER ALL THREE DATES PASS

      * CALENDAR VALIDATION.

           COMPUTE WS-EFF-INT =

              FUNCTION INTEGER-OF-DATE(PI-EFFECTIVE-DATE)

           COMPUTE WS-EXP-INT =

              FUNCTION INTEGER-OF-DATE(PI-EXPIRY-DATE)

           COMPUTE WS-CALC-INT =

              FUNCTION INTEGER-OF-DATE(PRI-CALCULATION-DATE)

           COMPUTE WS-TERM-DAYS =

              WS-EXP-INT - WS-EFF-INT + 1

           IF WS-TERM-DAYS <= ZERO

              MOVE 'E005' TO ER-CODE

              MOVE 'POLICY TERM DAYS INVALID' TO ER-MESSAGE

              PERFORM WRITE-ERROR

           ELSE

              IF WS-CALC-INT < WS-EFF-INT

                 MOVE ZERO TO WS-EARNED-DAYS

              ELSE

                 IF WS-CALC-INT > WS-EXP-INT

                    MOVE WS-TERM-DAYS TO WS-EARNED-DAYS

                 ELSE

                    COMPUTE WS-EARNED-DAYS =

                      WS-CALC-INT - WS-EFF-INT + 1

                 END-IF

              END-IF

              COMPUTE WS-EARNED ROUNDED =

                PRI-WRITTEN-PREMIUM

                * WS-EARNED-DAYS / WS-TERM-DAYS

              IF WS-EARNED > PRI-WRITTEN-PREMIUM

                 MOVE PRI-WRITTEN-PREMIUM TO WS-EARNED

              END-IF

              COMPUTE WS-UNEARNED =

                PRI-WRITTEN-PREMIUM - WS-EARNED

              IF WS-UNEARNED < ZERO

                 MOVE ZERO TO WS-UNEARNED

              END-IF

              PERFORM WRITE-RESULT

           END-IF.
 
       WRITE-RESULT.

           MOVE PRI-PREMIUM-ID TO PRO-PREMIUM-ID

           MOVE PRI-POLICY-NO TO PRO-POLICY-NO

           MOVE PRI-WRITTEN-PREMIUM TO PRO-WRITTEN-PREMIUM

           MOVE WS-EARNED TO PRO-EARNED-PREMIUM

           MOVE WS-UNEARNED TO PRO-UNEARNED-PREMIUM

           MOVE PRI-CALCULATION-DATE TO PRO-CALCULATION-DATE

           WRITE PRO-REC

           IF WS-PO-ST = '00'

              ADD 1 TO WS-CALCULATED

           ELSE

              DISPLAY 'PREMIUM OUTPUT WRITE ERROR ' WS-PO-ST

              ADD 1 TO WS-IO-ERRORS

              SET FATAL-ERROR TO TRUE

           END-IF.
 
       WRITE-ERROR.

           MOVE PRI-POLICY-NO TO ER-POLICY-NO

           WRITE ER-REC

           IF WS-ER-ST = '00'

              ADD 1 TO WS-ERRORS

           ELSE

              DISPLAY 'ERROR OUTPUT WRITE ERROR ' WS-ER-ST

              ADD 1 TO WS-IO-ERRORS

              SET FATAL-ERROR TO TRUE

           END-IF.
 
       CLOSE-FILES.

           CLOSE POLICY-IN PREMIUM-IN PREMIUM-OUT ERROR-OUT.

 