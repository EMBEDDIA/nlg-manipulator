# what type palojen järjestys määritelty täällä
TEMPLATES = {
    'cphi': [1, 'was', 'for price category', 2], # cphi(0)_hicp2015(1)_cp-hi00(2)
    'income': ['among', 2, 'in age group', 1, 'the', 3, 'was in', 4], # income(0)_total(1)_f(2)_med-e(3)_eur(4)
    'health': ['the', 1, 'was for', 2], # health(0)_pc-che(1)_hf3(2)
    'month': 'in {} {}',
    'year': 'in the year {}',
    'year_change': 'from {} to {}',
    'month_change': 'from {} {} to {} {}',
    'place': 'in {}',
}

CPHI = {
    'hicp2015': 'harmonized consumer price index', # harmonized consumer price index (2015=100)
    'rt1': 'growth rate on previous month', # growth rate on previous period (t/t-1)
    'rt12': 'growth rate', # growth rate (t/t-12)
    'cp-hi00': 'all items',
    'cp-hi01': 'food and non alcoholic beverages',
    'cp-hi02': 'alcoholic beverages and tobacco',
    'cp-hi03': 'clothing and footwear',
    'cp-hi04': 'housing, water, electricity,gas and other fuels',
    'cp-hi05': 'furnishings, household equipment and maintenance',
    'cp-hi06': 'health',
    'cp-hi07': 'transport',
    'cp-hi08': 'communication',
    'cp-hi09': 'recreation and culture',
    'cp-hi10': 'education',
    'cp-hi11': 'hotels, cafes and restaurants',
    'cp-hi12': 'miscellaneous goods and services',
    'cp-hi00xef': 'all items excluding energy, food, alcohol and tobacco',
    'cp-hi00xtb': 'all items excluding tobacco',
    'cp-hie': 'energy',
    'cp-hif': 'food',
    'cp-hifu': 'unprocessed food',
    'cp-hig': 'total goods',
    'cp-hiig': 'industrial goods',
    'cp-his': 'total services',
    'cp-hiigxe': 'non-energy industrial goods',
    'cp-hi00xe': 'all items excluding energy',
    'cp-hi00xefu': 'all items excluding energy and unprocessed food',
    'cp-hi00xes': 'all items excluding energy and seasonal food',
}

INCOME = {
    'f': 'females',
    'm': 'males',
    't': 'all sexes',
    'eur': 'euros',
    'nac': 'national currency',
    'pps': 'purchasing power standard',
    'med-e': 'median equivalised net income',
    'mei-e': 'mean equivalised net income',
    'total': 'all ages',
    'y-lt6': 'less than 6 years',
    'y6-10': 'from 6 to 10 years',
    'y6-11': 'from 6 to 11 years',
    'y11-15': 'from 11 to 15 years',
    'y12-17': 'from 12 to 17 years',
    'y-lT16': 'less than 16 years',
    'y16-24': 'from 16 to 24 years',
    'y16-64': 'from 16 to 64 years',
    'y-ge16': '16 years or over',
    'y-lT18': 'less than 18 years',
    'y18-24': 'from 18 to 24 years',
    'y18-64': 'from 18 to 64 years',
    'y-ge18': '18 years or over',
    'y25-49': 'from 25 to 49 years',
    'y25-54': 'from 25 to 54 years',
    'y50-64': 'from 50 to 64 years',
    'y55-64': 'from 55 to 64 years',
    'y-lt60': 'less than 60 years',
    'y-ge60': '60 years or over',
    'y-lt65': 'less than 65 years',
    'y65-74': 'from 65 to 74 years',
    'y-ge65': '65 years or over',
    'y-lt75': 'less than 75 years',
    'y-ge75': '75 years or over',
}

HEALTH = {
    'hf3': "household out-of-pocket payment",
    'pc-che': "percentual share of total current health expenditure",
}

DATA =  {
    'cphi': CPHI,
    'income': INCOME,
    'health': HEALTH,
}

SMALL_ORDINALS = {
    '1': "first",
    '2': "second",
    '3': "third",
    '4': "fourth",
    '5': "fifth",
    '6': "sixth",
    '7': "seventh",
    '8': "eighth",
    '9': "ninth",
    '10': "tenth",
    '11': "eleventh",
    '12': "twelfth",
    'else': 'th',
}

SMALL_CARDINALS = {
    '1': "one",
    '2': "two",
    '3': "three",
    '4': "four",
    '5': "five",
    '6': "six",
    '7': "seven",
    '8': "eight",
    '9': "nine",
    '10': "ten",
}

MONTHS = {
    '01': "January",
    '02': "February",
    '03': "March",
    '04': "April",
    '05': "May",
    '06': "June",
    '07': "July",
    '08': "August",
    '09': "September",
    '10': "October",
    '11': "November",
    '12': "December",
    'reference_options': ["during the month", "also", "at the same time"],
}

YEARS = {
    'reference_options': ["in the same year", "also during the same year", "also"],
}

PLACES = {
    'M': 'the municipality',
    'C': 'the country',
}

COUNTRIES = {
    'EA': 'Euro area (EA11-2000, EA12-2006, EA13-2007, EA15-2008, EA16-2010, EA17-2013, EA18-2014, EA19)',
	'EA19': 'Euro area (19 countries)',
	'EA18':	'Euro area (18 countries)',
	'EU': 'European Union (EU6-1958, EU9-1973, EU10-1981, EU12-1986, EU15-1995, EU25-2004, EU27-2007, EU28-2013)',
	'EU28':	'European Union - 28 countries',
	'BE': 'Belgium',
	'BG': 'Bulgaria',
	'CZ': 'Czechia',
	'DK': 'Denmark',
	'DE': 'Germany (until 1990 former territory of the FRG)',
	'EE': 'Estonia',
	'IE': 'Ireland',
	'EL': 'Greece',
	'ES': 'Spain',
	'FR': 'France',
	'HR': 'Croatia',
	'IT': 'Italy',
	'CY': 'Cyprus',
	'LV': 'Latvia',
	'LT': 'Lithuania',
	'LU': 'Luxembourg',
	'HU': 'Hungary',
	'MT': 'Malta',
	'NL': 'Netherlands',
	'AT': 'Austria',
	'PL': 'Poland',
	'PT': 'Portugal',
	'RO': 'Romania',
	'SI': 'Slovenia',
	'SK': 'Slovakia',
	'FI': 'Finland',
	'SE': 'Sweden',
	'UK': 'United Kingdom',
	'IS': 'Iceland',
	'NO': 'Norway',
	'CH': 'Switzerland',
	'MK': 'North Macedonia',
	'RS': 'Serbia',
	'TR': 'Turkey',
	'US': 'United States',
}

COMPARISONS = {
    'more': 'more than',
    'less': 'less than',
    'eu': "EU average",
    'us': "US average",
    'similar': "the average for countries that are considered to be similar",
    'highest': 'highest',
    'lowest': 'lowest',
    'rank': 'compared to other countries',
}