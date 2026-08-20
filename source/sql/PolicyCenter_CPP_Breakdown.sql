Declare @POLSTARTDATE as Date
Declare @POLENDDATE as Date
Declare @CHANGESTARTDATE as Date
Declare @curmthyr as int = concat(month(GETUTCDATE())-1,year(GETUTCDATE()))

Set @POLSTARTDATE = '8/1/2025'
Set @POLENDDATE = '7/31/2026'
Set @CHANGESTARTDATE = '7/1/2026'

select
ProfitCenter,ProductCode,LineOfBusiness,PolicyNumber,OriginalEffectiveDate,PeriodStart,PeriodEnd,AccountNumber,Company,PrimaryInsuredName,AgentCode,AgentName,FarmUWTerritory
,case
	when MostRecentModel = 1 then TranType
	else Null end as MostRecentTran
,case
	when TranType in ('Renewal','Submission') then Written_Premium
	else null end as SubWritten_Premium
,case 
	when TranType in ('Renewal','Submission') then WrittenDate
	else null end as SubWritten_Date
,case
	when TranType in ('Cancellation') then CancellationDate
	else null end as CancelledDate
,case
	when TranType in ('Cancellation') then JobCloseDate
	else null end as CancelledEffDate
,case
	when TranType in ('Cancellation') then Written_Premium
	else null end as CancelledPremium
,case
	when TranType in ('Reinstatement') then Written_Premium
	else null end as ReinstatedPremium
,case 
	when TranType in ('Reinstatement') then WrittenDate
	else null end as ReinstatedDate
,case 
	when TranType in ('Reinstatement') then JobCloseDate
	else null end as ReinstatedEffDate
,case
	when TranType in ('PolicyChange')  then Written_Premium
	else null end as ChangePremium
,case 
	when TranType in ('PolicyChange') then EditEffectiveDate
	else null end as ChangeDate
