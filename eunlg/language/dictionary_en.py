TEMPLATES = {
    # data
    "cphi": ["the", 1, "was for the", "{price, replace=True}", "category", 2],  # cphi(0)_hicp2015(1)_cp-hi00(2)
    "income": ["among", 2, "in the age", "{group, replace=True}", 1, "the", 3, "was in", 4],  # income(0)_total(1)_f(2)_med-e(3)_eur(4)
    "health": ["the", "{average, replace=True}", 1, "was for", 2],  # health(0)_pc-che(1)_hf3(2)
    "env": ["the national expenditure in the category of", 1, "in charasteristics of", 2, "was in", 3],  # env_cepa3_eps-p1_mio-eur

    # general
    "month": "in {} {}",  # month, year
    "year": "in the year {}",  # year
    "year_change": "from {} to {}",  # from year to year
    "month_change": "from {} {} to {} {}",  # from month year to month year
    "place": "in {}",  # area_name
}

CPHI = {
    "hicp2015": "harmonized consumer price index",  # harmonized consumer price index (2015=100)
    "rt1": "growth rate on previous month",  # growth rate on previous period (t/t-1)
    "rt12": "growth rate",  # growth rate (t/t-12)
    "cp-hi00": "all items",
    "cp-hi01": "food and non-alcoholic beverages",
    "cp-hi02": "alcoholic beverages and tobacco",
    "cp-hi03": "clothing and footwear",
    "cp-hi04": "housing, water, electricity, gas and other fuels",
    "cp-hi05": "furnishings, household equipment and maintenance",
    "cp-hi06": "health",
    "cp-hi07": "transport",
    "cp-hi08": "communication",
    "cp-hi09": "recreation and culture",
    "cp-hi10": "education",
    "cp-hi11": "hotels, cafes and restaurants",
    "cp-hi12": "miscellaneous goods and services",
    "cp-hi00xef": "all items excluding energy, food, alcohol and tobacco",
    "cp-hi00xtb": "all items excluding tobacco",
    "cp-hie": "energy",
    "cp-hif": "food",
    "cp-hifu": "unprocessed food",
    "cp-hig": "total goods",
    "cp-hiig": "industrial goods",
    "cp-his": "total services",
    "cp-hiigxe": "non-energy industrial goods",
    "cp-hi00xe": "all items excluding energy",
    "cp-hi00xefu": "all items excluding energy and unprocessed food",
    "cp-hi00xes": "all items excluding energy and seasonal food",
}

INCOME = {
    "f": "females",
    "m": "males",
    "t": "all sexes",
    "eur": "euros",
    "nac": "national currency",
    "pps": "purchasing power standard",
    "med-e": "median equivalised net income",
    "mei-e": "mean equivalised net income",
    "total": "all ages",
    "y-lt6": "less than 6 years",
    "y6-10": "from 6 to 10 years",
    "y6-11": "from 6 to 11 years",
    "y11-15": "from 11 to 15 years",
    "y12-17": "from 12 to 17 years",
    "y-lt16": "less than 16 years",
    "y16-24": "from 16 to 24 years",
    "y16-64": "from 16 to 64 years",
    "y-ge16": "16 years or over",
    "y-lt18": "less than 18 years",
    "y18-24": "from 18 to 24 years",
    "y18-64": "from 18 to 64 years",
    "y-ge18": "18 years or over",
    "y25-49": "from 25 to 49 years",
    "y25-54": "from 25 to 54 years",
    "y50-64": "from 50 to 64 years",
    "y55-64": "from 55 to 64 years",
    "y-lt60": "less than 60 years",
    "y-ge60": "60 years or over",
    "y-lt65": "less than 65 years",
    "y65-74": "from 65 to 74 years",
    "y-ge65": "65 years or over",
    "y-lt75": "less than 75 years",
    "y-ge75": "75 years or over",
}

HEALTH = {
    "hf3": "household out-of-pocket payment",
    "pc-che": "percentual share of total current health expenditure",
}

