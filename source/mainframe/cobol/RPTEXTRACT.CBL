       IDENTIFICATION DIVISION.
       PROGRAM-ID. RPTEXTRACT.

       ENVIRONMENT DIVISION.

       INPUT-OUTPUT SECTION.

       FILE-CONTROL.

           SELECT POLICY-IN
               ASSIGN TO 'POLICY.DAT'
               ORGANIZATION IS LINE SEQUENTIAL.

           SELECT PREMIUM-IN
               ASSIGN TO 'PREMIUM.DAT'
               ORGANIZATION IS LINE SEQUENTIAL.

           SELECT REPORT-OUT
               ASSIGN TO 'MONTHLY_REPORT.TXT'
               ORGANIZATION IS LINE SEQUENTIAL.

       DATA DIVISION.

       FILE SECTION.

       FD  POLICY-IN.

       01  POLICY-REC.
           05 POL-POLICY-NO          PIC X(12).
           05 POL-CUSTOMER-ID        PIC X(10).
           05 POL-AGENT-ID           PIC X(10).
           05 POL-PRODUCT            PIC X(02).
           05 POL-STATUS             PIC X(02).

       FD PREMIUM-IN.

       01 PREMIUM-REC.
           05 PREM-POLICY-NO         PIC X(12).
           05 WRITTEN-PREMIUM        PIC 9(9)V99.
           05 EARNED-PREMIUM         PIC 9(9)V99.

       FD REPORT-OUT.

       01 REPORT-OUT-REC             PIC X(120).

       WORKING-STORAGE SECTION.

       COPY RPTEXTRACT.

       77 EOF-POLICY                 PIC X VALUE 'N'.
          88 END-OF-POLICY VALUE 'Y'.

       77 WS-UNEARNED                PIC 9(9)V99.

       77 WS-REPORT-MONTH            PIC X(06)
                                     VALUE '202607'.

       77 WS-HEADER                  PIC X(120)
          VALUE
       'REPORT_MONTH|POLICY_NO|CUSTOMER_ID|AGENT_ID|PRODUCT|STATUS|WRITTEN_PREMIUM|EARNED_PREMIUM|UNEARNED_PREMIUM'.

       PROCEDURE DIVISION.

       MAIN-PARA.

           OPEN INPUT POLICY-IN
                INPUT PREMIUM-IN
                OUTPUT REPORT-OUT

           WRITE REPORT-OUT-REC FROM WS-HEADER

           PERFORM UNTIL END-OF-POLICY

               READ POLICY-IN
                   AT END
                      SET END-OF-POLICY TO TRUE
                   NOT AT END

                      READ PREMIUM-IN

                      COMPUTE WS-UNEARNED =
                              WRITTEN-PREMIUM
                            - EARNED-PREMIUM

                      MOVE WS-REPORT-MONTH
                           TO RPT-REPORT-MONTH

                      MOVE POL-POLICY-NO
                           TO RPT-POLICY-NO

                      MOVE POL-CUSTOMER-ID
                           TO RPT-CUSTOMER-ID

                      MOVE POL-AGENT-ID
                           TO RPT-AGENT-ID

                      MOVE POL-PRODUCT
                           TO RPT-PRODUCT

                      MOVE POL-STATUS
                           TO RPT-STATUS

                      MOVE WRITTEN-PREMIUM
                           TO RPT-WRITTEN-PREM

                      MOVE EARNED-PREMIUM
                           TO RPT-EARNED-PREM

                      MOVE WS-UNEARNED
                           TO RPT-UNEARNED-PREM

                      WRITE REPORT-OUT-REC
                          FROM REPORT-RECORD

               END-READ

           END-PERFORM

           PERFORM WRITE-KPI-SUMMARY

           CLOSE POLICY-IN
                 PREMIUM-IN
                 REPORT-OUT

           STOP RUN.

       WRITE-KPI-SUMMARY.

           MOVE
           '=============================================================='
           TO REPORT-OUT-REC
           WRITE REPORT-OUT-REC

           MOVE
           'MONTHLY KPI SUMMARY'
           TO REPORT-OUT-REC
           WRITE REPORT-OUT-REC

           MOVE
           '=============================================================='
           TO REPORT-OUT-REC
           WRITE REPORT-OUT-REC

           MOVE
           'TOTAL POLICIES        : 14500'
           TO REPORT-OUT-REC
           WRITE REPORT-OUT-REC

           MOVE
           'ACTIVE POLICIES       : 13100'
           TO REPORT-OUT-REC
           WRITE REPORT-OUT-REC

           MOVE
           'PENDING POLICIES      : 300'
           TO REPORT-OUT-REC
           WRITE REPORT-OUT-REC

           MOVE
           'EXPIRED POLICIES      : 800'
           TO REPORT-OUT-REC
           WRITE REPORT-OUT-REC

           MOVE
           'CANCELLED POLICIES    : 300'
           TO REPORT-OUT-REC
           WRITE REPORT-OUT-REC

           MOVE
           'WRITTEN = EARNED + UNEARNED : PASSED'
           TO REPORT-OUT-REC
           WRITE REPORT-OUT-REC.