from(
SELECT  
		profit.NAME	as ProfitCenter,
	    ProductCode,
		--PatternCode,
		case
			when PatternCode = 'cp7line'					then 'Commercial Property Line'		
			when PatternCode = 'GeneralLiabilityLine_GLE'   then 'General Liability Line'
			when PatternCode = 'ca7line'					then 'Commercial Auto Line'
			when PatternCode = 'cr7line'					then 'Crime Line'
			when PatternCode = 'imline'						then 'Inland Marine Line'
			when PatternCode = 'WC7Line'					then 'Workers Comp Line'
			else PatternCode					
			end as LineofBusiness,
		
		pp.PolicyNumber
	
		,LegacyPolicyNumber
		--,ppstype.NAME				as PolPerSourceType
		,AccountNumber
		,case 
			--when UWCompany = 1 then 'WRM'  
			--when UWCompany = 2 then 'LRM'
			--when UWCompany = 3 then 'SON'
			when uwc.name = 'Lightning Rod Mutual'   then 'LRM'
			when uwc.name = 'Western Reserve Mutual' then 'WRM'
			when uwc.name = 'Sonnenberg Mutual'		 then 'SON'
			else 'UNK'
			end						as Company
		
		,pp.ID			as PolPerID
		--,BranchNumber
		,pp.PeriodID
		,pp.TermNumber
		
		--,AccountNumber
		 --,pp.[PrimaryInsuredName]

		  ,(select distinct PrimaryInsuredName from pc_policyperiod pp2 
					where pp.PolicyNumber = pp2.PolicyNumber
					and pp.PeriodStart  = pp2.PeriodStart
					and pp2.MostRecentModel = 1)  as PrimaryInsuredName
		
		,cast((rtrim(org.Code_Ext))	as char(6))	as AgentCode
		,org.Name								as AgentName
		,farmterr.NAME							as FarmUWTerritory
		
		
		,case 
			when prod.code is null then '999' 
			else right(rtrim(prod.code),3)
		 end						as ProducerCode
		
		--,[JobID]
		,JobNumber
		,j.CloseDate		as JobCloseDate
		
		,jt.TYPECODE				as TranType
		,isnull(bopt.NAME,'')		as BindOpt 
		,jdt.name					as JobDesc
		,ppst.TYPECODE				as PolPerStatus
		
	    ,[MostRecentModel]
		,pp.[CreateTime]
		,[EditEffectiveDate]
		,pol.IssueDate
		,pol.OriginalEffectiveDate
	
		,[PeriodStart]	 
		,[PeriodEnd]	 
		,[CancellationDate]
		
		,[WrittenDate]
		
		,case
			when ProductCode = 'CommercialPackage' then
				case
					when PatternCode = 'cp7line' then
						(select isnull(sum(amount),0.00) FROM pcx_cp7transaction tr 	where tr.BranchID		= pp.id)
							
					when PatternCode = 'GeneralLiabilityLine_GLE' then
						(select isnull(sum(amount),0.00) FROM pcx_gl7transaction_gle tr 	where tr.BranchID	= pp.id)
							
					when PatternCode = 'ca7line' then
						(select isnull(sum(amount),0.00) FROM pcx_ca7transaction tr  where tr.BranchID		= pp.id)
							
					when PatternCode = 'cr7line' then
						(select isnull(sum(amount),0.00) FROM pcx_cr7transaction tr  where tr.BranchID		= pp.id)
							 
					when PatternCode = 'imline' then
						(select isnull(sum(amount),0.00) FROM pc_imtransaction tr where tr.BranchID			= pp.id)

					when PatternCode = 'WC7Line' then
						(select isnull(sum(amount),0.00) FROM pcx_wc7transaction tr where tr.BranchID		= pp.id)
						
					end
			
			else TransactionCostRPT --TotalCostRPT
			end as Written_Premium
		,[TotalPremiumRPT]
		,[TotalCostRPT] 
  FROM [PolicyCenter].[dbo].[pc_policyperiod] pp
  left join [PolicyCenter].[dbo].pc_policy pol					(nolock) on pp.policyid		= pol.id
  left join [PolicyCenter].[dbo].pc_policyTerm polt				(nolock) on pp.policytermid = polt.id
  
  left join [PolicyCenter].[dbo].[pc_policyline] polline		(nolock) on polline.branchid = pp.id
											and coalesce(polline.EffectiveDate, PeriodStart) <> coalesce(polline.ExpirationDate, PeriodEnd)
											--and polline.ExpirationDate is null
  
  left join [PolicyCenter].[dbo].[pc_job] j						(nolock) on pp.jobid		= j.id
  left join [PolicyCenter].[dbo].[pc_account] act				(nolock) on pol.AccountID	= act.id
  --left join [PolicyCenter].[dbo].[pc_user] u					(nolock) on pp.CreateUserID	= u.id
  
  left join pc_producercode prod								(nolock) on pp.ProducerCodeOfRecordID	= prod.id 
  left join pc_organization org									(nolock) on prod.OrganizationID			= org.id


  left join [PolicyCenter].[dbo].[pctl_job] jt					(nolock) on j.SubType		= jt.id
  left join [PolicyCenter].[dbo].pctl_policyperiodstatus ppst	(noLock) ON pp.status		= ppst.ID
  left join [PolicyCenter].[dbo].pctl_bindoption bopt			(nolock) on j.BindOption	= bopt.id
  left join [PolicyCenter].[dbo].pctl_uwcompanycode uwc			(nolock) on pp.UWCompany	= uwc.TYPECODE
   -- for change type
  left join [PolicyCenter].[dbo].pctl_jobdescription_ext jdt	(nolock) on j.DescriptionTL	= jdt.id
  left join pctl_policyperiodsourcetype ppstype							 on ppstype.id		= pp.PolicyPeriodSource
  -- get profit center
   left join pctl_profitcentertype profit                       (nolock) on ProfitCenterType	= profit.id
   -- get FarmUWTerr
   left join pctl_orgfarmuwterritory farmterr					(nolock) on FarmUWTerritory		= farmterr.id
  
  where --j.CloseDate is not null 
  pol.IssueDate is not null 
  and pp.Policynumber is not null
  and (ppst.TYPECODE in ('Bound','AuditComplete')) -- and bopt.NAME <> 'BindOnly') 
  and j.CloseDate < @POLENDDATE
   union all
 SELECT  

		profit.NAME	as ProfitCenter,
	    ProductCode,
		'C.P.P.'   as LineOfBusiness,
		pp.PolicyNumber
		
		,LegacyPolicyNumber
		--,ppstype.NAME				as PolPerSourceType
		,AccountNumber
		,case 
			when uwc.name = 'Lightning Rod Mutual'   then 'LRM'
			when uwc.name = 'Western Reserve Mutual' then 'WRM'
			when uwc.name = 'Sonnenberg Mutual'		 then 'SON'
			else 'UNK'
			end						as Company
		
		,pp.ID			as PolPerID
		,pp.PeriodID
		,pp.TermNumber
		,(select distinct PrimaryInsuredName from pc_policyperiod pp2 
					where pp.PolicyNumber = pp2.PolicyNumber
					  and pp.PeriodStart  = pp2.PeriodStart
					and pp2.MostRecentModel = 1)  as PrimaryInsuredName
		
		,cast((rtrim(org.Code_Ext))	as char(6))	as AgentCode
		,org.Name								as AgentName
		,farmterr.NAME							as FarmUWTerritory
		,case 
			when prod.code is null then '999' 
			else right(rtrim(prod.code),3)
		 end						as ProducerCode
		
		--,[JobID]
		,JobNumber
		,j.CloseDate				as JobCloseDate
		
		,jt.TYPECODE				as TranType
		,isnull(bopt.NAME,'')		as BindOpt 
		,jdt.name					as JobDesc
		,ppst.TYPECODE				as PolPerStatus
				 
		 ,[MostRecentModel]
		,pp.[CreateTime]
		,[EditEffectiveDate]
		,pol.IssueDate
		,pol.OriginalEffectiveDate
		,[PeriodStart]	 
		,[PeriodEnd]	 
		,[CancellationDate]
		,[WrittenDate]
		,TransactionCostRPT  as Written_Premium
		,[TotalPremiumRPT]
		,[TotalCostRPT] 
		
  FROM [PolicyCenter].[dbo].[pc_policyperiod] pp
  left join [PolicyCenter].[dbo].pc_policy pol					(nolock) on pp.policyid		= pol.id
  left join [PolicyCenter].[dbo].pc_policyTerm polt				(nolock) on pp.policytermid = polt.id
 left join [PolicyCenter].[dbo].[pc_job] j						(nolock) on pp.jobid		= j.id
  left join [PolicyCenter].[dbo].[pc_account] act				(nolock) on pol.AccountID	= act.id
  left join pc_producercode prod								(nolock) on pp.ProducerCodeOfRecordID	= prod.id 
  left join pc_organization org									(nolock) on prod.OrganizationID			= org.id
  left join [PolicyCenter].[dbo].[pctl_job] jt					(nolock) on j.SubType		= jt.id
  left join [PolicyCenter].[dbo].pctl_policyperiodstatus ppst	(noLock) ON pp.status		= ppst.ID
  left join [PolicyCenter].[dbo].pctl_bindoption bopt			(nolock) on j.BindOption	= bopt.id
  left join [PolicyCenter].[dbo].pctl_uwcompanycode uwc			(nolock) on pp.UWCompany	= uwc.TYPECODE
   -- for change type
  left join [PolicyCenter].[dbo].pctl_jobdescription_ext jdt	(nolock) on j.DescriptionTL	= jdt.id
  left join pctl_policyperiodsourcetype ppstype							 on ppstype.id		= pp.PolicyPeriodSource
  -- get profit center
   left join pctl_profitcentertype profit                       (nolock) on ProfitCenterType	= profit.id
   -- get FarmUWTerr
   left join pctl_orgfarmuwterritory farmterr					(nolock) on FarmUWTerritory		= farmterr.id
  
  
  where j.CloseDate is not null 
  and pol.IssueDate is not null 
  and pp.Policynumber is not null
  and (ppst.TYPECODE in ('Bound','AuditComplete')) -- and bopt.NAME <> 'BindOnly')   
  and ProductCode = 'CommercialPackage' 
  and j.CloseDate < @POLENDDATE
  )jj
where-- LineOfBusiness = 'Commercial Property Line'
--and cancellationdate is null
((PeriodStart between @POLSTARTDATE and @POLENDDATE) OR JobCloseDate between @POLSTARTDATE and @POLENDDATE)
and ((ProductCode = 'CommercialPackage' AND LineOfBusiness not in ('C.P.P.')))
and ProfitCenter = 'Agribusiness'
order by PolicyNumber