ENV = {
    "tot_cepa": "total environmental protection activities",
    "cepa1_4-9": "protection of ambient air and climate; protection and remediation of soil, groundwater and surface water; noise and vibration abatement; protection...",
    "cepa1": "protection of ambient air and climate",
    "cepa112_122": "protection of climate and ozone layer",
    "cepa2": "wastewater management",
    "cepa3": "waste management",
    "cepa4": "protection and remediation of soil, groundwater and surface water",
    "cepa5": "noise and vibration abatement (excluding workplace protection)",
    "cepa6": "protection of biodiversity and landscapes",
    "cepa7": "protection against radiation (excluding external safety)",
    "cepa8": "environmental research and development",
    "cepa9": "other environmental protection activities",
    "eps-p1": "output",
    "eps-p11": "market output",
    "eps-p13": "non-market output",
    "eps-p1-anc": "environmental protection related ancillary output",
    "eps-p2-eps-sp": "intermediate consumption of environmental protection services by corporations as specialist producers",
    "p3-eps": "final consumption expenditure of environmental protection services",
    "eps-p51g-np": "gross fixed capital formation and acquisition less disposals of non-produced non-financial assets",
    "p7-eps": "import of environmental protection services",
    "p6-eps": "export of environmental protection services",
    "eps-d21x31": "taxes less subsidies on products",
    "eps-sup-nu": "supply at purchasers' prices available for national uses",
    "ep-d3-7-92-99-p": "current and capital transfers for environmental protection, paid",
    "mio-eur": "million euros",
    "mio-nac": "million units of national currency",
}

DATA = {
    "cphi": CPHI,
    "income": INCOME,
    "health": HEALTH,
    "env": ENV,
}

SMALL_ORDINALS = {
    "1": "first",
    "2": "second",
    "3": "third",
    "4": "fourth",
    "5": "fifth",
    "6": "sixth",
    "7": "seventh",
    "8": "eighth",
    "9": "ninth",
    "10": "tenth",
    "11": "eleventh",
    "12": "twelfth",
    "else": "th",
}

SMALL_CARDINALS = {
    "1": "one",
    "2": "two",
    "3": "three",
    "4": "four",
    "5": "five",
    "6": "six",
    "7": "seven",
    "8": "eight",
    "9": "nine",
    "10": "ten",
}

MONTHS = {
    "01": "January",
    "02": "February",
    "03": "March",
    "04": "April",
    "05": "May",
    "06": "June",
    "07": "July",
    "08": "August",
    "09": "September",
    "10": "October",
    "11": "November",
    "12": "December",
    "reference_options": ["during the month", "also", "at the same time"],
}

YEARS = {
    "reference_options": ["in the same year", "also during the same year", "also"],
}

PLACES = {
    "M": "the municipality",
    "C": "the country",
}

COUNTRIES = {
    "EA": "Euro area (at that point in time)",  # (EA11-2000, EA12-2006, EA13-2007, EA15-2008, EA16-2010, EA17-2013, EA18-2014, EA19)
    "EA19": "Euro area (19 countries)",
    "EA18": "Euro area (18 countries)",
    "EU": "European Union (at that point in time)",  # (EU6-1958, EU9-1973, EU10-1981, EU12-1986, EU15-1995, EU25-2004, EU27-2007, EU28-2013)
    "EU28": "European Union (28 countries)",
    "BE": "Belgium",
    "BG": "Bulgaria",
    "CZ": "Czechia",
    "DK": "Denmark",
    "DE": "Germany",  # (until 1990 former territory of the FRG)
    "EE": "Estonia",
    "IE": "Ireland",
    "EL": "Greece",
    "ES": "Spain",
    "FR": "France",
    "HR": "Croatia",
    "IT": "Italy",
    "CY": "Cyprus",
    "LV": "Latvia",
    "LT": "Lithuania",
    "LU": "Luxembourg",
    "HU": "Hungary",
    "MT": "Malta",
    "NL": "Netherlands",
    "AT": "Austria",
    "PL": "Poland",
    "PT": "Portugal",
    "RO": "Romania",
    "SI": "Slovenia",
    "SK": "Slovakia",
    "FI": "Finland",
    "SE": "Sweden",
    "UK": "the United Kingdom",
    "IS": "Iceland",
    "NO": "Norway",
    "CH": "Switzerland",
    "MK": "North Macedonia",
    "RS": "Serbia",
    "TR": "Turkey",
    "US": "the United States",
}

COMPARISONS = {
    "more": "more than",
    "less": "less than",
    "eu": "EU average",
    "us": "US average",
    "similar": "the average for countries that are considered to be similar",
    "highest": "highest",
    "lowest": "lowest",
    "rank": "compared to other countries",
}
