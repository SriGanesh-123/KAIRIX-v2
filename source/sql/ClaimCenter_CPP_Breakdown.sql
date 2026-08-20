-- *****************************************************************************************
--
-- With filter (primarily YTD) & data returned modifications this can be also used for P&L 
-- incurred losses using the detail calculation.  It will also require a join to PC to get 
-- profit center and uses the TFG loss transaction codes as a filter.
--
-- *****************************************************************************************
-- ************************************************************************************
-- Server: PBENGWCSQL01    Converted to Cloud Claim Center views.
--  Must Join to Policy Center to get accurate policy underwriting company
-- ************************************************************************************


 -- Not used
declare @PV_STARTDATE datetime = '2026-6-30 00:00:00'
declare @PV_ENDDATE datetime = '2026-08-1 00:00:00'


select   --*
distinct 
PolSource,
case 
	when LOBCode = 'Business Owners Line' then 'BP7Line'
	when LOBCode like 'Workers%' then 'Workers Comp Line'
	else LOBCode
end as LOBCode
--,ClaimNumber
--,LossDate
--,ReportedDate
--,Count(0) as RecCount
,sum(TransAmount) as IncurredAmount
,PolicyNumber
from
(
Select 
	--rownum,
	PolSource,
	PolicyPrefix_Ext,
	LOBCode,
	 
	ClaimNumber,
	PolicyType,
	PolicyType2,
	ClaimRep1,
	ClaimRep2,
	ClaimState,
	PolicyState,
	PolicyNumber,
	--right('000' + cast(PolicyDec as varchar(2)),3)  as PolicyDec,
	PolicyDec,
	Producer,
	Company,
	PolOrgEffDate,
	PolEffDate,
	PolExpDate,
	ReportedDate,
	LossDate,
	CauseOfLoss,
	Costtype,
	TranCode,
	RecoveryCat,
	case
		when TFGTran = '431' AND CostType = 'Indemnity' AND rownum = 1 then '421'
		when TFGTran = '431' AND CostType = 'Indemnity' AND rownum <> 1 then '431'
		when TFGTran = '431' AND CostType <> 'Indemnity' AND rownum = 1 then '422'
		when TFGTran = '431' AND CostType <> 'Indemnity' AND rownum <> 1 then '432'
	else TFGTran end as TFGTran,
	AcctDate_sql,
	AcctDate, 
	right('000' + cast(ClmtNumber as varchar(3)),3) as ClmtNumber,
	right('00000000' + isnull(ltrim(Class),'0'),8) as Class,
		
	--FinancialAmount,
	CoveragePatternCode,
	
	CovSubType, 
	CheckNumber,
	IssueDate,
	DoesNotErodeReserves,
	ReinCo,
	ReinsAmt,
	Amount,
	TransAmount

from
(
SELECT 
	case
		when PolicyPrefix_Ext is null then 'Legacy'
			else 'Guidewire'
			end as PolSource,

	PolicyPrefix_Ext,
	case 
		when tt.TYPECODE = 'Reserve' then
			row_number() over(partition by ClaimNumber, ex.id, tt.typecode, CST.NAME
							order by tl.CreateTime)
		else 0 
		end											as rownum,
	cast(cl.ClaimNumber					as char(13)) as ClaimNumber
	,cast(PolicyPrefix_Ext				as char(3)) as PolicyType
	,lob.name						as LOBCode
	,PolicyTypePrefix_Ext as PolicyType2
	,cast(left(ProducerCode,2)	as char(2)) as ClaimState
	,cast(left(ProducerCode,2)	as char(2)) as PolicyState

	,case 
		when left(ProducerCode,2) = '13' then left(isnull(u1.InRepID_ext,'00000'),5)
		else left(isnull(u1.OhRepID_ext,'00000'),5)
		end											as ClaimRep1 

	,case
		when SubroRepresentative_Ext is null then '00000'
		else isnull(left(u2.SubroRepId_Ext,5),'00000') 
		end											as ClaimRep2
			
	,cast((po.Policynumber)	as char(10))				as PolicyNumber
	,po.PolicyDecNo_Ext  as PolicyDec
  
	,case 
			when uw.name = 'Lightning Rod Mutual Insurance Company'	 then 'LRM'
			when uw.name = 'Western Reserve Mutual Casualty Company' then 'WRM'
			when uw.name = 'Sonnenberg Mutual Insurance Company'	 then 'SON'
			else 'UNK'
		end																			 as Company
	,CAST(replace(convert(char(10), po.OrigEffectiveDate, 101), '/', '') AS CHAR(8)) as PolOrgEffDate
	,CAST(replace(convert(char(10), po.EffectiveDate, 101), '/', '')	 AS CHAR(8)) as PolEffDate
	,CAST(replace(convert(char(10), po.ExpirationDate, 101), '/', '')	 AS CHAR(8)) as PolExpDate
	,cl.ReportedDate
	,cl.Lossdate
	,upper(cast(left(tlc.TYPECODE,45)									 AS CHAR(45))) as CauseOfLoss
	
	----
	,cv.CicsClaimCov_Ext as TFGCov

	,case
		when ct.typecode in ('CPEquipBrkCov')					then '270'
		when ct.typecode in ('CPINCCCov')						then '010'
		when cv.CicsClaimCov_Ext in ('615','616','617','618')	then '010'
		else '021' end as TFGASL

	,case
		when ct.typecode in ('CPEquipBrkCov')					then '270'
		when ct.typecode in ('CPINCCCov')						then '010'
		when tlc.TYPECODE in ('fire','fire-wood_coal-stove','ightning','vandalism',
							  'explosion','sprinkler','sprinkler_leakage')	then '010'
		else '021' end as GWASL
     --------
	
	,tl.CreateTime as TLICreate
	,isnull(tset.ApprovalDate,'01/01/2000') as ApprovalDate
	,ScheduledSendDate 
	
	,case 
		when tl.CreateTime >= isnull(tset.ApprovalDate,'01/01/2000') then cast(tl.CreateTime as date)
		else cast(tset.approvaldate as date)
		end																	as AcctDate_sql
	
	,CAST(replace(convert(char(10)
	
	,case 
		when tl.CreateTime >= isnull(tset.ApprovalDate,'01/01/2000') then tl.CreateTime 
		else tset.approvaldate end, 101), '/', '')	 AS CHAR(8))					as AcctDate
	
	,cast(left(ProducerCode,9) 											 AS CHAR(9)) as Producer
	,cast((isnull(CicsClaimantNum_Ext,0))	as numeric(3))							as ClmtNumber
	,cast(cls.Code as char(8))								as Class
	
	,DoesNotErodeReserves
	
	,CicsUnitLocNum_Ext
	,CicsClassCode_Ext
	,cv.CicsClaimCov_Ext		as CovCicsClaimCov
	,ex.CicsClaimCov_Ext		as ExpCicsClaimCov
	
	,case 
	when tt.TYPECODE = 'Reserve' AND cst.NAME = 'Indemnity' then '431'
	when tt.TYPECODE = 'Reserve' AND cst.NAME <> 'Indemnity' then '432'
	when tt.TYPECODE = 'Payment' AND cst.NAME = 'Indemnity' AND DoesNotErodeReserves = 1 then '321'
	when tt.TYPECODE = 'Payment' AND cst.NAME = 'Indemnity' AND DoesNotErodeReserves <> 1 then '331'
	when tt.TYPECODE = 'Payment' AND cst.NAME <> 'Indemnity' AND DoesNotErodeReserves = 1 then '322'
	when tt.TYPECODE = 'Payment' AND cst.NAME <> 'Indemnity' AND DoesNotErodeReserves <> 1 then '332'
	when tt.TYPECODE = 'Recovery' AND RV.TypeCode = 'Credit_loss' AND cst.NAME = 'Indemnity' then '321'
	when tt.TYPECODE = 'Recovery' AND rv.TYPECODE = 'Credit_loss' AND cst.NAME <> 'Indemnity' then '322'
	when tt.TYPECODE = 'Recovery' AND cst.NAME = 'EXPENSE - OTHERS' then '322'
	when tt.TYPECODE = 'Recovery' AND rv.TYPECODE = 'credit_exp' then '322'
	when tt.TYPECODE = 'Recovery' AND rv.TYPECODE = 'deductible' then '321'
	when tt.TYPECODE = 'Recovery' AND rv.TYPECODE = 'salvage' AND cst.NAME = 'Indemnity' then '341'
	when tt.TYPECODE = 'Recovery' AND rv.TYPECODE = 'salvage' AND cst.NAME <> 'Indemnity' then '342'
	when tt.TYPECODE = 'Recovery' AND rv.TYPECODE = 'subro' AND cst.NAME = 'Indemnity' then '351'
	when tt.TYPECODE = 'Recovery' AND rv.TYPECODE = 'subro' AND cst.NAME <> 'Indemnity' then '353'
	else 'XXX'
	end as TFGTran
		
		,rv.typecode as RecoveryCat
	,upper(cast(ct.typecode as char(64)))									 as CoveragePatternCode
	--,upper(cast(ex.CoverageSubType as char(50)))							 as ExCovSubType
	
	,ct.typecode			 
	--,ex.CoverageSubType														 as exCoverageSubType												  
	
	,upper(cast(st.typecode as char(50)))									 as CovSubType
	,tt.TYPECODE															 as TranCode
	,upper(cast(CST.NAME as char(25)))										 as CostType
	--,upper(isnull(cast(ccat.TYPECODE as char(25)),''))						 as CostCategory
	--,isnull(ccat.NAME, '')	as CostCategory
	--,ISNULL(lc.Name, '')	as LineCategory
	
	,case
		when CST.NAME = 'Indemnity'							       then '                                             '
		when ccat.TYPECODE in ('legalexpense_ext','appraisal_ext') then upper(cast(ccat.TYPECODE as char(45)))
		
		-- these are retired
		when lc.TYPECODE in ('deductible','formerdeductible')      then upper(cast(ccat.TYPECODE as char(45)))
		when lc.TYPECODE is not null						       then upper(cast(lc.TYPECODE as char(45)))
		-- not in prod costcat table
		when lc.TYPECODE is null and ccat.TYPECODE = 'autoparts'   then 'OTHER                                        '
		else upper(cast(ccat.TYPECODE as char(45)))
		end											as ExpCode
	
	,ISNULL(cast(CheckNumber as char(9)),'')		as CheckNumber
	,ISNULL(CAST(replace(convert(char(10), ck.IssueDate, 101), '/', '') AS CHAR(8)),'') as IssueDate 
	,'  '											as ReinCo
	-- these not needed for loss stats
	--,tls.name										as TranLifeStatus
	--,ts.TYPECODE									as TransStatus

	--,tl.TransactionAmount as TrxAmt
	,'000000000.00'									as ReinsAmt
	
	
	, case 
		when tt.TYPECODE = 'Payment' then
			case
				when DoesNotErodeReserves = 0 then isnull(tl.TransactionAmount,0.00) * -1
				else tl.TransactionAmount
			end
		when tt.TYPECODE = 'Recovery' then isnull(tl.TransactionAmount,0.00) * -1
		else isnull(tl.TransactionAmount,0.00)

		end							as TransAmount
	
	
	--,tl.TransactionAmount
	
	
	,CASE 
		when tt.TYPECODE = 'Recovery'	then
			case
				WHEN isnull(tl.TransactionAmount,0.00) > 0 	THEN 
					CONCAT('-', RIGHT(CAST((-100000000 + isnull(-1 * tl.TransactionAmount,0.00)) AS numeric(11,2)),11)) 
				ELSE 
					RIGHT(CONCAT('00000000', CAST(isnull(-1 * tl.TransactionAmount,0.00) AS numeric(11,2))),12) 
			END  
		else
			case
				WHEN isnull(tl.TransactionAmount,0.00) < 0 	THEN 
					CONCAT('-', RIGHT(CAST((-100000000 + isnull(tl.TransactionAmount,0.00)) AS numeric(11,2)),11)) 
				ELSE 
					RIGHT(CONCAT('00000000', CAST(isnull(tl.TransactionAmount,0.00) AS numeric(11,2))),12) 
			END  
		end
			as Amount 						
	,tl.id						as TransLineItemID
	,t.id						as TransactionID
	--  **********************************************************************************************
		,cv.PolicySystemId					as CovPolSystemID  
		
		,case 
			when upper(cast(ct.typecode as char(50))) in ('BP7EmploymentPracticesLiabilityInsurance','BP7SupplementalExtendReportingPeriodEPLI') then
				case 
					when cv.Deductible > 99999 then '99999     '	-- Deductible is S9(5) on TFG stats
					else cast(isnull(cv.Deductible, '          ')	as char(10))  
				end
			--else cast(isnull(stat.DedStatAmount, '          ') as char(10)) 
			else '          '
			end as DedStatAmount
	
		--closed and reopen fields added 09/21/2018 ek
		
		,CAST(replace(convert(char(10), cl.CloseDate, 101), '/', '') AS CHAR(8)) as Claim_CloseDate
		,CAST(replace(convert(char(10), cl.ReOpenDate, 101), '/', '') AS CHAR(8)) as Claim_ReOpenDate
		
												

FROM vw_curr_cc_transactionlineitem tl
	left join vw_curr_cc_transaction t					(nolock) on tl.TransactionID	= t.id
	left join vw_curr_cc_transactionset tset			(nolock) on t.TransactionSetID	= tset.id
	left join vw_curr_cc_claim cl						(nolock) on t.ClaimID			= cl.id
	left join vw_curr_cc_policy po						(nolock) on cl.PolicyID			= po.id
	left join vw_curr_cc_check ck						(nolock) on t.CheckID			= ck.id
	left join vw_curr_cc_reserveline rl					(nolock) on t.ReserveLineID		= rl.id
	left join vw_curr_cc_exposure ex					(nolock) on t.ExposureID		= ex.id
	left join vw_curr_cc_coverage cv					(nolock) on ex.CoverageID		= cv.id
	left join vw_curr_cc_contact clmcont				(nolock) on ex.ClaimantDenormID = clmcont.id
	
	left join vw_curr_cc_user u1						(nolock) on cl.AssignedUserID	= u1.id
	left join vw_curr_cc_user u2						(nolock) on cl.SubroRepresentative_Ext 	= u2.id
	
	left join vw_curr_cc_riskunit ru					(nolock) on cv.RiskUnitID		= ru.id
	left join vw_curr_cc_classcode cls					(nolock) on ru.ClassCodeID		= cls.id
	left join vw_curr_cctl_lobcode lob							on cl.LOBCode			= lob.id
	left join vw_curr_cctl_policytype polt				(nolock) on po.PolicyType		= polt.id
	left join vw_curr_cctl_transaction tt				(nolock) on t.Subtype			= tt.id
	left join vw_curr_cctl_losscause tlc				(nolock) on cl.LossCause		= tlc.id
	left join vw_curr_cctl_transactionstatus ts			(nolock) on t.Status			= ts.id
	left join vw_curr_cctl_costtype CST					(nolock) on T.CostType			= CST.ID
	left join vw_curr_cctl_costcategory ccat			(nolock) on t.CostCategory		= ccat.ID
	left join vw_curr_cctl_linecategory lc				(nolock) on TL.LineCategory		= lc.ID
	left join vw_curr_cctl_transactionlifecyclestate tls (nolock) on T.LifeCycleState	= tls.ID
	left join vw_curr_cctl_recoverycategory rv			 (nolock) on t.RecoveryCategory = rv.ID
	left join vw_curr_cctl_underwritingcompanytype uw	 (nolock) on po.UnderwritingCo  = uw.id
	left join vw_curr_cctl_coveragesubtype st			(nolock) on ex.CoverageSubType	= st.id
	left join vw_curr_cctl_coveragetype ct				(nolock) on cv.type				= ct.id
	left join vw_curr_cctl_checkbatching cb				(nolock) on ck.CheckBatching	= cb.ID
	left join vw_curr_cctl_paymenttype pt				(nolock) on t.PaymentType		= pt.id
	where tls.name = 'committed'
	and tset.ApprovalStatus=1				--Approved  added 08/29/2018 ek
	
	-- 08/07/24  mec
	and tl.Retired = 0						-- If > 0 then transaction was deleted (matches DH)
) x
 
)a	
-- For Incurred  *********************************************************
where TFGTran in ('321', '351', '341', '421', '431')
--and PolSource in ('guidewire') --('legacy')
--and PolSource in ('legacy') 
--and AcctDate_sql < '08/01/2024'
and AcctDate_sql > @PV_STARTDATE and AcctDate_sql < @PV_ENDDATE --'08/01/2024'
--and AcctDate_sql > '12/30/2022' and AcctDate_sql < '12/30/2023'	  -- 2023
and PolSource = 'Guidewire'
 group by 
 PolSource 
  --LOBCode 
 -- ClaimNumber
  ,LOBCode
  ,PolicyNumber
 -- ,LossDate
 -- ,ReportedDate
 having sum(TransAmount) <> 0

 order by 
 PolSource desc 
 --LOBCode 
 --ClaimNumber