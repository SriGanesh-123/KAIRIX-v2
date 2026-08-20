       *****************************************************************
       * PROGRAM NAME : POLLOAD
       * PURPOSE      : Load Policy Master Records into VSAM KSDS
       * SYSTEM       : TFG Mainframe Personal Lines
       * AUTHOR       : Data Engineering Project
       *****************************************************************

       IDENTIFICATION DIVISION.
       PROGRAM-ID. POLLOAD.

       ENVIRONMENT DIVISION.

       INPUT-OUTPUT SECTION.

       FILE-CONTROL.

           SELECT POLICY-IN
               ASSIGN TO POLIN
               ORGANIZATION IS LINE SEQUENTIAL
               FILE STATUS IS WS-IN-STATUS.

           SELECT POLICY-MASTER
               ASSIGN TO POLYMAST
               ORGANIZATION IS INDEXED
               ACCESS MODE IS DYNAMIC
               RECORD KEY IS POLICY-NUMBER
               FILE STATUS IS WS-VSAM-STATUS.

       DATA DIVISION.

       FILE SECTION.

       FD  POLICY-IN.
       01  POLICY-IN-REC.
           05 PI-POLICY-NUMBER       PIC X(15).
           05 PI-CUSTOMER-ID         PIC X(10).
           05 PI-AGENT-ID            PIC X(10).
           05 PI-PRODUCT-CODE        PIC X(10).
           05 PI-POLICY-TYPE         PIC X(30).
           05 PI-EFFECTIVE-DATE      PIC X(10).
           05 PI-EXPIRATION-DATE     PIC X(10).
           05 PI-CURRENT-STATUS      PIC X(20).
           05 PI-PAYMENT-FREQUENCY   PIC X(20).
           05 PI-POLICY-TERM         PIC 9(02).
           05 PI-WRITTEN-PREMIUM     PIC 9(10)V99.
           05 PI-EARNED-PREMIUM      PIC 9(10)V99.
           05 PI-RENEWAL-DATE        PIC X(10).

       FD  POLICY-MASTER.

       COPY POLYMAST.

       WORKING-STORAGE SECTION.

       77  WS-EOF                    PIC X VALUE 'N'.

       77  WS-IN-STATUS              PIC XX VALUE SPACES.
       77  WS-VSAM-STATUS            PIC XX VALUE SPACES.

       77  WS-READ-COUNT             PIC 9(7) VALUE ZERO.
       77  WS-WRITE-COUNT            PIC 9(7) VALUE ZERO.
       77  WS-ERROR-COUNT            PIC 9(7) VALUE ZERO.

       PROCEDURE DIVISION.

       MAIN-PROCESS.

           PERFORM 1000-INITIALIZE

           PERFORM UNTIL WS-EOF = 'Y'

               PERFORM 2000-READ-INPUT

               IF WS-EOF NOT = 'Y'
                   PERFORM 3000-VALIDATE
                   PERFORM 4000-WRITE-VSAM
               END-IF

           END-PERFORM

           PERFORM 9000-CLOSE-FILES

           STOP RUN.

      *============================================================*
      * INITIALIZATION
      *============================================================*

       1000-INITIALIZE.

           DISPLAY 'POLLOAD STARTED'.

           OPEN INPUT POLICY-IN

           IF WS-IN-STATUS NOT = "00"
               DISPLAY 'ERROR OPENING INPUT FILE'
               DISPLAY 'STATUS = ' WS-IN-STATUS
               STOP RUN
           END-IF

           OPEN OUTPUT POLICY-MASTER

           IF WS-VSAM-STATUS NOT = "00"
               DISPLAY 'ERROR OPENING VSAM FILE'
               DISPLAY 'STATUS = ' WS-VSAM-STATUS
               STOP RUN
           END-IF.

      *============================================================*
      * READ INPUT
      *============================================================*

       2000-READ-INPUT.

           READ POLICY-IN

               AT END
                   MOVE 'Y' TO WS-EOF

               NOT AT END
                   ADD 1 TO WS-READ-COUNT

           END-READ.

      *============================================================*
      * VALIDATION
      *============================================================*

       3000-VALIDATE.

           IF PI-POLICY-NUMBER = SPACES

               DISPLAY 'INVALID POLICY NUMBER'

               ADD 1 TO WS-ERROR-COUNT

               GO TO 3000-EXIT

           END-IF.

      * Move Input Record to VSAM Record

           MOVE PI-POLICY-NUMBER      TO POLICY-NUMBER
           MOVE PI-CUSTOMER-ID        TO CUSTOMER-ID
           MOVE PI-AGENT-ID           TO AGENT-ID
           MOVE PI-PRODUCT-CODE       TO PRODUCT-CODE
           MOVE PI-POLICY-TYPE        TO POLICY-TYPE
           MOVE PI-EFFECTIVE-DATE     TO EFFECTIVE-DATE
           MOVE PI-EXPIRATION-DATE    TO EXPIRATION-DATE
           MOVE PI-CURRENT-STATUS     TO CURRENT-STATUS
           MOVE PI-PAYMENT-FREQUENCY  TO PAYMENT-FREQUENCY
           MOVE PI-POLICY-TERM        TO POLICY-TERM
           MOVE PI-WRITTEN-PREMIUM    TO WRITTEN-PREMIUM
           MOVE PI-EARNED-PREMIUM     TO EARNED-PREMIUM
           MOVE PI-RENEWAL-DATE       TO RENEWAL-DATE.

       3000-EXIT.
           EXIT.

      *============================================================*
      * WRITE VSAM RECORD
      *============================================================*

       4000-WRITE-VSAM.

           WRITE POLICY-MASTER-RECORD

           INVALID KEY

               DISPLAY 'DUPLICATE POLICY : '
                       POLICY-NUMBER

               ADD 1 TO WS-ERROR-COUNT

           NOT INVALID KEY

               ADD 1 TO WS-WRITE-COUNT

           END-WRITE.

      *============================================================*
      * CLOSE FILES
      *============================================================*

       9000-CLOSE-FILES.

           CLOSE POLICY-IN.

           CLOSE POLICY-MASTER.

           DISPLAY '-------------------------------------'.

           DISPLAY 'TOTAL RECORDS READ    : '
                    WS-READ-COUNT.

           DISPLAY 'TOTAL RECORDS WRITTEN : '
                    WS-WRITE-COUNT.

           DISPLAY 'TOTAL ERRORS          : '
                    WS-ERROR-COUNT.

           DISPLAY 'POLLOAD COMPLETED'.

           DISPLAY '-------------------------------------'.

       END PROGRAM POLLOAD.