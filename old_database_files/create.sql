drop table if exists acs_data;
create table acs_data (
	county text unique, 

	B03002_001E text, -- Hispanic Or Latino Origin By Race Total
	B03002_003E text, -- White Alone
	B03002_004E text, -- Black Or African American Alone
	B03002_012E text, -- Hispanic Or Latino

	B05012_001E text, -- Nativity In The United States
	B05012_003E text, -- Nativity In The United States (Foreign-Born)

	B01003_001E text, -- Total Population

	B05001_001E text, -- Nativity And Citizenship Status In The United States Total
	B05001_006E text, -- Nativity and Citizenship Status In The United States (Non-Citizen)

	B17001_001E text, -- Poverty Status In The Past 12 Months Total
	B17001_002E text, -- Income In The Past 12 Months Below Poverty Level
	B17001A_002E text, -- Poverty Status In The Past 12 Months Total (White Alone)
	B17001A_001E text, -- Income In The Past 12 Months Below Poverty Level (White Alone)
	B17001B_002E text, -- Poverty Status In The Past 12 Months Total (Black Or African American Alone)
	B17001B_001E text, -- Income In The Past 12 Months Below Poverty Level (Black Or African American Alone)
	B17001I_002E text, -- Poverty Status In The Past 12 Months Total (Hispanic Or Latino)
	B17001I_001E text, -- Income In The Past 12 Months Below Poverty Level (Hispanic Or Latino)

	B19013_001E text, -- Median Household Income In The Past 12 Months
	B19013A_001E text, -- Median Household Income In The Past 12 Months (In 2012 Inflation-Adjusted Dollars) (White Alone Householder)
	B19013B_001E text, -- Median Household Income In The Past 12 Months (In 2012 Inflation-Adjusted Dollars) (Black Or African American Alone Householder)
	B19013I_001E text, -- Median Household Income In The Past 12 Months (In 2012 Inflation-Adjusted Dollars) (Hispanic Or Latino Householder)

	B19051_001E text, -- Earnings In The Past 12 Months For Households Total

	B01002_001E text, -- Median Age By Sex Total

	B23025_001E text, -- Employment Status For The Population 16 Years And Over Total
	B23025_005E text, -- Unemployed
	B23025_003E text, -- Civilian Labor Force

	B19083_001E text -- Gini
);

drop table if exists county_zip;
create table county_zip (
	zip text,
	county text,
	population text
);
