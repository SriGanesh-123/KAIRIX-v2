IDENTIFICATION DIVISION.
       PROGRAM-ID. POLSTAT.
      ******************************************************************
      * TASK 8 - POLICY STATUS LOGIC
      *
      * DEPENDENCY: TASK 5 POLLOAD PROVIDES VALID POLICY MASTER DATA.
      * TASKS 6/7 MAY RUN BEFORE/AFTER ACCORDING TO THE JOB SCHEDULE.
      *
      * PROJECT STATUS CODES:
      * PN = PENDING/FUTURE
      * AC = ACTIVE/IN-FORCE
      * EX = EXPIRED
      * CN = CANCELLED (PRESERVED; NOT DERIVED)
      *
      * RULE:
      * IF EXISTING STATUS = CN, PRESERVE CN.
      * ELSE CURRENT-DATE < EFFECTIVE-DATE => PN
      * ELSE CURRENT-DATE <= EXPIRY-DATE  => AC
      * ELSE                               => EX
      *
      * CANCELLATION IS NOT DERIVED BECAUSE NO CANCELLATION DATE/RULE
      * EXISTS IN THE CURRENT TASK-2/3 POLICY LAYOUT.
      ******************************************************************
       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT POLICY-IN ASSIGN TO POLIN
             ORGANIZATION IS SEQUENTIAL FILE STATUS IS WS-PI-ST.
           SELECT POLICY-OUT ASSIGN TO POLOUT
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
 
       FD POLICY-OUT RECORD CONTAINS 77 CHARACTERS.
       01 PO-REC.
          05 PO-POLICY-NO       PIC X(12).
          05 PO-CUSTOMER-ID     PIC X(9).
          05 PO-AGENT-ID        PIC X(9).
          05 PO-PRODUCT-TYPE    PIC X(2).
          05 PO-POLICY-STATUS   PIC X(2).
          05 PO-EFFECTIVE-DATE  PIC 9(8).
          05 PO-EXPIRY-DATE     PIC 9(8).
          05 PO-WRITTEN-PREMIUM PIC 9(9)V99.
          05 PO-CREATE-DT       PIC 9(8).
          05 PO-UPDATE-DT       PIC 9(8).
 
       FD ERROR-OUT RECORD CONTAINS 70 CHARACTERS.
       01 ER-REC.
          05 ER-POLICY-NO PIC X(12).
          05 ER-CODE PIC X(4).
          05 ER-MESSAGE PIC X(54).
 
       WORKING-STORAGE SECTION.
       01 WS-STATUS.
          05 WS-PI-ST PIC XX VALUE SPACES.
          05 WS-PO-ST PIC XX VALUE SPACES.
          05 WS-ER-ST PIC XX VALUE SPACES.
       01 WS-SW.
          05 WS-EOF PIC X VALUE 'N'.
             88 END-OF-FILE VALUE 'Y'.
          05 WS-FATAL PIC X VALUE 'N'.
             88 FATAL-ERROR VALUE 'Y'.
          05 WS-DATE-VALID PIC X VALUE 'N'.
          05 WS-PI-OPEN PIC X VALUE 'N'.
          05 WS-PO-OPEN PIC X VALUE 'N'.
          05 WS-ER-OPEN PIC X VALUE 'N'.
       01 WS-DATE.
          05 WS-CURRENT-DATE PIC 9(8).
          05 WS-DATE-IN PIC 9(8).
          05 WS-YEAR PIC 9(4).
          05 WS-MONTH PIC 99.
          05 WS-DAY PIC 99.
          05 WS-MAX-DAY PIC 99.
          05 WS-LEAP PIC X.
          05 WS-REM4 PIC 9(4).
          05 WS-REM100 PIC 9(4).
          05 WS-REM400 PIC 9(4).
       01 WS-COUNTERS.
          05 WS-READ PIC 9(9) VALUE ZERO.
          05 WS-WRITTEN PIC 9(9) VALUE ZERO.
          05 WS-CHANGED PIC 9(9) VALUE ZERO.
          05 WS-PENDING PIC 9(9) VALUE ZERO.
          05 WS-ACTIVE PIC 9(9) VALUE ZERO.
          05 WS-EXPIRED PIC 9(9) VALUE ZERO.
          05 WS-CANCELLED PIC 9(9) VALUE ZERO.
          05 WS-REJECTED PIC 9(9) VALUE ZERO.
          05 WS-IO-ERRORS PIC 9(9) VALUE ZERO.
 
       PROCEDURE DIVISION.
       MAIN.
           MOVE FUNCTION CURRENT-DATE(1:8) TO WS-CURRENT-DATE
           MOVE WS-CURRENT-DATE TO WS-DATE-IN
           PERFORM VALIDATE-CALENDAR-DATE
           IF WS-DATE-VALID NOT = 'Y'
              DISPLAY 'INVALID SYSTEM CURRENT DATE ' WS-CURRENT-DATE
              MOVE 12 TO RETURN-CODE
              GOBACK
           END-IF
           OPEN INPUT POLICY-IN
           IF WS-PI-ST = '00'
              MOVE 'Y' TO WS-PI-OPEN
           ELSE
              DISPLAY 'POLICY INPUT OPEN ERROR ' WS-PI-ST
              SET FATAL-ERROR TO TRUE
           END-IF
 
           OPEN OUTPUT POLICY-OUT
           IF WS-PO-ST = '00'
              MOVE 'Y' TO WS-PO-OPEN
           ELSE
              DISPLAY 'POLICY OUTPUT OPEN ERROR ' WS-PO-ST
              SET FATAL-ERROR TO TRUE
           END-IF
 
           OPEN OUTPUT ERROR-OUT
           IF WS-ER-ST = '00'
              MOVE 'Y' TO WS-ER-OPEN
           ELSE
              DISPLAY 'ERROR OUTPUT OPEN ERROR ' WS-ER-ST
              SET FATAL-ERROR TO TRUE
           END-IF
 
           IF FATAL-ERROR
              PERFORM CLOSE-FILES
              MOVE 12 TO RETURN-CODE
              GOBACK
           END-IF
 
           PERFORM UNTIL END-OF-FILE OR FATAL-ERROR
              READ POLICY-IN
                 AT END MOVE 'Y' TO WS-EOF
                 NOT AT END
                    IF WS-PI-ST NOT = '00'
                       DISPLAY 'POLICY READ ERROR ' WS-PI-ST
                       ADD 1 TO WS-IO-ERRORS
                       SET FATAL-ERROR TO TRUE
                    ELSE
                       ADD 1 TO WS-READ
                       PERFORM PROCESS-POLICY
                    END-IF
              END-READ
           END-PERFORM
 
           PERFORM CLOSE-FILES
           DISPLAY 'POLSTAT READ      : ' WS-READ
           DISPLAY 'POLSTAT WRITTEN   : ' WS-WRITTEN
           DISPLAY 'POLSTAT CHANGED   : ' WS-CHANGED
           DISPLAY 'POLSTAT PENDING   : ' WS-PENDING
           DISPLAY 'POLSTAT ACTIVE    : ' WS-ACTIVE
           DISPLAY 'POLSTAT EXPIRED   : ' WS-EXPIRED
           DISPLAY 'POLSTAT CANCELLED : ' WS-CANCELLED
           DISPLAY 'POLSTAT REJECTED  : ' WS-REJECTED
           DISPLAY 'POLSTAT I/O ERRORS: ' WS-IO-ERRORS
           IF FATAL-ERROR MOVE 12 TO RETURN-CODE END-IF
           GOBACK.
 
       PROCESS-POLICY.
           MOVE PI-EFFECTIVE-DATE TO WS-DATE-IN
           PERFORM VALIDATE-CALENDAR-DATE
           IF WS-DATE-VALID NOT = 'Y'
              MOVE 'S001' TO ER-CODE
              MOVE 'INVALID POLICY EFFECTIVE DATE' TO ER-MESSAGE
              PERFORM WRITE-ERROR
           ELSE
              MOVE PI-EXPIRY-DATE TO WS-DATE-IN
              PERFORM VALIDATE-CALENDAR-DATE
              IF WS-DATE-VALID NOT = 'Y'
                 MOVE 'S002' TO ER-CODE
                 MOVE 'INVALID POLICY EXPIRY DATE' TO ER-MESSAGE
                 PERFORM WRITE-ERROR
              ELSE
                 IF PI-EXPIRY-DATE < PI-EFFECTIVE-DATE
                    MOVE 'S003' TO ER-CODE
                    MOVE 'EXPIRY DATE BEFORE EFFECTIVE DATE'
                      TO ER-MESSAGE
                    PERFORM WRITE-ERROR
                 ELSE
                    PERFORM DETERMINE-STATUS
                    PERFORM WRITE-POLICY
                 END-IF
              END-IF
           END-IF.
 
       DETERMINE-STATUS.
           MOVE PI-REC TO PO-REC
           IF PI-POLICY-STATUS = 'CN'
              MOVE 'CN' TO PO-POLICY-STATUS
              ADD 1 TO WS-CANCELLED
           ELSE
              IF WS-CURRENT-DATE < PI-EFFECTIVE-DATE
                 MOVE 'PN' TO PO-POLICY-STATUS
                 ADD 1 TO WS-PENDING
              ELSE
                 IF WS-CURRENT-DATE <= PI-EXPIRY-DATE
                    MOVE 'AC' TO PO-POLICY-STATUS
                    ADD 1 TO WS-ACTIVE
                 ELSE
                    MOVE 'EX' TO PO-POLICY-STATUS
                    ADD 1 TO WS-EXPIRED
                 END-IF
              END-IF
           END-IF
           IF PO-POLICY-STATUS NOT = PI-POLICY-STATUS
              ADD 1 TO WS-CHANGED
              MOVE WS-CURRENT-DATE TO PO-UPDATE-DT
           END-IF.
 
       WRITE-POLICY.
           WRITE PO-REC
           IF WS-PO-ST = '00'
              ADD 1 TO WS-WRITTEN
           ELSE
              DISPLAY 'POLICY OUTPUT WRITE ERROR ' WS-PO-ST
              ADD 1 TO WS-IO-ERRORS
              SET FATAL-ERROR TO TRUE
           END-IF.
 
       WRITE-ERROR.
           MOVE PI-POLICY-NO TO ER-POLICY-NO
           WRITE ER-REC
           IF WS-ER-ST = '00'
              ADD 1 TO WS-REJECTED
           ELSE
              DISPLAY 'ERROR OUTPUT WRITE ERROR ' WS-ER-ST
              ADD 1 TO WS-IO-ERRORS
              SET FATAL-ERROR TO TRUE
           END-IF.
 
       CLOSE-FILES.
           IF WS-PI-OPEN = 'Y'
              CLOSE POLICY-IN
              IF WS-PI-ST NOT = '00'
                 DISPLAY 'POLICY INPUT CLOSE ERROR ' WS-PI-ST
                 ADD 1 TO WS-IO-ERRORS
                 SET FATAL-ERROR TO TRUE
              ELSE
                 MOVE 'N' TO WS-PI-OPEN
              END-IF
           END-IF
 
           IF WS-PO-OPEN = 'Y'
              CLOSE POLICY-OUT
              IF WS-PO-ST NOT = '00'
                 DISPLAY 'POLICY OUTPUT CLOSE ERROR ' WS-PO-ST
                 ADD 1 TO WS-IO-ERRORS
                 SET FATAL-ERROR TO TRUE
              ELSE
                 MOVE 'N' TO WS-PO-OPEN
              END-IF
           END-IF
 
           IF WS-ER-OPEN = 'Y'
              CLOSE ERROR-OUT
              IF WS-ER-ST NOT = '00'
                 DISPLAY 'ERROR OUTPUT CLOSE ERROR ' WS-ER-ST
                 ADD 1 TO WS-IO-ERRORS
                 SET FATAL-ERROR TO TRUE
              ELSE
                 MOVE 'N' TO WS-ER-OPEN
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