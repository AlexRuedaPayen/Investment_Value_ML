assets = [
'totalAssets', 'intangibleAssets', 'earningAssets', 'otherCurrentAssets',
'goodWill', 'otherAssets', 'cash', 'cashAndEquivalents'
][::-1]

liabilities = [
    'totalLiab', 'totalCurrentLiabilities', 'currentDeferredRevenue', 'deferredLongTermLiab', 'otherCurrentLiab',
    'netDebt', 'shortTermDebt'
][::-1]

equity = [
    'totalStockholderEquity', 'commonStock', 'capitalStock', 'retainedEarnings', 'otherLiab'
][::-1]


revenue_and_costs = ['totalRevenue', 'costOfRevenue', 'grossProfit'][::-1]
operating_income_and_expenses = [
    'operatingIncome', 'sellingGeneralAdministrative', 'researchDevelopment',
    'reconciledDepreciation', 'nonOperatingIncomeNetOther', 'ebit', 'ebitda',
    'depreciationAndAmortization', 'otherOperatingExpenses'
][::-1]
interest_and_taxes = ['interestExpense', 'interestIncome', 'taxProvision', 'incomeTaxExpense'][::-1]
net_income_components = [
    'netIncome', 'extraordinaryItems', 'nonRecurring', 'discontinuedOperations',
    'netIncomeFromContinuingOps', 'netIncomeApplicableToCommonShares'
][::-1]
