import sys


unit = {
  'HICP2015' :	'Harmonized consumer price index, 2015=100',
	'RT1' :	'Growth rate on previous period (t/t-1)',
	'RT12' :	'Growth rate (t/t-12)',
}


INDICATOR = {
	'CP-HI00' :	'All items (HICP=Harmonized Index of Consumer Prices)',
	'CP-HI01' :	'Food and non alcoholic beverages',
	'CP-HI02' :	'Alcoholic beverages and tobacco',
	'CP-HI03' :	'Clothing and footwear',
	'CP-HI04' :	'Housing, water, electricity,gas and other fuels',
	'CP-HI05' :	'Furnishings, household equipment and maintenance',
	'CP-HI06' :	'Health',
	'CP-HI07' :	'Transport',
	'CP-HI08' :	'Communication',
	'CP-HI09'	: 'Recreation and culture',
	'CP-HI10' :	'Education',
	'CP-HI11' :	'Hotels, cafes and restaurants',
	'CP-HI12' :	'Miscellaneous goods and services',
	'CP-HI00XEF' : 'All items excluding energy, food, alcohol and tobacco',
	'CP-HI00XTB' :	'All items excluding tobacco',
	'CP-HIE' :	'Energy',
	'CP-HIF' :	'Food',
	'CP-HIFU' :	'Unprocessed food',
	'CP-HIG' :	'Total goods',
	'CP-HIIG' :	'Industrial goods',
	'CP-HIS' :	'Total services',
	'CP-HIIGXE' :	'Non-energy industrial goods',
	'CP-HI00XE' :	'All items excluding energy',
	'CP-HI00XEFU' :	'All items excluding energy and unprocessed food',
	'CP-HI00XES' :	'All items excluding energy and seasonal food',
}


def find_with_code(code):
  if code in unit:
    return unit[code]
  elif code in INDICATOR:
    return INDICATOR[code]
  else:
    return 'Code not found'


if __name__ == "__main__":
    code = sys.argv[1]
    print(find_with_code(code))